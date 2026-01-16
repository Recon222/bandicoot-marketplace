# Failing Custom Indicators

**Test Date:** 2026-01-16
**Test Data:** `416-225-5506` (150 records), `416-367-8573` (166 records)
**Total Failing:** 15 indicators

---

## Root Cause Analysis

All 15 failing indicators share the same root cause:

**The `@grouping` and `@spatial_grouping` decorators from Bandicoot's `bandicoot.helper.group` module expect indicators to return:**
- A number (int or float)
- A `SummaryStats` object
- `None`
- A list of numbers or `SummaryStats` objects

**The failing indicators return:**
- Dictionaries with string keys (e.g., correspondent_id -> value)
- Lists of dictionaries (e.g., list of gap/burst records)

The Bandicoot statistics pipeline (specifically the `infer_type()` function in `group.py` lines 212-242) validates return values and throws a `TypeError` when it encounters non-numeric values.

---

## Recommended Solution Pattern

These indicators need a different approach. There are two options:

### Option 1: Remove @grouping decorator (Recommended)

Convert to standalone functions that operate directly on `user.records`:

```python
# Before (fails)
@grouping
def relationship_strength(records):
    # ... returns dict
    return {correspondent_id: score, ...}

# After (works)
def relationship_strength(user):
    """
    Rank contacts by communication intensity.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> strength_score
    """
    records = user.records
    if len(records) == 0:
        return {}
    # ... same logic ...
    return {correspondent_id: score, ...}
```

### Option 2: Return numeric/SummaryStats values

If you want to keep the `@grouping` decorator for its filtering and aggregation benefits, modify the return type:

```python
@grouping
def relationship_strength_count(records):
    """Returns count of unique contacts (numeric)."""
    contacts = set(r.correspondent_id for r in records)
    return len(contacts)

@grouping
def relationship_strength_entropy(records):
    """Returns entropy of contact distribution (numeric)."""
    from bandicoot.helper.maths import entropy
    counts = Counter(r.correspondent_id for r in records)
    return entropy(list(counts.values()))
```

---

## Failing Indicators Detail

### relationship.relationship_strength

**Error:**
```
TypeError: 416-367-8573 is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
The function returns a dictionary mapping correspondent_id (string) to strength_score (float). The decorator cannot process string keys.

**Suggested Fix:**
```python
# Remove decorator and accept user object directly
def relationship_strength(user):
    """
    Rank contacts by communication intensity.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> strength_score, sorted by score descending
    """
    records = user.records
    if len(records) == 0:
        return {}

    contact_stats = defaultdict(lambda: {'count': 0, 'duration': 0, 'last': None})

    for r in records:
        cid = r.correspondent_id
        contact_stats[cid]['count'] += 1
        if r.call_duration:
            contact_stats[cid]['duration'] += r.call_duration
        if contact_stats[cid]['last'] is None or r.datetime > contact_stats[cid]['last']:
            contact_stats[cid]['last'] = r.datetime

    # Normalize and compute composite score
    max_count = max(s['count'] for s in contact_stats.values())
    max_duration = max(s['duration'] for s in contact_stats.values()) or 1

    scores = {}
    for cid, stats in contact_stats.items():
        freq_score = stats['count'] / max_count
        dur_score = stats['duration'] / max_duration
        scores[cid] = (0.6 * freq_score) + (0.4 * dur_score)

    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
```

---

### relationship.reciprocity_score

**Error:**
```
TypeError: 416-367-8573 is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns dictionary mapping correspondent_id to reciprocity score.

**Suggested Fix:**
```python
def reciprocity_score(user):
    """
    Measure balance of in/out communication per contact.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> reciprocity score (0.0 to 1.0)
    """
    records = user.records
    if len(records) == 0:
        return {}

    contact_dirs = defaultdict(lambda: {'in': 0, 'out': 0})

    for r in records:
        contact_dirs[r.correspondent_id][r.direction] += 1

    scores = {}
    for cid, dirs in contact_dirs.items():
        in_count = dirs['in']
        out_count = dirs['out']
        if in_count == 0 and out_count == 0:
            scores[cid] = None
        elif in_count == 0 or out_count == 0:
            scores[cid] = 0.0
        else:
            scores[cid] = min(in_count, out_count) / max(in_count, out_count)

    return scores
```

---

### relationship.initiation_ratio

**Error:**
```
TypeError: 416-367-8573 is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns dictionary mapping correspondent_id to initiation ratio.

**Suggested Fix:**
```python
def initiation_ratio(user):
    """
    Track who initiates contact in each relationship.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> ratio of subject-initiated interactions (0.0 to 1.0)
    """
    records = user.records
    if len(records) == 0:
        return {}

    contact_counts = defaultdict(lambda: {'initiated': 0, 'total': 0})

    for r in records:
        contact_counts[r.correspondent_id]['total'] += 1
        if r.direction == 'out':
            contact_counts[r.correspondent_id]['initiated'] += 1

    return {
        cid: counts['initiated'] / counts['total'] if counts['total'] > 0 else None
        for cid, counts in contact_counts.items()
    }
```

---

### relationship.first_contact_of_day

**Error:**
```
TypeError: 416-367-8573 is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns dictionary mapping correspondent_id to count of days they were first contact. Also uses `user_kwd=True` which needs the user parameter.

**Suggested Fix:**
```python
def first_contact_of_day(user):
    """
    Identify who the subject contacts first each day.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> count of days they were first contact
    """
    records = user.records
    if len(records) == 0:
        return {}

    # Group records by date
    by_date = defaultdict(list)
    for r in records:
        by_date[r.datetime.date()].append(r)

    first_contacts = []
    for date, day_records in by_date.items():
        sorted_records = sorted(day_records, key=lambda r: r.datetime)
        if sorted_records:
            first_contacts.append(sorted_records[0].correspondent_id)

    return dict(Counter(first_contacts))
```

---

### relationship.last_contact_of_day

**Error:**
```
TypeError: 416-367-8573 is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Same pattern as first_contact_of_day.

**Suggested Fix:**
```python
def last_contact_of_day(user):
    """
    Identify who the subject contacts last each day.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> count of days they were last contact
    """
    records = user.records
    if len(records) == 0:
        return {}

    by_date = defaultdict(list)
    for r in records:
        by_date[r.datetime.date()].append(r)

    last_contacts = []
    for date, day_records in by_date.items():
        sorted_records = sorted(day_records, key=lambda r: r.datetime)
        if sorted_records:
            last_contacts.append(sorted_records[-1].correspondent_id)

    return dict(Counter(last_contacts))
```

---

### relationship.contact_interaction_summary

**Error:**
```
TypeError: 416-367-8573 is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns a complex dictionary with nested data per contact.

**Suggested Fix:**
```python
def contact_interaction_summary(user):
    """
    Detailed summary of interactions with each contact.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> {
            'total': int,
            'calls_in': int, 'calls_out': int,
            'texts_in': int, 'texts_out': int,
            'total_call_duration': int,
            'first_contact': datetime,
            'last_contact': datetime
        }
    """
    records = user.records
    if len(records) == 0:
        return {}

    summaries = defaultdict(lambda: {
        'total': 0,
        'calls_in': 0, 'calls_out': 0,
        'texts_in': 0, 'texts_out': 0,
        'total_call_duration': 0,
        'first_contact': None,
        'last_contact': None
    })

    for r in records:
        s = summaries[r.correspondent_id]
        s['total'] += 1
        key = f"{r.interaction}s_{r.direction}"
        s[key] += 1
        if r.call_duration:
            s['total_call_duration'] += r.call_duration
        if s['first_contact'] is None or r.datetime < s['first_contact']:
            s['first_contact'] = r.datetime
        if s['last_contact'] is None or r.datetime > s['last_contact']:
            s['last_contact'] = r.datetime

    return dict(summaries)
```

---

### temporal.communication_gaps

**Error:**
```
TypeError: {'start': datetime.datetime(2012, 1, 2, 0, 25, 27), 'end': datetime.datetime(2012, 1, 3, 1, 44, 40), 'duration_hours': 25.32027777777778} is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns a list of dictionaries, each representing a communication gap with start, end, and duration.

**Suggested Fix:**
```python
def communication_gaps(user, threshold_hours=24):
    """
    Detect unusual periods of silence.

    Parameters
    ----------
    user : bandicoot.core.User
    threshold_hours : int
        Minimum gap duration to report (default 24 hours)

    Returns
    -------
    list of dict
        Each gap: {'start': datetime, 'end': datetime, 'duration_hours': float}
    """
    from bandicoot.helper.tools import pairwise

    records = user.records
    if len(records) < 2:
        return []

    sorted_records = sorted(records, key=lambda r: r.datetime)
    threshold_seconds = threshold_hours * 3600
    gaps = []

    for prev, curr in pairwise(sorted_records):
        delta = (curr.datetime - prev.datetime).total_seconds()
        if delta >= threshold_seconds:
            gaps.append({
                'start': prev.datetime,
                'end': curr.datetime,
                'duration_hours': delta / 3600
            })

    return gaps
```

---

### temporal.activity_bursts

**Error:**
```
TypeError: {'start': datetime.datetime(2012, 1, 2, 0, 25, 27), 'end': datetime.datetime(2012, 1, 2, 0, 55, 27), 'count': 1, 'contacts': ['416-367-8573']} is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns a list of dictionaries representing activity bursts.

**Suggested Fix:**
```python
def activity_bursts(user, window_minutes=30, threshold_multiplier=3):
    """
    Identify periods of unusually high activity.

    Parameters
    ----------
    user : bandicoot.core.User
    window_minutes : int
        Size of sliding window (default 30 minutes)
    threshold_multiplier : float
        Activity must exceed average by this factor (default 3x)

    Returns
    -------
    list of dict
        Each burst: {'start': datetime, 'end': datetime, 'count': int, 'contacts': list}
    """
    records = user.records
    if len(records) < 2:
        return []

    sorted_records = sorted(records, key=lambda r: r.datetime)

    total_seconds = (sorted_records[-1].datetime - sorted_records[0].datetime).total_seconds()
    if total_seconds == 0:
        return []

    avg_rate = len(records) / (total_seconds / (window_minutes * 60))
    threshold = avg_rate * threshold_multiplier

    window_delta = timedelta(minutes=window_minutes)
    bursts = []
    i = 0

    while i < len(sorted_records):
        window_start = sorted_records[i].datetime
        window_end = window_start + window_delta

        window_records = [r for r in sorted_records[i:] if r.datetime < window_end]
        count = len(window_records)

        if count >= threshold:
            bursts.append({
                'start': window_start,
                'end': window_end,
                'count': count,
                'contacts': list(set(r.correspondent_id for r in window_records))
            })
            i += count
        else:
            i += 1

    return bursts
```

---

### temporal.contact_first_appearance

**Error:**
```
TypeError: 416-367-8573 is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns dictionary mapping correspondent_id to first contact datetime.

**Suggested Fix:**
```python
def contact_first_appearance(user):
    """
    Identify when each contact first appears in the record.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> first_contact_datetime
    """
    records = user.records
    if len(records) == 0:
        return {}

    first_seen = {}
    for r in sorted(records, key=lambda r: r.datetime):
        if r.correspondent_id not in first_seen:
            first_seen[r.correspondent_id] = r.datetime

    return first_seen
```

---

### temporal.contact_last_appearance

**Error:**
```
TypeError: 416-367-8573 is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns dictionary mapping correspondent_id to last contact datetime.

**Suggested Fix:**
```python
def contact_last_appearance(user):
    """
    Identify when each contact last appears in the record.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> last_contact_datetime
    """
    records = user.records
    if len(records) == 0:
        return {}

    last_seen = {}
    for r in records:
        if r.correspondent_id not in last_seen or r.datetime > last_seen[r.correspondent_id]:
            last_seen[r.correspondent_id] = r.datetime

    return last_seen
```

---

### temporal.daily_activity_counts

**Error:**
```
TypeError: 2012-01-02 is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns dictionary mapping date objects to counts. Date keys are not supported.

**Suggested Fix:**
```python
def daily_activity_counts(user):
    """
    Count of interactions per day.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        date -> count
    """
    records = user.records
    if len(records) == 0:
        return {}

    return dict(Counter(r.datetime.date() for r in records))
```

---

### location.location_timeline

**Error:**
```
TypeError: {'datetime': datetime.datetime(2012, 1, 2, 0, 25, 27), 'antenna_id': '703', 'coordinates': (44.103724, -79.593519), 'interaction': 'call', 'correspondent_id': '416-367-8573'} is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns list of dictionaries representing location timeline entries. Uses `@spatial_grouping` decorator.

**Suggested Fix:**
```python
def location_timeline(user):
    """
    Chronological list of locations with timestamps.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    list of dict
        Each entry: {'datetime': dt, 'antenna_id': id, 'coordinates': (lat, lon),
                     'interaction': str, 'correspondent_id': str}
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
```

---

### location.frequent_locations_ranked

**Error:**
```
TypeError: {'antenna_id': '706', 'coordinates': (43.661278, -79.337933), 'count': 22, 'percentage': 0.17054263565891473} is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns list of dictionaries with location rankings.

**Suggested Fix:**
```python
def frequent_locations_ranked(user, top_n=10):
    """
    Rank locations by visit frequency.

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
```

---

### location.location_transitions

**Error:**
```
TypeError: {'from_antenna': '703', 'to_antenna': '706', 'from_time': datetime.datetime(2012, 1, 2, 0, 25, 27), 'to_time': datetime.datetime(2012, 1, 2, 7, 12, 24), 'duration_minutes': 406.95, 'distance_km': 53.29168842095634} is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns list of dictionaries representing location transitions.

**Suggested Fix:**
```python
def location_transitions(user):
    """
    Detect movement between different antennas.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    list of dict
        Each transition: {'from_antenna': str, 'to_antenna': str,
                          'from_time': dt, 'to_time': dt,
                          'duration_minutes': float, 'distance_km': float}
    """
    from bandicoot.helper.maths import great_circle_distance

    transitions = []
    sorted_records = sorted([r for r in user.records if r.position.antenna],
                            key=lambda r: r.datetime)

    for i in range(1, len(sorted_records)):
        prev = sorted_records[i - 1]
        curr = sorted_records[i]

        if prev.position.antenna != curr.position.antenna:
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
```

---

### location.time_at_locations

**Error:**
```
TypeError: 703 is not a valid input. It should be a number, a SummaryStats object, or None
```

**Analysis:**
Returns dictionary mapping antenna_id (string) to estimated hours. The string keys cause the failure.

**Suggested Fix:**
```python
def time_at_locations(user):
    """
    Estimate time spent at each location based on record proximity.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        antenna_id -> estimated_hours
    """
    records = [r for r in user.records if r.position.antenna]
    if not records:
        return {}

    # Simple estimation: count records at each location
    # More sophisticated: use inter-record times
    location_counts = Counter(r.position.antenna for r in records)

    # Rough estimate: each record represents ~30 min window
    return {str(antenna): count * 0.5 for antenna, count in location_counts.items()}
```

---

## Summary Table

| Module | Indicator | Return Type | Fix Required |
|--------|-----------|-------------|--------------|
| relationship | relationship_strength | dict[str, float] | Remove @grouping |
| relationship | reciprocity_score | dict[str, float] | Remove @grouping |
| relationship | initiation_ratio | dict[str, float] | Remove @grouping |
| relationship | first_contact_of_day | dict[str, int] | Remove @grouping |
| relationship | last_contact_of_day | dict[str, int] | Remove @grouping |
| relationship | contact_interaction_summary | dict[str, dict] | Remove @grouping |
| temporal | communication_gaps | list[dict] | Remove @grouping |
| temporal | activity_bursts | list[dict] | Remove @grouping |
| temporal | contact_first_appearance | dict[str, datetime] | Remove @grouping |
| temporal | contact_last_appearance | dict[str, datetime] | Remove @grouping |
| temporal | daily_activity_counts | dict[date, int] | Remove @grouping |
| location | location_timeline | list[dict] | Remove @spatial_grouping |
| location | frequent_locations_ranked | list[dict] | Remove @spatial_grouping |
| location | location_transitions | list[dict] | Remove @spatial_grouping |
| location | time_at_locations | dict[str, float] | Remove @spatial_grouping |

---

## Alternative: Keep Decorator for Filtering Only

If you want to leverage the `@grouping` decorator's filtering capabilities (part_of_week, part_of_day, interaction type), you could create a wrapper pattern:

```python
from bandicoot.helper.group import filter_user

def relationship_strength(user, part_of_week='allweek', part_of_day='allday', interaction=None):
    """
    Wrapper that uses Bandicoot filtering but returns custom data structures.
    """
    # Use Bandicoot's filtering
    records = filter_user(user, using='records', interaction=interaction,
                          part_of_week=part_of_week, part_of_day=part_of_day)

    if len(records) == 0:
        return {}

    # Custom logic with dict return...
    contact_stats = defaultdict(lambda: {'count': 0, 'duration': 0})
    # ... rest of implementation

    return scores
```

This gives you the filtering benefits without the statistics aggregation that causes the type errors.
