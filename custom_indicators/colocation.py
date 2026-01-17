"""
Co-Location Analysis Indicators (Multi-User)
============================================

Indicators for detecting when multiple subjects were in the same
location at the same time. These are NOT standard Bandicoot @grouping
indicators - they operate on multiple User objects.

Investigative Value
-------------------
- Prove two people were in the same location (critical evidence)
- Detect meetings between subjects
- Identify coordinated movement patterns
"""

from collections import defaultdict
from datetime import timedelta


def antenna_overlap(user_a, user_b, window_minutes=30):
    """
    Find times when two users hit the same antenna within a time window.

    Investigative Value
    -------------------
    Proves two people were in the same location - critical for
    establishing meetings, coordination, or presence at crime scene.

    Parameters
    ----------
    user_a : bandicoot.core.User
        First subject
    user_b : bandicoot.core.User
        Second subject
    window_minutes : int
        Time window for co-location (default 30 minutes)

    Returns
    -------
    list of dict
        Each overlap: {
            'antenna_id': str,
            'user_a_time': datetime,
            'user_b_time': datetime,
            'delta_seconds': float,
            'coordinates': tuple or None
        }
    """
    window_seconds = window_minutes * 60
    overlaps = []

    # Get antenna coordinates for output
    antennas = user_a.antennas or user_b.antennas or {}

    # Build index of user_b records by antenna for efficiency
    b_by_antenna = defaultdict(list)
    for r in user_b.records:
        if r.position.antenna:
            b_by_antenna[r.position.antenna].append(r)

    # Check each user_a record against matching antenna records from user_b
    for rec_a in user_a.records:
        if rec_a.position.antenna is None:
            continue

        antenna = rec_a.position.antenna
        if antenna not in b_by_antenna:
            continue

        for rec_b in b_by_antenna[antenna]:
            delta = abs((rec_a.datetime - rec_b.datetime).total_seconds())
            if delta <= window_seconds:
                overlaps.append({
                    'antenna_id': antenna,
                    'user_a_time': rec_a.datetime,
                    'user_b_time': rec_b.datetime,
                    'delta_seconds': delta,
                    'coordinates': antennas.get(antenna)
                })

    # Sort by time
    overlaps.sort(key=lambda x: x['user_a_time'])
    return overlaps


def travel_pattern_match(user_a, user_b, window_minutes=60, min_sequence_length=2):
    """
    Detect when two subjects traverse the same sequence of antennas.

    Investigative Value
    -------------------
    Indicates following someone or traveling together.

    Parameters
    ----------
    user_a : bandicoot.core.User
    user_b : bandicoot.core.User
    window_minutes : int
        Time window for matching movements
    min_sequence_length : int
        Minimum number of matching transitions to report

    Returns
    -------
    list of dict
        Matching travel sequences
    """
    window_seconds = window_minutes * 60

    # Get ordered antenna sequences for each user
    def get_transitions(user):
        sorted_records = sorted([r for r in user.records if r.position.antenna],
                                key=lambda r: r.datetime)
        transitions = []
        for i in range(1, len(sorted_records)):
            prev = sorted_records[i - 1]
            curr = sorted_records[i]
            if prev.position.antenna != curr.position.antenna:
                transitions.append({
                    'from': prev.position.antenna,
                    'to': curr.position.antenna,
                    'time': curr.datetime
                })
        return transitions

    trans_a = get_transitions(user_a)
    trans_b = get_transitions(user_b)

    if not trans_a or not trans_b:
        return []

    # Find matching transitions within time window
    matches = []
    for ta in trans_a:
        for tb in trans_b:
            if (ta['from'] == tb['from'] and ta['to'] == tb['to']):
                delta = abs((ta['time'] - tb['time']).total_seconds())
                if delta <= window_seconds:
                    matches.append({
                        'from_antenna': ta['from'],
                        'to_antenna': ta['to'],
                        'user_a_time': ta['time'],
                        'user_b_time': tb['time'],
                        'delta_seconds': delta
                    })

    return matches


def meeting_detection(user_a, user_b, colocation_window_minutes=30,
                      gap_threshold_minutes=60):
    """
    Detect co-locations with surrounding activity context.

    Finds times when both users were at the same antenna within a time window,
    and provides the surrounding activity context for each user. Does NOT
    claim these are "meetings" - that is an interpretation for investigators.

    Investigative Value
    -------------------
    Co-location with activity context helps investigators evaluate whether
    users may have met in person. Low surrounding activity may suggest
    in-person interaction (no need to call when together).

    Parameters
    ----------
    user_a : bandicoot.core.User
    user_b : bandicoot.core.User
    colocation_window_minutes : int
        Time window for co-location detection
    gap_threshold_minutes : int
        Window around co-location to count surrounding activity

    Returns
    -------
    list of dict
        Data-first evidence with:
        - type: "colocation_with_context"
        - colocation: antenna_id, coord, user times, delta
        - activity_context: records_around for each user
        - parameters: methodology exposure
    """
    from .utils import serialize_record, normalize_coordinates

    # First find co-locations
    colocations = antenna_overlap(user_a, user_b, colocation_window_minutes)

    if not colocations:
        return []

    gap_seconds = gap_threshold_minutes * 60
    results = []

    # Get antennas dict for coordinates
    antennas = user_a.antennas or user_b.antennas or {}

    for coloc in colocations:
        coloc_time = coloc['user_a_time']

        # Get activity around co-location for user_a
        a_records_around = [r for r in user_a.records
                           if abs((r.datetime - coloc_time).total_seconds()) < gap_seconds]

        # Get activity around co-location for user_b
        b_records_around = [r for r in user_b.records
                           if abs((r.datetime - coloc_time).total_seconds()) < gap_seconds]

        # Normalize coordinates
        coord = normalize_coordinates(coloc['antenna_id'], antennas)

        results.append({
            "type": "colocation_with_context",
            "colocation": {
                "antenna_id": coloc['antenna_id'],
                "coord": coord,
                "user_a_time": coloc['user_a_time'].isoformat(),
                "user_b_time": coloc['user_b_time'].isoformat(),
                "delta_seconds": coloc['delta_seconds']
            },
            "activity_context": {
                "user_a": {
                    "records_around_count": len(a_records_around),
                    "records_around": [serialize_record(r) for r in sorted(a_records_around, key=lambda x: x.datetime)],
                    "gap_window_minutes": gap_threshold_minutes
                },
                "user_b": {
                    "records_around_count": len(b_records_around),
                    "records_around": [serialize_record(r) for r in sorted(b_records_around, key=lambda x: x.datetime)],
                    "gap_window_minutes": gap_threshold_minutes
                }
            },
            "parameters": {
                "colocation_window_minutes": colocation_window_minutes,
                "gap_threshold_minutes": gap_threshold_minutes
            }
        })

    return results


def multi_user_colocation(users, window_minutes=30):
    """
    Find times when 3+ users were at the same antenna.

    Investigative Value
    -------------------
    Group meetings between multiple subjects.

    Parameters
    ----------
    users : list of bandicoot.core.User
        List of users to analyze
    window_minutes : int
        Time window for co-location

    Returns
    -------
    list of dict
        Multi-party co-locations with all participants and times
    """
    window_seconds = window_minutes * 60

    # Build timeline of all antenna hits
    all_hits = []
    for i, user in enumerate(users):
        for r in user.records:
            if r.position.antenna:
                all_hits.append({
                    'user_index': i,
                    'datetime': r.datetime,
                    'antenna': r.position.antenna
                })

    # Sort by time
    all_hits.sort(key=lambda x: x['datetime'])

    # Find clusters at same antenna within window
    colocations = []

    for i, hit in enumerate(all_hits):
        # Find all hits at same antenna within window
        cluster = [hit]
        for j in range(i + 1, len(all_hits)):
            other = all_hits[j]
            delta = (other['datetime'] - hit['datetime']).total_seconds()
            if delta > window_seconds:
                break
            if other['antenna'] == hit['antenna'] and other['user_index'] != hit['user_index']:
                # Check not already in cluster
                if other['user_index'] not in [c['user_index'] for c in cluster]:
                    cluster.append(other)

        # Report if 3+ users
        if len(cluster) >= 3:
            user_indices = sorted(set(c['user_index'] for c in cluster))
            times = [c['datetime'] for c in cluster]
            colocations.append({
                'antenna': hit['antenna'],
                'user_indices': user_indices,
                'participant_count': len(user_indices),
                'earliest_time': min(times),
                'latest_time': max(times),
                'time_span_seconds': (max(times) - min(times)).total_seconds()
            })

    # Deduplicate (same event may be detected multiple times)
    seen = set()
    unique = []
    for c in colocations:
        key = (c['antenna'], tuple(c['user_indices']), c['earliest_time'].isoformat()[:16])
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique


def proximity_to_location(user, target_antenna, target_datetime=None, window_minutes=60):
    """
    Check if user was near a specific location (antenna) around a specific time.

    Investigative Value
    -------------------
    Was the subject near the crime scene around the time of the offence?

    Parameters
    ----------
    user : bandicoot.core.User
    target_antenna : str
        Antenna ID of location of interest
    target_datetime : datetime, optional
        Time of interest (if None, checks all records)
    window_minutes : int
        Time window around target_datetime

    Returns
    -------
    list of dict
        Records showing presence at or near target location
    """
    results = []

    for r in user.records:
        if r.position.antenna is None:
            continue

        # Check if at target antenna
        if r.position.antenna == target_antenna:
            include = True
            if target_datetime:
                delta = abs((r.datetime - target_datetime).total_seconds())
                include = delta <= window_minutes * 60

            if include:
                results.append({
                    'datetime': r.datetime,
                    'antenna_id': r.position.antenna,
                    'at_target': True,
                    'interaction': r.interaction,
                    'correspondent_id': r.correspondent_id
                })

    results.sort(key=lambda x: x['datetime'])
    return results


def synchronized_silence(users, user_ids, min_silence_minutes=60,
                         min_overlap_minutes=30, min_participants=None):
    """
    Detect periods when multiple/all users stop communicating simultaneously.

    Investigative Value
    -------------------
    Synchronized silence across multiple subjects may indicate:
    - In-person meeting (no need to call when together)
    - Coordinated operational activity
    - Deliberate communication blackout
    - Shared external event (arrest, hospitalization)

    Investigators interpret what the silence means - this function only
    provides the raw observables.

    Parameters
    ----------
    users : list of bandicoot.core.User
        List of users to analyze
    user_ids : list of str
        Identifiers for each user (e.g., phone numbers, names)
    min_silence_minutes : int
        Minimum individual silence period to consider (default 60 min)
    min_overlap_minutes : int
        Minimum overlap duration to report (default 30 min)
    min_participants : int or None
        Minimum users that must be silent. None = all users required.
        Use for partial overlap (e.g., 3 of 5 suspects)

    Returns
    -------
    list of dict
        Data-first evidence with:
        - type: "synchronized_silence"
        - users: list of user_ids who were silent
        - silence: start_ts, end_ts, duration_minutes
        - parameters: methodology exposure
        - support: raw observables (participant_count, total_users, start_hour, is_daytime)
        - preceding_events: serialized last event before silence for each user
        - following_events: serialized first event after silence for each user

        Sorted chronologically by start time (not by any subjective score).
    """
    from .utils import serialize_record_dict

    if min_participants is None:
        min_participants = len(users)

    min_participants = max(2, min(min_participants, len(users)))

    min_silence_seconds = min_silence_minutes * 60
    min_overlap_seconds = min_overlap_minutes * 60

    # Step 1: Find silence periods for each user
    user_silences = {}  # user_id -> list of (start, end, last_before, first_after)

    for user, uid in zip(users, user_ids):
        records = sorted(user.records, key=lambda r: r.datetime)
        if len(records) < 2:
            user_silences[uid] = []
            continue

        silences = []
        for i in range(1, len(records)):
            prev_rec = records[i - 1]
            curr_rec = records[i]
            gap_seconds = (curr_rec.datetime - prev_rec.datetime).total_seconds()

            if gap_seconds >= min_silence_seconds:
                silences.append({
                    'start': prev_rec.datetime,
                    'end': curr_rec.datetime,
                    'last_before': {
                        'datetime': prev_rec.datetime,
                        'correspondent_id': prev_rec.correspondent_id,
                        'interaction': prev_rec.interaction,
                        'direction': prev_rec.direction,
                        'call_duration': prev_rec.call_duration,
                        'antenna_id': prev_rec.position.antenna if prev_rec.position else None
                    },
                    'first_after': {
                        'datetime': curr_rec.datetime,
                        'correspondent_id': curr_rec.correspondent_id,
                        'interaction': curr_rec.interaction,
                        'direction': curr_rec.direction,
                        'call_duration': curr_rec.call_duration,
                        'antenna_id': curr_rec.position.antenna if curr_rec.position else None
                    }
                })

        user_silences[uid] = silences

    # Step 2: Find overlapping silence periods across users
    # Collect all silence interval endpoints to find overlap candidates
    all_intervals = []
    for uid, silences in user_silences.items():
        for s in silences:
            all_intervals.append((s['start'], s['end'], uid, s))

    if not all_intervals:
        return []

    # Sort by start time
    all_intervals.sort(key=lambda x: x[0])

    # Use sweep line algorithm to find overlaps
    synchronized_events = []

    # For each possible silence start point, check how many users are silent
    # Get all unique timestamps
    time_points = set()
    for start, end, uid, s in all_intervals:
        time_points.add(start)
        time_points.add(end)

    time_points = sorted(time_points)

    # Track active silences at each point
    def get_active_silences_at_time(t):
        """Get which users are silent at time t."""
        active = {}
        for start, end, uid, silence_info in all_intervals:
            # User is silent if t is strictly between their last activity and next
            if start < t < end:
                active[uid] = silence_info
        return active

    # Find intervals where enough participants are silent
    current_overlap_start = None
    current_participants = {}

    for i, t in enumerate(time_points):
        active = get_active_silences_at_time(t)

        if len(active) >= min_participants:
            if current_overlap_start is None:
                current_overlap_start = t
                current_participants = active.copy()
            else:
                # Update participants (may change during overlap)
                current_participants.update(active)
        else:
            if current_overlap_start is not None:
                # End of overlap period
                overlap_end = t
                duration_seconds = (overlap_end - current_overlap_start).total_seconds()

                if duration_seconds >= min_overlap_seconds:
                    # Build context with serialized events
                    preceding_events = {}
                    following_events = {}
                    for uid, sinfo in current_participants.items():
                        preceding_events[uid] = serialize_record_dict(sinfo['last_before'])
                        following_events[uid] = serialize_record_dict(sinfo['first_after'])

                    # Raw observables for support
                    start_hour = current_overlap_start.hour

                    synchronized_events.append({
                        "type": "synchronized_silence",
                        "users": list(current_participants.keys()),
                        "silence": {
                            "start_ts": current_overlap_start.isoformat(),
                            "end_ts": overlap_end.isoformat(),
                            "duration_minutes": duration_seconds / 60
                        },
                        "parameters": {
                            "min_silence_minutes": min_silence_minutes,
                            "min_overlap_minutes": min_overlap_minutes,
                            "min_participants": min_participants
                        },
                        "support": {
                            "participant_count": len(current_participants),
                            "total_users": len(users),
                            "participant_ratio": len(current_participants) / len(users),
                            "start_hour": start_hour,
                            "is_daytime": 9 <= start_hour <= 21
                        },
                        "preceding_events": preceding_events,
                        "following_events": following_events
                    })

                current_overlap_start = None
                current_participants = {}

    # Sort chronologically by start time (not by any subjective score)
    synchronized_events.sort(key=lambda x: x['silence']['start_ts'])

    return synchronized_events


def group_locations_at_time(users, user_ids, target_datetime, window_minutes=30):
    """
    Determine location of all users at a specific time.

    Investigative Value
    -------------------
    "Where was everyone at the time of the crime?"
    - Alibi verification
    - Crime scene presence
    - Witness location identification
    - Coordination detection (multiple suspects at same location)

    Parameters
    ----------
    users : list of bandicoot.core.User
        List of users to analyze
    user_ids : list of str
        Identifiers for each user
    target_datetime : datetime
        The specific time of interest
    window_minutes : int
        Search window around target time (default 30 min)
        Records within this window of target_datetime are considered

    Returns
    -------
    dict
        Data-first evidence structure with:
        - type: "group_locations_at_time"
        - target_ts: ISO timestamp of target time
        - window_minutes: search window size
        - users: dict of user_id -> {support, location, closest_event, events_in_window}
        - colocation_summary: groups users by antenna for quick co-location detection
    """
    from .utils import serialize_record, normalize_coordinates

    window_seconds = window_minutes * 60
    user_results = {}

    for user, uid in zip(users, user_ids):
        # Get antenna coordinates lookup
        antennas = user.antennas or {}

        # Find all records in window
        all_window_records = [r for r in user.records
                              if abs((r.datetime - target_datetime).total_seconds()) <= window_seconds]

        # Find closest record to target_datetime
        best_record = None
        best_delta = float('inf')

        for r in all_window_records:
            delta = abs((r.datetime - target_datetime).total_seconds())
            if delta < best_delta:
                best_delta = delta
                best_record = r

        if best_record is None:
            user_results[uid] = {
                "support": {
                    "closest_event_delta_sec": None,
                    "events_in_window": 0,
                    "has_location": False
                },
                "location": {
                    "antenna_id": None,
                    "coord": None
                },
                "closest_event": None,
                "events_in_window": []
            }
        else:
            # Get antenna and coordinates
            antenna_id = best_record.position.antenna
            coord = normalize_coordinates(antenna_id, antennas) if antenna_id else None

            user_results[uid] = {
                "support": {
                    "closest_event_delta_sec": best_delta,
                    "events_in_window": len(all_window_records),
                    "has_location": antenna_id is not None
                },
                "location": {
                    "antenna_id": antenna_id,
                    "coord": coord
                },
                "closest_event": {
                    "ts": best_record.datetime.isoformat(),
                    "interaction": best_record.interaction,
                    "direction": best_record.direction,
                    "correspondent_id": best_record.correspondent_id,
                    "duration_sec": best_record.call_duration,
                    "antenna_id": antenna_id
                },
                "events_in_window": [serialize_record(r) for r in sorted(all_window_records, key=lambda x: x.datetime)]
            }

    # Build colocation summary - group users by antenna
    by_antenna = defaultdict(list)
    for uid, data in user_results.items():
        antenna_id = data["location"]["antenna_id"]
        if antenna_id:
            by_antenna[antenna_id].append(uid)

    return {
        "type": "group_locations_at_time",
        "target_ts": target_datetime.isoformat(),
        "window_minutes": window_minutes,
        "users": user_results,
        "colocation_summary": {
            "by_antenna": dict(by_antenna)
        }
    }
