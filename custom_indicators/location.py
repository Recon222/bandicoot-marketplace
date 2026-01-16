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
        Location info with confidence based on record proximity
    """
    window = timedelta(minutes=window_minutes)
    window_start = target_datetime - window
    window_end = target_datetime + window

    # Find records in window
    window_records = [r for r in user.records
                      if window_start <= r.datetime <= window_end
                      and r.position.antenna is not None]

    if not window_records:
        return None

    # Find closest record to target time
    closest = min(window_records,
                  key=lambda r: abs((r.datetime - target_datetime).total_seconds()))

    coords = None
    if user.antennas and closest.position.antenna in user.antennas:
        coords = user.antennas[closest.position.antenna]

    delta_seconds = abs((closest.datetime - target_datetime).total_seconds())

    return {
        'antenna_id': closest.position.antenna,
        'coordinates': coords,
        'record_datetime': closest.datetime,
        'delta_seconds': delta_seconds,
        'confidence': 'high' if delta_seconds < 300 else 'medium' if delta_seconds < 900 else 'low',
        'interaction': closest.interaction,
        'correspondent_id': closest.correspondent_id
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
