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


def synchronized_silence(users, user_ids, min_silence_minutes=60,
                         min_overlap_minutes=30, min_participants=None):
    """
    Detect periods when multiple/all users stop communicating simultaneously.

    Investigative Value
    -------------------
    Synchronized silence across multiple suspects may indicate:
    - In-person meeting (no need to call when together)
    - Coordinated operational activity (e.g., crime commission)
    - Deliberate communication blackout
    - Shared external event (arrest, hospitalization)

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
        Each synchronized silence event with:
        - start: datetime when overlap begins
        - end: datetime when overlap ends
        - duration_minutes: float
        - participants: list of user_ids who were silent
        - participant_count: int
        - preceding_activity: dict mapping user_id to their last contact before silence
        - following_activity: dict mapping user_id to their first contact after silence
        - suspicion_score: float 0-1 based on duration and coordination

    Notes
    -----
    Suspicion score factors:
    - Duration: Longer coordinated silences are more suspicious
    - Participant ratio: Higher percentage of participants = more suspicious
    - Time of day: Nighttime silences may be normal (sleeping)
    """
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
                        'direction': prev_rec.direction
                    },
                    'first_after': {
                        'datetime': curr_rec.datetime,
                        'correspondent_id': curr_rec.correspondent_id,
                        'interaction': curr_rec.interaction,
                        'direction': curr_rec.direction
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
                    # Calculate suspicion score
                    participant_ratio = len(current_participants) / len(users)
                    duration_hours = duration_seconds / 3600

                    # Base score from duration (caps at 0.5 for 12+ hours)
                    duration_score = min(0.5, duration_hours / 24)

                    # Coordination score from participant ratio (0-0.4)
                    coordination_score = participant_ratio * 0.4

                    # Time of day factor (0-0.1): daytime silence more suspicious
                    hour = current_overlap_start.hour
                    if 9 <= hour <= 21:  # Daytime
                        time_score = 0.1
                    else:  # Nighttime (could be sleeping)
                        time_score = 0.0

                    suspicion_score = min(1.0, duration_score + coordination_score + time_score)

                    # Build context
                    preceding_activity = {}
                    following_activity = {}
                    for uid, sinfo in current_participants.items():
                        preceding_activity[uid] = sinfo['last_before']
                        following_activity[uid] = sinfo['first_after']

                    synchronized_events.append({
                        'start': current_overlap_start,
                        'end': overlap_end,
                        'duration_minutes': duration_seconds / 60,
                        'participants': list(current_participants.keys()),
                        'participant_count': len(current_participants),
                        'preceding_activity': preceding_activity,
                        'following_activity': following_activity,
                        'suspicion_score': round(suspicion_score, 3)
                    })

                current_overlap_start = None
                current_participants = {}

    # Sort by suspicion score descending
    synchronized_events.sort(key=lambda x: (-x['suspicion_score'], x['start']))

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
        user_id -> {
            'antenna_id': str or None (antenna at/near target time),
            'coordinates': tuple (lat, lon) or None,
            'record_datetime': datetime (closest record found),
            'delta_seconds': float (how far from target time),
            'confidence': str ('high'/'medium'/'low'/None),
            'activity_at_time': str (what were they doing - e.g., "call out"),
            'correspondent': str (who they were communicating with)
        }

    Notes
    -----
    Confidence levels:
    - 'high': Record within 5 minutes of target
    - 'medium': Record within 15 minutes of target
    - 'low': Record within window but > 15 minutes
    - None: No record found within window
    """
    window_seconds = window_minutes * 60
    results = {}

    for user, uid in zip(users, user_ids):
        # Get antenna coordinates lookup
        antennas = user.antennas or {}

        # Find the closest record to target_datetime within window
        best_record = None
        best_delta = float('inf')

        for r in user.records:
            delta = abs((r.datetime - target_datetime).total_seconds())
            if delta <= window_seconds and delta < best_delta:
                best_delta = delta
                best_record = r

        if best_record is None:
            results[uid] = {
                'antenna_id': None,
                'coordinates': None,
                'record_datetime': None,
                'delta_seconds': None,
                'confidence': None,
                'activity_at_time': None,
                'correspondent': None
            }
        else:
            # Determine confidence based on time proximity
            if best_delta <= 300:  # 5 minutes
                confidence = 'high'
            elif best_delta <= 900:  # 15 minutes
                confidence = 'medium'
            else:
                confidence = 'low'

            # Get coordinates if antenna available
            antenna_id = best_record.position.antenna
            coordinates = None
            if antenna_id and antenna_id in antennas:
                ant_data = antennas[antenna_id]
                if hasattr(ant_data, 'latitude') and hasattr(ant_data, 'longitude'):
                    coordinates = (ant_data.latitude, ant_data.longitude)
                elif isinstance(ant_data, (list, tuple)) and len(ant_data) >= 2:
                    coordinates = (ant_data[0], ant_data[1])

            # Build activity description
            activity = f"{best_record.interaction} {best_record.direction}"

            results[uid] = {
                'antenna_id': antenna_id,
                'coordinates': coordinates,
                'record_datetime': best_record.datetime,
                'delta_seconds': best_delta,
                'confidence': confidence,
                'activity_at_time': activity,
                'correspondent': best_record.correspondent_id
            }

    return results
