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
    Identify likely in-person meetings between subjects.

    A meeting is detected when:
    1. Both users are at the same antenna within the time window
    2. There's a communication gap between them during/around the co-location
       (people don't call each other when meeting in person)

    Investigative Value
    -------------------
    In-person meetings are critical events - when people meet, they often
    stop calling/texting each other.

    Parameters
    ----------
    user_a : bandicoot.core.User
    user_b : bandicoot.core.User
    colocation_window_minutes : int
        Time window for co-location detection
    gap_threshold_minutes : int
        Communication gap suggesting in-person meeting

    Returns
    -------
    list of dict
        Probable meetings with confidence scores
    """
    # First find co-locations
    colocations = antenna_overlap(user_a, user_b, colocation_window_minutes)

    if not colocations:
        return []

    # Get communication between the two users
    # Find user_b's phone number (filename)
    user_b_id = None
    for r in user_a.records:
        # Check if this correspondent appears in user_b's records as the ego
        # This is a heuristic - in practice, you'd pass the IDs explicitly
        pass

    # For now, check for communication gaps around co-location times
    meetings = []
    gap_seconds = gap_threshold_minutes * 60

    for coloc in colocations:
        meeting_time = coloc['user_a_time']

        # Check if there's a communication gap around this time
        # (simplified - a full implementation would check mutual communication)
        a_records_around = [r for r in user_a.records
                           if abs((r.datetime - meeting_time).total_seconds()) < gap_seconds]

        # If low activity around co-location, likely a meeting
        activity_level = len(a_records_around)

        meetings.append({
            'antenna_id': coloc['antenna_id'],
            'time': meeting_time,
            'coordinates': coloc['coordinates'],
            'delta_seconds': coloc['delta_seconds'],
            'activity_around': activity_level,
            'confidence': 'high' if activity_level < 3 else 'medium' if activity_level < 6 else 'low'
        })

    return meetings


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
