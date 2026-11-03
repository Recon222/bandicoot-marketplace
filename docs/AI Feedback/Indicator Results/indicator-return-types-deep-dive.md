# Indicator Return Types Deep Dive

> A detailed technical reference explaining exactly how each custom investigation indicator returns its results

---

## Overview

This document provides a comprehensive breakdown of the return types and data structures for all 47 custom investigation indicators. Each indicator is examined with:
- **Return type** - The Python type returned
- **Structure** - The exact shape of the data
- **Field definitions** - What each field means
- **Example output** - Realistic example data

---

## Table of Contents

1. [Relationship Indicators](#relationship-indicators)
2. [Temporal Indicators](#temporal-indicators)
3. [Location Indicators](#location-indicators)
4. [Co-Location Indicators](#co-location-indicators)
5. [Network Indicators](#network-indicators)
6. [Utility Functions](#utility-functions)

---

## Relationship Indicators

### `relationship_strength(user)`

**Return Type:** `dict[str, float]`

Returns a dictionary mapping each correspondent ID (phone number) to a composite strength score between 0 and 1. The dictionary is **pre-sorted** in descending order by score.

**How the score is calculated:**
1. **Frequency score** = (contact's interaction count) / (max interaction count across all contacts)
2. **Duration score** = (contact's total call duration) / (max call duration across all contacts)
3. **Final score** = (0.6 × frequency_score) + (0.4 × duration_score)

**Example Output:**
```python
{
    '416-555-1234': 0.95,    # Highest - most communication + longest calls
    '416-555-5678': 0.72,
    '416-555-9012': 0.45,
    '416-555-3456': 0.23     # Lowest
}
```

**Empty case:** Returns `{}` if user has no records.

---

### `reciprocity_score(user)`

**Return Type:** `dict[str, float | None]`

Returns a dictionary mapping correspondent IDs to their reciprocity score (0.0 to 1.0).

**How it's calculated:**
- Formula: `min(incoming, outgoing) / max(incoming, outgoing)`
- A score of **1.0** means perfectly balanced two-way communication
- A score of **0.0** means completely one-sided (all in OR all out)
- **None** is returned if both incoming and outgoing counts are zero (shouldn't happen in practice)

**Example Output:**
```python
{
    '416-555-1234': 0.85,    # Very balanced - both parties initiate
    '416-555-5678': 0.33,    # Unbalanced - subject contacts them 3x more
    '416-555-9012': 0.0      # Completely one-sided
}
```

---

### `initiation_ratio(user)`

**Return Type:** `dict[str, float | None]`

Returns a dictionary mapping correspondent IDs to the ratio of subject-initiated contact.

**How it's calculated:**
- Formula: `outgoing_count / total_count`
- **1.0** means the subject always initiates (all outgoing)
- **0.0** means the subject never initiates (all incoming)
- **0.5** means evenly split

**Example Output:**
```python
{
    '416-555-1234': 0.75,    # Subject initiates 75% of contact
    '416-555-5678': 0.20,    # Subject rarely initiates - mostly receiving
    '416-555-9012': 1.0      # Subject always initiates (possible pursuit)
}
```

---

### `first_contact_of_day(user)`

**Return Type:** `dict[str, int]`

Returns a dictionary mapping correspondent IDs to the **count of days** they were the first contact.

**How it works:**
1. Groups all records by calendar date
2. For each day, finds the earliest record (by time)
3. Counts how many days each contact appears as the first contact

**Example Output:**
```python
{
    '416-555-1234': 45,      # First contact on 45 different days (likely partner)
    '416-555-5678': 12,      # First contact on 12 days
    '416-555-9012': 3        # Occasionally first
}
```

---

### `last_contact_of_day(user)`

**Return Type:** `dict[str, int]`

Same structure as `first_contact_of_day` but tracks the **last** contact each day.

**Example Output:**
```python
{
    '416-555-1234': 52,      # Last contact on 52 days (very close relationship)
    '416-555-5678': 8
}
```

---

### `contact_interaction_summary(user)`

**Return Type:** `dict[str, dict]`

Returns a comprehensive summary dictionary for each contact with nested statistics.

**Structure:**
```python
{
    'correspondent_id': {
        'total': int,              # Total interactions
        'calls_in': int,           # Incoming calls
        'calls_out': int,          # Outgoing calls
        'texts_in': int,           # Incoming texts
        'texts_out': int,          # Outgoing texts
        'total_call_duration': int,  # Seconds
        'first_contact': datetime,   # First interaction timestamp
        'last_contact': datetime     # Last interaction timestamp
    }
}
```

**Example Output:**
```python
{
    '416-555-1234': {
        'total': 347,
        'calls_in': 45,
        'calls_out': 62,
        'texts_in': 120,
        'texts_out': 120,
        'total_call_duration': 18450,  # ~5 hours total
        'first_contact': datetime(2024, 1, 15, 8, 30, 0),
        'last_contact': datetime(2024, 6, 20, 23, 15, 0)
    }
}
```

---

## Temporal Indicators

### `hourly_activity_profile(records)`

**Return Type:** `dict[int, int]`

**Note:** This function uses the `@grouping` decorator, meaning it takes `records` not `user`.

Returns a dictionary with exactly 24 keys (0-23) representing hours, mapped to interaction counts.

**Example Output:**
```python
{
    0: 2, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1,
    6: 8, 7: 15, 8: 25, 9: 32, 10: 28, 11: 22,
    12: 35, 13: 30, 14: 27, 15: 25, 16: 22, 17: 38,
    18: 42, 19: 35, 20: 28, 21: 18, 22: 12, 23: 5
}
```

**Empty case:** Returns `{0: 0, 1: 0, ..., 23: 0}` (all zeros).

---

### `communication_gaps(user, threshold_hours=24)`

**Return Type:** `list[dict]`

Returns a list of gap dictionaries, each representing a period of silence exceeding the threshold.

**Structure per gap:**
```python
{
    'start': datetime,       # Last activity before gap
    'end': datetime,         # First activity after gap
    'duration_hours': float  # Gap length in hours
}
```

**Example Output:**
```python
[
    {
        'start': datetime(2024, 6, 14, 23, 45, 0),
        'end': datetime(2024, 6, 17, 8, 30, 0),
        'duration_hours': 56.75  # ~2.5 days of silence
    },
    {
        'start': datetime(2024, 6, 20, 18, 0, 0),
        'end': datetime(2024, 6, 22, 14, 15, 0),
        'duration_hours': 44.25
    }
]
```

**Empty case:** Returns `[]` if fewer than 2 records or no gaps exceed threshold.

---

### `activity_bursts(user, window_minutes=30, threshold_multiplier=3)`

**Return Type:** `list[dict]`

Returns a list of burst events where activity exceeded 3x the average rate.

**Structure per burst:**
```python
{
    'start': datetime,       # When burst started
    'end': datetime,         # Window end (start + window_minutes)
    'count': int,            # Number of interactions in window
    'contacts': list[str]    # Unique correspondent IDs contacted during burst
}
```

**How bursts are detected:**
1. Calculate average rate: `total_records / (total_time_span / window_minutes)`
2. Threshold = average_rate × threshold_multiplier
3. Slide through records; if count in window ≥ threshold, it's a burst

**Example Output:**
```python
[
    {
        'start': datetime(2024, 6, 15, 14, 30, 0),
        'end': datetime(2024, 6, 15, 15, 0, 0),
        'count': 18,  # 18 interactions in 30 minutes
        'contacts': ['416-555-1234', '416-555-5678', '416-555-9012']
    }
]
```

---

### `contact_first_appearance(user)`

**Return Type:** `dict[str, datetime]`

Returns a dictionary mapping each correspondent ID to the datetime of their **first ever** interaction.

**Example Output:**
```python
{
    '416-555-1234': datetime(2024, 1, 15, 8, 30, 0),   # Known since January
    '416-555-5678': datetime(2024, 6, 10, 14, 22, 0),  # New contact in June
    '416-555-9012': datetime(2024, 6, 14, 9, 0, 0)     # Very recent
}
```

---

### `contact_last_appearance(user)`

**Return Type:** `dict[str, datetime]`

Returns a dictionary mapping each correspondent ID to the datetime of their **last** interaction.

**Example Output:**
```python
{
    '416-555-1234': datetime(2024, 6, 20, 23, 15, 0),  # Still active
    '416-555-5678': datetime(2024, 3, 5, 16, 45, 0),   # Stopped in March
    '416-555-9012': datetime(2024, 6, 14, 9, 0, 0)     # Only one contact
}
```

---

### `daily_activity_counts(user)`

**Return Type:** `dict[date, int]`

Returns a dictionary mapping each calendar date to the count of interactions that day.

**Example Output:**
```python
{
    date(2024, 6, 14): 45,
    date(2024, 6, 15): 78,  # Unusually high
    date(2024, 6, 16): 12,  # Unusually low
    date(2024, 6, 17): 38
}
```

---

### `inter_event_times(records)`

**Return Type:** `bandicoot.helper.maths.SummaryStats`

**Note:** Uses `@grouping` decorator, takes `records`.

Returns a `SummaryStats` named tuple containing statistical measures of the time (in seconds) between consecutive interactions.

**SummaryStats fields:**
```python
SummaryStats(
    mean=float,    # Average inter-event time
    std=float,     # Standard deviation
    min=float,     # Shortest gap
    max=float,     # Longest gap
    median=float   # Median gap
)
```

**Example Output:**
```python
SummaryStats(
    mean=2847.5,     # Average ~47 minutes between events
    std=5420.3,      # High variability
    min=15.0,        # Shortest: 15 seconds
    max=86400.0,     # Longest: 24 hours
    median=1200.0    # Median: 20 minutes
)
```

**Empty case:** Returns `SummaryStats` with all None values if fewer than 2 records.

---

### `activity_around_time(user, target_datetime, hours_before=24, hours_after=24)`

**Return Type:** `dict`

Returns a comprehensive breakdown of activity around a specific point in time.

**Structure:**
```python
{
    'before': list[Record],           # Raw Record objects before target
    'after': list[Record],            # Raw Record objects after target
    'contacts_before': Counter,       # correspondent_id -> count before
    'contacts_after': Counter,        # correspondent_id -> count after
    'count_before': int,              # Total interactions before
    'count_after': int                # Total interactions after
}
```

**Example Output:**
```python
{
    'before': [<Record>, <Record>, ...],  # 12 records
    'after': [<Record>, <Record>, ...],   # 5 records (activity dropped)
    'contacts_before': Counter({'416-555-1234': 5, '416-555-5678': 4, ...}),
    'contacts_after': Counter({'416-555-9012': 3, '416-555-1234': 2}),
    'count_before': 12,
    'count_after': 5
}
```

---

### `first_contact_after_time(user, target_datetime)`

**Return Type:** `dict | None`

Returns details about the first communication after a specified time.

**Structure:**
```python
{
    'correspondent_id': str,   # Who they contacted
    'datetime': datetime,      # When
    'interaction': str,        # 'call' or 'text'
    'direction': str,          # 'in' or 'out'
    'delay_seconds': float     # Seconds from target_datetime to contact
}
```

**Example Output:**
```python
{
    'correspondent_id': '416-555-1234',
    'datetime': datetime(2024, 6, 15, 15, 2, 30),
    'interaction': 'call',
    'direction': 'out',
    'delay_seconds': 150.0  # 2.5 minutes after incident
}
```

**Empty case:** Returns `None` if no records exist after target time.

---

## Location Indicators

### `location_timeline(user)`

**Return Type:** `list[dict]`

Returns a chronologically sorted list of all location records with full context.

**Structure per entry:**
```python
{
    'datetime': datetime,
    'antenna_id': str,
    'coordinates': tuple[float, float] | None,  # (lat, lon)
    'interaction': str,                          # 'call' or 'text'
    'correspondent_id': str
}
```

**Example Output:**
```python
[
    {
        'datetime': datetime(2024, 6, 15, 8, 30, 0),
        'antenna_id': 'ANT_001',
        'coordinates': (43.6532, -79.3832),
        'interaction': 'call',
        'correspondent_id': '416-555-1234'
    },
    {
        'datetime': datetime(2024, 6, 15, 9, 15, 0),
        'antenna_id': 'ANT_042',
        'coordinates': (43.6612, -79.3950),
        'interaction': 'text',
        'correspondent_id': '416-555-5678'
    }
]
```

**Note:** Records without antenna data are excluded from the timeline.

---

### `frequent_locations_ranked(user, top_n=10)`

**Return Type:** `list[dict]`

Returns the top N locations sorted by visit frequency.

**Structure per location:**
```python
{
    'antenna_id': str,
    'coordinates': tuple[float, float] | None,
    'count': int,           # Number of records at this antenna
    'percentage': float     # Fraction of total records (0-1)
}
```

**Example Output:**
```python
[
    {
        'antenna_id': 'ANT_001',
        'coordinates': (43.6532, -79.3832),
        'count': 245,
        'percentage': 0.42  # 42% of all records - likely home
    },
    {
        'antenna_id': 'ANT_015',
        'coordinates': (43.6451, -79.3801),
        'count': 156,
        'percentage': 0.27  # 27% - likely work
    }
]
```

---

### `unusual_locations(positions, user, threshold_visits=2)`

**Return Type:** `list[dict]`

**Note:** Uses `@spatial_grouping(user_kwd=True)` decorator.

Returns locations visited fewer than the threshold number of times.

**Structure per location:**
```python
{
    'antenna_id': str,
    'coordinates': tuple[float, float] | None,
    'visit_count': int,
    'timestamps': list[datetime]  # Sorted chronologically
}
```

**Example Output:**
```python
[
    {
        'antenna_id': 'ANT_099',
        'coordinates': (43.7842, -79.1856),  # Unfamiliar area
        'visit_count': 1,
        'timestamps': [datetime(2024, 6, 14, 22, 30, 0)]  # Single visit
    },
    {
        'antenna_id': 'ANT_077',
        'coordinates': (43.7123, -79.4521),
        'visit_count': 2,
        'timestamps': [
            datetime(2024, 6, 10, 14, 0, 0),
            datetime(2024, 6, 14, 14, 30, 0)
        ]
    }
]
```

---

### `location_transitions(user)`

**Return Type:** `list[dict]`

Returns all movements between different antennas.

**Structure per transition:**
```python
{
    'from_antenna': str,
    'to_antenna': str,
    'from_time': datetime,
    'to_time': datetime,
    'duration_minutes': float,
    'distance_km': float | None  # None if coordinates unavailable
}
```

**Example Output:**
```python
[
    {
        'from_antenna': 'ANT_001',
        'to_antenna': 'ANT_015',
        'from_time': datetime(2024, 6, 15, 8, 30, 0),
        'to_time': datetime(2024, 6, 15, 9, 15, 0),
        'duration_minutes': 45.0,
        'distance_km': 3.2
    }
]
```

---

### `time_at_locations(user)`

**Return Type:** `dict[str, float]`

Returns estimated hours spent at each location. **Heuristic:** Each record represents ~30 minutes of presence.

**Example Output:**
```python
{
    'ANT_001': 122.5,   # ~122 hours (records * 0.5)
    'ANT_015': 78.0,
    'ANT_042': 12.5
}
```

---

### `location_at_specific_time(user, target_datetime, window_minutes=30)`

**Return Type:** `dict | None`

Returns the subject's location at a specific time with confidence assessment.

**Structure:**
```python
{
    'antenna_id': str,
    'coordinates': tuple[float, float] | None,
    'record_datetime': datetime,     # Actual record time
    'delta_seconds': float,          # Difference from target
    'confidence': str,               # 'high', 'medium', or 'low'
    'interaction': str,
    'correspondent_id': str
}
```

**Confidence levels:**
- **high**: Record within 5 minutes (300 seconds) of target
- **medium**: Record within 15 minutes (900 seconds)
- **low**: Record within window but > 15 minutes

**Example Output:**
```python
{
    'antenna_id': 'ANT_042',
    'coordinates': (43.6612, -79.3950),
    'record_datetime': datetime(2024, 6, 15, 14, 28, 30),
    'delta_seconds': 90.0,
    'confidence': 'high',
    'interaction': 'call',
    'correspondent_id': '416-555-1234'
}
```

**Empty case:** Returns `None` if no records within window.

---

### `locations_in_time_range(user, start_datetime, end_datetime)`

**Return Type:** `list[dict]`

Returns all location records within a specified time range. Same structure as `location_timeline` entries.

---

## Co-Location Indicators

### `antenna_overlap(user_a, user_b, window_minutes=30)`

**Return Type:** `list[dict]`

Returns instances where two users hit the same antenna within the time window.

**Structure per overlap:**
```python
{
    'antenna_id': str,
    'user_a_time': datetime,
    'user_b_time': datetime,
    'delta_seconds': float,      # Time difference between records
    'coordinates': tuple | None
}
```

**Example Output:**
```python
[
    {
        'antenna_id': 'ANT_042',
        'user_a_time': datetime(2024, 6, 15, 14, 30, 0),
        'user_b_time': datetime(2024, 6, 15, 14, 35, 0),
        'delta_seconds': 300.0,  # 5 minutes apart
        'coordinates': (43.6612, -79.3950)
    }
]
```

**Sorted by:** `user_a_time` ascending.

---

### `travel_pattern_match(user_a, user_b, window_minutes=60, min_sequence_length=2)`

**Return Type:** `list[dict]`

Returns matching transitions where both users moved between the same antennas.

**Structure per match:**
```python
{
    'from_antenna': str,
    'to_antenna': str,
    'user_a_time': datetime,
    'user_b_time': datetime,
    'delta_seconds': float
}
```

**Example Output:**
```python
[
    {
        'from_antenna': 'ANT_001',
        'to_antenna': 'ANT_042',
        'user_a_time': datetime(2024, 6, 15, 9, 15, 0),
        'user_b_time': datetime(2024, 6, 15, 9, 45, 0),
        'delta_seconds': 1800.0  # User B followed 30 min later
    }
]
```

---

### `meeting_detection(user_a, user_b, colocation_window_minutes=30, gap_threshold_minutes=60)`

**Return Type:** `list[dict]`

Returns probable in-person meetings based on co-location + communication gaps.

**Structure per meeting:**
```python
{
    'antenna_id': str,
    'time': datetime,
    'coordinates': tuple | None,
    'delta_seconds': float,      # Co-location time delta
    'activity_around': int,      # Number of records around meeting time
    'confidence': str            # 'high', 'medium', or 'low'
}
```

**Confidence calculation:**
- **high**: < 3 records around meeting time (low activity = likely meeting)
- **medium**: 3-5 records
- **low**: 6+ records (high activity suggests not meeting in person)

---

### `multi_user_colocation(users, window_minutes=30)`

**Return Type:** `list[dict]`

Returns events where 3+ users were at the same antenna simultaneously.

**Structure per event:**
```python
{
    'antenna': str,
    'user_indices': list[int],    # Indices into the users list
    'participant_count': int,
    'earliest_time': datetime,
    'latest_time': datetime,
    'time_span_seconds': float
}
```

**Example Output:**
```python
[
    {
        'antenna': 'ANT_042',
        'user_indices': [0, 1, 3],  # Users 0, 1, and 3 were together
        'participant_count': 3,
        'earliest_time': datetime(2024, 6, 15, 14, 30, 0),
        'latest_time': datetime(2024, 6, 15, 14, 45, 0),
        'time_span_seconds': 900.0
    }
]
```

**Note:** Results are deduplicated to avoid reporting the same event multiple times.

---

### `proximity_to_location(user, target_antenna, target_datetime=None, window_minutes=60)`

**Return Type:** `list[dict]`

Returns records showing presence at a specific antenna (e.g., crime scene).

**Structure per record:**
```python
{
    'datetime': datetime,
    'antenna_id': str,
    'at_target': bool,         # Always True (filtered to target)
    'interaction': str,
    'correspondent_id': str
}
```

---

### `synchronized_silence(users, user_ids, min_silence_minutes=60, min_overlap_minutes=30, min_participants=None)`

**Return Type:** `list[dict]`

Returns periods when multiple users stopped communicating simultaneously. **Sorted by suspicion score descending.**

**Structure per event:**
```python
{
    'start': datetime,
    'end': datetime,
    'duration_minutes': float,
    'participants': list[str],        # User IDs who were silent
    'participant_count': int,
    'preceding_activity': dict,       # user_id -> last contact info
    'following_activity': dict,       # user_id -> first contact after
    'suspicion_score': float          # 0-1 score
}
```

**Preceding/following activity structure:**
```python
{
    'user_id': {
        'datetime': datetime,
        'correspondent_id': str,
        'interaction': str,
        'direction': str
    }
}
```

**Suspicion score calculation:**
- **Duration factor (0-0.5):** `min(0.5, duration_hours / 24)`
- **Coordination factor (0-0.4):** `participant_ratio × 0.4`
- **Time-of-day factor (0-0.1):** 0.1 for daytime (9am-9pm), 0.0 for nighttime

**Example Output:**
```python
[
    {
        'start': datetime(2024, 6, 15, 14, 30, 0),
        'end': datetime(2024, 6, 15, 17, 45, 0),
        'duration_minutes': 195.0,
        'participants': ['416-555-1234', '416-555-5678', '416-555-9012'],
        'participant_count': 3,
        'preceding_activity': {
            '416-555-1234': {'datetime': ..., 'correspondent_id': '416-555-0000', ...},
            '416-555-5678': {'datetime': ..., ...},
            '416-555-9012': {'datetime': ..., ...}
        },
        'following_activity': {...},
        'suspicion_score': 0.723
    }
]
```

---

### `group_locations_at_time(users, user_ids, target_datetime, window_minutes=30)`

**Return Type:** `dict[str, dict]`

Returns where each user was at a specific moment.

**Structure:**
```python
{
    'user_id': {
        'antenna_id': str | None,
        'coordinates': tuple | None,
        'record_datetime': datetime | None,
        'delta_seconds': float | None,
        'confidence': str | None,        # 'high', 'medium', 'low', or None
        'activity_at_time': str | None,  # e.g., "call out"
        'correspondent': str | None
    }
}
```

**Example Output:**
```python
{
    '416-555-1234': {
        'antenna_id': 'ANT_042',
        'coordinates': (43.6612, -79.3950),
        'record_datetime': datetime(2024, 6, 15, 14, 32, 0),
        'delta_seconds': 120.0,
        'confidence': 'high',
        'activity_at_time': 'call out',
        'correspondent': '416-555-9999'
    },
    '416-555-5678': {
        'antenna_id': 'ANT_042',  # Same location! Co-location detected
        'coordinates': (43.6612, -79.3950),
        'record_datetime': datetime(2024, 6, 15, 14, 35, 0),
        'delta_seconds': 300.0,
        'confidence': 'high',
        'activity_at_time': 'text in',
        'correspondent': '416-555-0000'
    },
    '416-555-9012': {
        'antenna_id': None,        # No data within window
        'coordinates': None,
        'record_datetime': None,
        'delta_seconds': None,
        'confidence': None,
        'activity_at_time': None,
        'correspondent': None
    }
}
```

---

## Network Indicators

### `build_communication_matrix(users, user_ids)`

**Return Type:** `dict[tuple[str, str], int]`

Returns a directed graph represented as edge weights.

**Structure:** `{(from_id, to_id): communication_count}`

**Example Output:**
```python
{
    ('416-555-1234', '416-555-5678'): 45,  # 1234 contacted 5678 45 times
    ('416-555-5678', '416-555-1234'): 32,  # 5678 contacted 1234 32 times
    ('416-555-1234', '416-555-9012'): 18
}
```

---

### `degree_centrality(users, user_ids)`

**Return Type:** `dict[str, dict]`

Returns contact counts for each user, **sorted by total contacts descending**.

**Structure:**
```python
{
    'user_id': {
        'total_contacts': int,
        'in_network_contacts': int,      # Contacts who are also subjects
        'out_of_network_contacts': int,  # External contacts
        'in_network_list': list[str],
        'out_of_network_list': list[str]
    }
}
```

---

### `communication_chains(users, user_ids, time_window_minutes=30)`

**Return Type:** `list[dict]`

Returns A→B→C communication patterns.

**Structure per chain:**
```python
{
    'sequence': list[str],           # [A, B, C]
    'times': list[datetime],         # [AB_time, BC_time]
    'total_time_seconds': float,     # Time from A→B to B→C
    'a_to_b': dict,                  # Full communication record
    'b_to_c': dict
}
```

---

### `shared_contacts(users, user_ids, min_shared=2)`

**Return Type:** `dict[str, list[str]]`

Returns external contacts shared by multiple subjects. **Sorted by sharing count descending.**

**Structure:** `{contact_id: [list of user_ids who know this contact]}`

**Example Output:**
```python
{
    '416-555-0000': ['416-555-1234', '416-555-5678', '416-555-9012'],  # 3 subjects
    '416-555-1111': ['416-555-1234', '416-555-5678']  # 2 subjects
}
```

---

### `communication_volume_matrix(users, user_ids)`

**Return Type:** `dict[tuple[str, str], dict]`

Returns symmetric (undirected) communication volume. **Sorted by total descending.**

**Structure:**
```python
{
    (user_a, user_b): {  # Tuple is sorted alphabetically
        'total': int,
        'calls': int,
        'texts': int,
        'duration': int  # Total call seconds
    }
}
```

---

### `network_timeline(users, user_ids, time_bucket_hours=24)`

**Return Type:** `list[dict]`

Returns time-bucketed network activity.

**Structure per bucket:**
```python
{
    'start': datetime,
    'end': datetime,
    'active_pairs': list[tuple[str, str]],  # Which pairs communicated
    'unique_pair_count': int,
    'total_communications': int
}
```

---

### `identify_bridges(users, user_ids)`

**Return Type:** `list[dict]`

Returns users who have exclusive in-network contacts. **Sorted by exclusive count descending.**

**Structure:**
```python
{
    'user_id': str,
    'exclusive_contacts': list[str],   # Contacts only this user knows
    'exclusive_count': int,
    'total_contacts': int
}
```

---

## Utility Functions

### `load_id_mapping(mapping_path)` → `dict[str, str]`
Maps phone numbers to human-readable names.

### `resolve_contact(phone_number, mapping)` → `str`
Returns name if found, else original number.

### `resolve_contacts(results, mapping)` → `dict | list`
Bulk-replaces phone numbers with names in results.

### `records_in_window(user, start_datetime, end_datetime)` → `list[Record]`
Returns raw Bandicoot Record objects.

### `records_around_time(user, target_datetime, window_minutes=30)` → `list[Record]`
Symmetric window around target time.

### `contacts_in_window(user, start_datetime, end_datetime)` → `dict[str, int]`
Returns `{correspondent_id: count}`.

### `location_at_time(user, target_datetime, window_minutes=30)` → `dict | None`
Simplified location lookup (same structure as `location_at_specific_time` but fewer fields).

### `filter_by_contact(records, correspondent_id)` → `list[Record]`
### `filter_by_direction(records, direction)` → `list[Record]`
### `filter_by_interaction(records, interaction)` → `list[Record]`
Standard filter operations returning Record objects.

### `parse_datetime(datetime_str, fmt)` → `datetime`
String to datetime conversion.

### `format_duration(seconds)` → `str`
Returns human-readable strings like `"2h 30m 15s"`.

---

## Quick Reference: Return Type Summary

| Indicator | Returns | Sorted? |
|-----------|---------|---------|
| relationship_strength | `dict[str, float]` | Yes (desc by score) |
| reciprocity_score | `dict[str, float\|None]` | No |
| initiation_ratio | `dict[str, float\|None]` | No |
| first_contact_of_day | `dict[str, int]` | No |
| last_contact_of_day | `dict[str, int]` | No |
| contact_interaction_summary | `dict[str, dict]` | No |
| hourly_activity_profile | `dict[int, int]` | By hour (0-23) |
| communication_gaps | `list[dict]` | By time |
| activity_bursts | `list[dict]` | By time |
| contact_first_appearance | `dict[str, datetime]` | No |
| contact_last_appearance | `dict[str, datetime]` | No |
| daily_activity_counts | `dict[date, int]` | No |
| inter_event_times | `SummaryStats` | N/A |
| activity_around_time | `dict` | N/A |
| first_contact_after_time | `dict\|None` | N/A |
| location_timeline | `list[dict]` | Yes (chronological) |
| frequent_locations_ranked | `list[dict]` | Yes (desc by count) |
| unusual_locations | `list[dict]` | No |
| location_transitions | `list[dict]` | Yes (chronological) |
| time_at_locations | `dict[str, float]` | No |
| location_at_specific_time | `dict\|None` | N/A |
| locations_in_time_range | `list[dict]` | Yes (chronological) |
| antenna_overlap | `list[dict]` | Yes (by user_a_time) |
| travel_pattern_match | `list[dict]` | No |
| meeting_detection | `list[dict]` | No |
| multi_user_colocation | `list[dict]` | No (deduplicated) |
| proximity_to_location | `list[dict]` | Yes (chronological) |
| synchronized_silence | `list[dict]` | Yes (desc by suspicion) |
| group_locations_at_time | `dict[str, dict]` | No |
| build_communication_matrix | `dict[tuple, int]` | No |
| degree_centrality | `dict[str, dict]` | Yes (desc by contacts) |
| communication_chains | `list[dict]` | By time |
| shared_contacts | `dict[str, list]` | Yes (desc by sharing) |
| communication_volume_matrix | `dict[tuple, dict]` | Yes (desc by total) |
| network_timeline | `list[dict]` | Yes (chronological) |
| identify_bridges | `list[dict]` | Yes (desc by exclusive) |

---

*Documentation generated January 2026*
