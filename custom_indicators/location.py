"""
Location Analysis Indicators (Single-User)
==========================================

Indicators for analyzing individual movement patterns,
frequent locations, and spatial behavior.

Investigative Value
-------------------
- Identify home, work, and other significant locations
- Reconstruct movement for alibi verification
- Detect unusual location visits around key dates
"""

from bandicoot.helper.group import spatial_grouping
from bandicoot.helper.maths import summary_stats, great_circle_distance
from collections import Counter, defaultdict
from datetime import timedelta


def location_timeline(user):
    """
    Chronological list of locations with timestamps.

    Investigative Value
    -------------------
    Reconstruct movement for alibi verification and proximity analysis.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    list of dict
        Each entry: {'datetime': dt, 'antenna_id': id, 'coordinates': (lat, lon)}
    """
    timeline = []

    for r in sorted(user.records, key=lambda r: r.datetime):
        if r.position.antenna is None:
            continue

        coords = None
        if user.antennas and r.position.antenna in user.antennas:
            coords = user.antennas[r.position.antenna]

        timeline.append({
            'datetime': r.datetime,
            'antenna_id': r.position.antenna,
            'coordinates': coords,
            'interaction': r.interaction,
            'correspondent_id': r.correspondent_id
        })

    return timeline


def frequent_locations_ranked(user, top_n=10):
    """
    Rank locations by visit frequency.

    Investigative Value
    -------------------
    Identify home, work, and other significant locations.

    Parameters
    ----------
    user : bandicoot.core.User
    top_n : int
        Number of top locations to return

    Returns
    -------
    list of dict
        Each entry: {'antenna_id': id, 'coordinates': (lat, lon),
                     'count': int, 'percentage': float}
    """
    records = [r for r in user.records if r.position.antenna]
    if not records:
        return []

    location_counts = Counter(r.position.antenna for r in records)
    total = sum(location_counts.values())

    results = []
    for antenna_id, count in location_counts.most_common(top_n):
        coords = None
        if user.antennas and antenna_id in user.antennas:
            coords = user.antennas[antenna_id]

        results.append({
            'antenna_id': antenna_id,
            'coordinates': coords,
            'count': count,
            'percentage': count / total if total > 0 else 0
        })

    return results


@spatial_grouping(user_kwd=True)
def unusual_locations(positions, user, threshold_visits=2):
    """
    Locations visited fewer than threshold times.

    Investigative Value
    -------------------
    One-time or rare visits to unusual locations around key dates
    may be significant.

    Parameters
    ----------
    threshold_visits : int
        Maximum visits to be considered "unusual"

    Returns
    -------
    list of dict
        Unusual locations with visit details
    """
    # Group positions by antenna and track timestamps
    location_visits = defaultdict(list)

    for r in user.records:
        if r.position.antenna:
            location_visits[r.position.antenna].append(r.datetime)

    unusual = []
    for antenna_id, timestamps in location_visits.items():
        if len(timestamps) <= threshold_visits:
            coords = None
            if user.antennas and antenna_id in user.antennas:
                coords = user.antennas[antenna_id]

            unusual.append({
                'antenna_id': antenna_id,
                'coordinates': coords,
                'visit_count': len(timestamps),
                'timestamps': sorted(timestamps)
            })

    return unusual


def location_transitions(user):
    """
    Detect movement between different antennas.

    Investigative Value
    -------------------
    Identify travel patterns and movement between locations.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    list of dict
        Each transition: {'from': antenna, 'to': antenna,
                          'from_time': dt, 'to_time': dt, 'distance_km': float}
    """
    transitions = []

    sorted_records = sorted([r for r in user.records if r.position.antenna],
                            key=lambda r: r.datetime)

    for i in range(1, len(sorted_records)):
        prev = sorted_records[i - 1]
        curr = sorted_records[i]

        # Different antenna?
        if prev.position.antenna != curr.position.antenna:
            # Calculate distance if coordinates available
            distance = None
            if user.antennas:
                prev_coords = user.antennas.get(prev.position.antenna)
                curr_coords = user.antennas.get(curr.position.antenna)
                if prev_coords and curr_coords:
                    distance = great_circle_distance(prev_coords, curr_coords)

            transitions.append({
                'from_antenna': prev.position.antenna,
                'to_antenna': curr.position.antenna,
                'from_time': prev.datetime,
                'to_time': curr.datetime,
                'duration_minutes': (curr.datetime - prev.datetime).total_seconds() / 60,
                'distance_km': distance
            })

    return transitions


def time_at_locations(user):
    """
    Estimate time spent at each location based on record counts.

    Investigative Value
    -------------------
    Quantify how much time was spent at each location.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        antenna_id -> estimated_hours (rough estimate: each record ~30 min)
    """
    records = [r for r in user.records if r.position.antenna]
    if not records:
        return {}

    # Simple estimation: count records at each location
    # Rough estimate: each record represents ~30 min window
    location_counts = Counter(r.position.antenna for r in records)

    return {str(antenna): count * 0.5 for antenna, count in location_counts.items()}


def location_at_specific_time(user, target_datetime, window_minutes=30):
    """
    Determine location at a specific datetime.

    NOT a @spatial_grouping indicator - specific query.

    Investigative Value
    -------------------
    Where was the subject at the time of the offence? Alibi verification.

    Parameters
    ----------
    user : bandicoot.core.User
    target_datetime : datetime
    window_minutes : int
        Search window around target time

    Returns
    -------
    dict or None
        Data-first location evidence with:
        - type: "location_at_time"
        - user_id: user identifier
        - window: search parameters
        - support: objective strength metrics (no confidence labels)
        - location: antenna_id and normalized coordinates
        - closest_event: serialized event data
        - events_in_window: all events found in window
        - coverage: data availability metrics
    """
    from .utils import serialize_record, normalize_coordinates

    window = timedelta(minutes=window_minutes)
    window_start = target_datetime - window
    window_end = target_datetime + window

    # Find all records in window (with or without antenna)
    all_window_records = [r for r in user.records
                          if window_start <= r.datetime <= window_end]

    # Find records with antenna data
    window_records = [r for r in all_window_records
                      if r.position.antenna is not None]

    if not window_records:
        # No location data but may have records
        if all_window_records:
            return {
                "type": "location_at_time",
                "user_id": getattr(user, 'name', None),
                "window": {
                    "center_ts": target_datetime.isoformat(),
                    "before_min": window_minutes,
                    "after_min": window_minutes
                },
                "support": {
                    "closest_event_delta_sec": None,
                    "events_in_window": len(all_window_records),
                    "has_location": False,
                    "location_event_delta_sec": None
                },
                "location": {
                    "antenna_id": None,
                    "coord": None
                },
                "closest_event": None,
                "events_in_window": [serialize_record(r) for r in sorted(all_window_records, key=lambda x: x.datetime)],
                "coverage": {
                    "total_events_in_window": len(all_window_records),
                    "events_with_antenna": 0,
                    "missing_antenna_events": len(all_window_records)
                }
            }
        return None

    # Find closest record with location to target time
    closest = min(window_records,
                  key=lambda r: abs((r.datetime - target_datetime).total_seconds()))

    delta_seconds = abs((closest.datetime - target_datetime).total_seconds())

    # Normalize coordinates
    coord = normalize_coordinates(closest.position.antenna, user.antennas)

    # Count antenna coverage
    events_with_antenna = len(window_records)
    missing_antenna_events = len(all_window_records) - events_with_antenna

    return {
        "type": "location_at_time",
        "user_id": getattr(user, 'name', None),
        "window": {
            "center_ts": target_datetime.isoformat(),
            "before_min": window_minutes,
            "after_min": window_minutes
        },
        "support": {
            "closest_event_delta_sec": delta_seconds,
            "events_in_window": len(all_window_records),
            "has_location": True,
            "location_event_delta_sec": delta_seconds
        },
        "location": {
            "antenna_id": closest.position.antenna,
            "coord": coord
        },
        "closest_event": {
            "ts": closest.datetime.isoformat(),
            "interaction": closest.interaction,
            "direction": closest.direction,
            "correspondent_id": closest.correspondent_id,
            "duration_sec": closest.call_duration,
            "antenna_id": closest.position.antenna
        },
        "events_in_window": [serialize_record(r) for r in sorted(all_window_records, key=lambda x: x.datetime)],
        "coverage": {
            "total_events_in_window": len(all_window_records),
            "events_with_antenna": events_with_antenna,
            "missing_antenna_events": missing_antenna_events
        }
    }


def locations_in_time_range(user, start_datetime, end_datetime):
    """
    Get all locations visited in a time range.

    NOT a @spatial_grouping indicator - specific query.

    Investigative Value
    -------------------
    Where was the subject during a specific time period?

    Returns
    -------
    list of dict
        All location records in the time range
    """
    records = [r for r in user.records
               if start_datetime <= r.datetime <= end_datetime
               and r.position.antenna is not None]

    results = []
    for r in sorted(records, key=lambda r: r.datetime):
        coords = None
        if user.antennas and r.position.antenna in user.antennas:
            coords = user.antennas[r.position.antenna]

        results.append({
            'datetime': r.datetime,
            'antenna_id': r.position.antenna,
            'coordinates': coords,
            'interaction': r.interaction,
            'correspondent_id': r.correspondent_id
        })

    return results
