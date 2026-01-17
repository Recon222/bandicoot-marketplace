# Data-First Indicator Refactor - Completion Summary

**Date Completed:** 2026-01-17
**Version:** 0.2.0

## Summary

Successfully refactored 10 custom investigation indicators to follow a "data-first" design principle. All subjective scoring and confidence labels have been removed. Indicators now return raw observables with full methodology transparency, allowing investigators to interpret evidence themselves.

Additionally, created a new renderer layer (`render.py`) that transforms structured evidence into plain-English statements without subjective language.

## Changes by Phase

### Phase 1: High Priority Refactors
**Commit:** `9608b98`

Refactored the most critical indicators that had subjective fields:

1. **location_at_specific_time** - Removed `confidence` field
2. **group_locations_at_time** - Removed `confidence` and `activity_at_time` phrase
3. **meeting_detection** - Removed `confidence`, renamed conceptually to "colocation_with_context"
4. **synchronized_silence** - Removed `suspicion_score`, now sorted chronologically

Added utility functions:
- `serialize_record()` - Standardize Record to Event dict format
- `serialize_record_dict()` - Serialize record-like dictionaries
- `normalize_coordinates()` - Standardize coordinate formats

### Phase 2: Medium Priority Refactors
**Commit:** `fa11ecc`

Refactored indicators to expose raw data:

1. **time_at_locations** - Added `hit_count`, `assumption_minutes_per_hit`
2. **unusual_locations** - Returns full histogram plus filtered list (removed @spatial_grouping decorator)
3. **activity_bursts** - Exposed `computed_avg_rate`, `computed_threshold`, `data_span`
4. **inter_event_times** - Returns raw `deltas_seconds` list (removed @grouping decorator)
5. **activity_around_time** - Serialized events (no raw Record objects)

### Phase 3: Documentation and Consistency
**Commit:** `fbb3981`

Fixed documentation and exposed scoring methodology:

1. **relationship_strength** - Fixed docstring (removed false recency claim), exposed raw components and methodology weights

### Phase 4: Renderer Layer
**Commit:** `df27c16`

Created new `custom_indicators/render.py` module:

- `render_evidence(e)` - Returns list of human-readable lines
- `render_evidence_compact(e)` - Returns single-line summary
- Registered renderers for all 10 evidence types
- Enforced language rules (no subjective terms)

## Functions Modified

### location_at_specific_time (location.py)

**Removed:**
- `confidence` field (was: 'high'/'medium'/'low')

**Added:**
- `type`: "location_at_time"
- `support.closest_event_delta_sec`: raw seconds delta
- `support.events_in_window`: count of events
- `support.has_location`: boolean
- `events_in_window`: serialized Event list
- `coverage.total_events_in_window`, `events_with_antenna`, `missing_antenna_events`

**New Return Structure:**
```python
{
    "type": "location_at_time",
    "user_id": str | None,
    "window": {"center_ts": str, "before_min": int, "after_min": int},
    "support": {"closest_event_delta_sec": float, "events_in_window": int, "has_location": bool, "location_event_delta_sec": float},
    "location": {"antenna_id": str, "coord": {"lat": float, "lon": float} | None},
    "closest_event": {...},  # Serialized Event
    "events_in_window": [...],  # List of serialized Events
    "coverage": {"total_events_in_window": int, "events_with_antenna": int, "missing_antenna_events": int}
}
```

### group_locations_at_time (colocation.py)

**Removed:**
- `confidence` field per user
- `activity_at_time` phrase (e.g., "call out")

**Added:**
- `type`: "group_locations_at_time"
- `users[uid].support.closest_event_delta_sec`: raw seconds
- `users[uid].support.has_location`: boolean
- `users[uid].events_in_window`: serialized Event list
- `colocation_summary.by_antenna`: groups users by antenna

**New Return Structure:**
```python
{
    "type": "group_locations_at_time",
    "target_ts": str,
    "window_minutes": int,
    "users": {
        "user_id": {
            "support": {"closest_event_delta_sec": float, "events_in_window": int, "has_location": bool},
            "location": {"antenna_id": str, "coord": {...}},
            "closest_event": {...},
            "events_in_window": [...]
        }
    },
    "colocation_summary": {"by_antenna": {"antenna_id": ["user_id", ...]}}
}
```

### meeting_detection (colocation.py)

**Removed:**
- `confidence` field
- Renamed conceptually from "meeting" to "colocation_with_context"

**Added:**
- `type`: "colocation_with_context"
- `activity_context.user_a/user_b.records_around_count`: raw count
- `activity_context.user_a/user_b.records_around`: serialized Events
- `parameters`: methodology exposure

**New Return Structure:**
```python
[
    {
        "type": "colocation_with_context",
        "colocation": {"antenna_id": str, "coord": {...}, "user_a_time": str, "user_b_time": str, "delta_seconds": float},
        "activity_context": {
            "user_a": {"records_around_count": int, "records_around": [...], "gap_window_minutes": int},
            "user_b": {...}
        },
        "parameters": {"colocation_window_minutes": int, "gap_threshold_minutes": int}
    }
]
```

### synchronized_silence (colocation.py)

**Removed:**
- `suspicion_score` (was: 0-1 float)
- Sorting by suspicion score (now sorted chronologically)

**Added:**
- `type`: "synchronized_silence"
- `silence.start_ts`, `end_ts`, `duration_minutes`: timing
- `support.participant_count`, `total_users`, `participant_ratio`: raw counts
- `support.start_hour`, `is_daytime`: time context
- `parameters`: methodology exposure
- `preceding_events`, `following_events`: serialized Events per user

**New Return Structure:**
```python
[
    {
        "type": "synchronized_silence",
        "users": ["user_id", ...],
        "silence": {"start_ts": str, "end_ts": str, "duration_minutes": float},
        "parameters": {"min_silence_minutes": int, "min_overlap_minutes": int, "min_participants": int},
        "support": {"participant_count": int, "total_users": int, "participant_ratio": float, "start_hour": int, "is_daytime": bool},
        "preceding_events": {"user_id": {...}},
        "following_events": {"user_id": {...}}
    }
]
```

### time_at_locations (location.py)

**Removed:**
- Simple dict return (antenna -> estimated_hours)

**Added:**
- `type`: "time_at_locations"
- `locations[antenna].hit_count`: raw record count
- `locations[antenna].assumption_minutes_per_hit`: methodology exposure
- `totals.total_records_with_location`, `unique_antennas`

**New Return Structure:**
```python
{
    "type": "time_at_locations",
    "locations": {
        "antenna_id": {
            "hit_count": int,
            "estimated_hours": float,
            "assumption_minutes_per_hit": int,
            "coord": {"lat": float, "lon": float} | None
        }
    },
    "totals": {"total_records_with_location": int, "unique_antennas": int}
}
```

### unusual_locations (location.py)

**Removed:**
- `@spatial_grouping` decorator
- Function name implies judgment ("unusual")

**Added:**
- `type`: "location_visit_histogram"
- `all_locations`: full histogram for ALL locations
- `parameters.threshold_visits`: methodology exposure
- `filtered_below_threshold`: list of antenna_ids (not labeled as "unusual")

**New Return Structure:**
```python
{
    "type": "location_visit_histogram",
    "all_locations": {
        "antenna_id": {"visit_count": int, "coord": {...}, "timestamps": [str, ...]}
    },
    "parameters": {"threshold_visits": int},
    "filtered_below_threshold": ["antenna_id", ...]
}
```

### activity_bursts (temporal.py)

**Removed:**
- Old simple list return

**Added:**
- `type`: "activity_bursts"
- `parameters.computed_avg_rate`, `computed_threshold`: methodology transparency
- `data_span.first_record`, `last_record`, `total_records`
- `bursts[].events`: serialized Events in each burst

**New Return Structure:**
```python
{
    "type": "activity_bursts",
    "parameters": {"window_minutes": int, "threshold_multiplier": float, "computed_avg_rate": float, "computed_threshold": float},
    "data_span": {"first_record": str, "last_record": str, "total_records": int},
    "bursts": [
        {"start_ts": str, "end_ts": str, "count": int, "contacts": [str, ...], "events": [...]}
    ]
}
```

### inter_event_times (temporal.py)

**Removed:**
- `@grouping` decorator
- Returns only summary_stats

**Added:**
- `type`: "inter_event_times"
- `deltas_seconds`: raw list of all inter-event times

**New Return Structure:**
```python
{
    "type": "inter_event_times",
    "deltas_seconds": [float, ...],
    "summary": {"mean": float, "std": float, "min": float, "max": float, "median": float, "count": int}
}
```

### activity_around_time (temporal.py)

**Removed:**
- `before`, `after` as raw Record lists

**Added:**
- `type`: "activity_around_time"
- `before.events`, `after.events`: serialized Event lists
- `before.unique_contacts`, `after.unique_contacts`: counts

**New Return Structure:**
```python
{
    "type": "activity_around_time",
    "user_id": str,
    "window": {"center_ts": str, "before_hours": int, "after_hours": int},
    "support": {"events_before": int, "events_after": int, "total_events": int},
    "before": {"events": [...], "contacts": {"id": count}, "unique_contacts": int},
    "after": {"events": [...], "contacts": {"id": count}, "unique_contacts": int}
}
```

### relationship_strength (relationship.py)

**Removed:**
- False docstring claim about recency weighting

**Added:**
- `type`: "relationship_strength"
- `contacts[id].count`: raw interaction count
- `contacts[id].duration_sec`: raw call duration
- `contacts[id].score_components.count_norm`, `duration_norm`
- `methodology.count_weight`, `duration_weight`, `recency_weight`, `note`

**New Return Structure:**
```python
{
    "type": "relationship_strength",
    "user_id": str,
    "contacts": {
        "correspondent_id": {
            "score": float,
            "count": int,
            "duration_sec": int,
            "last_contact_ts": str,
            "score_components": {"count_norm": float, "duration_norm": float}
        }
    },
    "methodology": {"count_weight": 0.6, "duration_weight": 0.4, "recency_weight": 0.0, "note": str}
}
```

## New Files Created

### custom_indicators/render.py

Evidence renderer module providing:
- `render_evidence(e)` - Main entry point, returns list of human-readable lines
- `render_evidence_compact(e)` - Single-line summary for tables
- Dispatch system using evidence `type` field
- Registered renderers for all 10 evidence types

Language rules enforced:
- **Forbidden:** confidence, suspicious, likely, probably
- **Allowed:** found, within, closest, same tower, records, window
- **Missing data:** "unknown" or "no data present"

### custom_indicators/tests/__init__.py, test_data_first_indicators.py

Comprehensive test suite with 68 tests covering:
- Phase 1: No subjective fields tests
- Phase 2: Raw data exposure tests
- Phase 3: Documentation and methodology tests
- Phase 4: Renderer output tests

## Commits Made

| Commit Hash | Message |
|-------------|---------|
| `9608b98` | refactor(indicators): Remove subjective fields from high-priority indicators (Phase 1) |
| `fa11ecc` | refactor(indicators): Expose raw data in medium-priority indicators (Phase 2) |
| `fbb3981` | refactor(indicators): Fix relationship_strength docstring and expose components (Phase 3) |
| `df27c16` | feat(render): Add evidence renderer module for human-readable output (Phase 4) |

## Test Results

**Final validation:** 68 tests passed (100%)

Tests validate:
1. No subjective fields (`confidence`, `suspicion_score`) in any return
2. All required fields present (`type`, `support`, etc.)
3. Coordinates normalized to `{"lat": float, "lon": float}`
4. Events serialized to standard Event format
5. Renderer output contains no forbidden words
6. All edge cases handled (empty records, missing data)

## Version Bump

- Previous: 0.1.0
- Current: 0.2.0 (data-first refactor)
