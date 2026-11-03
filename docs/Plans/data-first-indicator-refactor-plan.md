# Data-First Indicator Refactor Plan

## Executive Summary

### Why This Refactor Matters

The current custom investigation indicators mix **data extraction** with **subjective interpretation**. Functions return fields like `confidence: 'high'`, `suspicion_score: 0.82`, and pre-interpreted phrases like `activity_at_time: "call out"`. This approach is problematic for investigative and evidentiary contexts because:

1. **Credibility Risk**: Labels like "high confidence" or "suspicious" can be interpreted as the system asserting truth or intent. This invites arguments like "the tool says this was suspicious," which is indefensible in court.

2. **Hidden Data**: Raw observables (actual record details, time deltas, counts) are collapsed into lossy abstractions, hiding the evidence that supports conclusions.

3. **Non-Reproducible Judgments**: Subjective scoring algorithms (e.g., suspicion_score with time-of-day heuristics) are opinion engines, not data extraction tools.

4. **Investigator Dependence**: The tool should present facts; investigators decide what those facts mean.

### The Solution: Data-First Architecture

**Indicators return only structured data** (timestamps, IDs, counts, deltas, lists of events). A separate **renderer layer** transforms that data into plain-English sentences for investigators who need human-readable output.

**Rule**: Indicators must never output: `confidence`, `suspicion`, `likely`, `probably`, `meeting`, `coordinated`. They may output: counts, deltas, durations, timestamps, IDs, normalized coordinates, and the actual records that support those numbers.

---

## Principles

### The Data-First Rules

1. **No Confidence Scores**: Never return `confidence: 'high'|'medium'|'low'`. Return the raw delta (`closest_event_delta_sec: 212`) and let consumers decide what "close enough" means.

2. **No Suspicion Ratings**: Never return `suspicion_score` or similar subjective metrics. Return the raw observables (duration, participant count, time of day) separately.

3. **Return Raw Observables**: Always include the underlying data that supports any calculation. If you compute a ratio, also return the numerator and denominator.

4. **Serialize Records**: Never return raw Python `Record` objects. Return structured dictionaries with all relevant fields.

5. **Normalize Coordinates**: Always return coordinates as `{"lat": float, "lon": float}`, never as tuples or position objects.

6. **Expose Methodology**: If you apply thresholds or heuristics, include them in the output so investigators understand what parameters were used.

7. **Separate Rendering**: Human-readable output is a presentation concern, not a data concern. Build a separate renderer layer.

---

## Canonical Schema

### Evidence Primitives

These standardized structures replace ad-hoc return formats across all indicators.

#### Event (Serialized CDR Record)

Use this everywhere you currently return a Record object or a human phrase.

```python
{
    "event_id": "optional-stable-id-or-null",          # Optional unique identifier
    "ts": "2026-01-16T14:03:21-05:00",                 # ISO 8601 timestamp
    "interaction": "call|text|data|unknown",           # Interaction type
    "direction": "in|out|unknown",                     # Direction
    "correspondent_id": "string-or-null",              # Contact phone/ID
    "duration_sec": 42,                                # Call duration (null for texts)
    "antenna_id": "string-or-null"                     # Antenna/tower ID
}
```

#### Coord (Normalized Coordinates)

Always normalize to this format, never tuples or position objects.

```python
{
    "lat": 43.123456,
    "lon": -79.123456
}
```

#### WindowSpec (Search Parameters)

Attach to any time-based query to document what was searched.

```python
{
    "center_ts": "2026-01-16T14:00:00-05:00",
    "before_min": 30,
    "after_min": 30
}
```

#### Support (Objective Strength Fields)

Replaces subjective `confidence`. Contains only observables.

```python
{
    "closest_event_delta_sec": 212,    # Seconds from target time
    "events_in_window": 4,             # Count of records found
    "has_location": True,              # Whether antenna data exists
    "location_event_delta_sec": 212    # Delta for record with location
}
```

#### Coverage (Data Availability Flags)

Documents data quality without interpretation.

```python
{
    "total_events_in_window": 4,
    "events_with_antenna": 3,
    "missing_antenna_events": 1
}
```

---

## Phase 1: High Priority Refactors

These functions contain explicit subjective scoring that must be removed immediately.

### 1.1 `location_at_specific_time` (location.py, lines 223-275)

**Current Problem**: Returns `confidence: 'high'|'medium'|'low'` based on `delta_seconds` thresholds.

**Current Return Structure**:
```python
{
    'antenna_id': closest.position.antenna,
    'coordinates': coords,                    # tuple, should be Coord
    'record_datetime': closest.datetime,
    'delta_seconds': delta_seconds,
    'confidence': 'high' if delta_seconds < 300 else 'medium' if delta_seconds < 900 else 'low',  # REMOVE
    'interaction': closest.interaction,
    'correspondent_id': closest.correspondent_id
}
```

**Proposed Return Structure**:
```python
{
    "type": "location_at_time",
    "user_id": user.name,                     # ADD: User identifier
    "window": {
        "center_ts": target_datetime.isoformat(),
        "before_min": window_minutes,
        "after_min": window_minutes
    },
    "support": {
        "closest_event_delta_sec": delta_seconds,
        "events_in_window": len(window_records),
        "has_location": True,
        "location_event_delta_sec": delta_seconds
    },
    "location": {
        "antenna_id": closest.position.antenna,
        "coord": {"lat": coords[0], "lon": coords[1]} if coords else None
    },
    "closest_event": {
        "ts": closest.datetime.isoformat(),
        "interaction": closest.interaction,
        "direction": closest.direction,
        "correspondent_id": closest.correspondent_id,
        "duration_sec": closest.call_duration,
        "antenna_id": closest.position.antenna
    },
    "events_in_window": [serialize_record(r) for r in window_records],
    "coverage": {
        "total_events_in_window": len(window_records),
        "events_with_antenna": len([r for r in window_records if r.position.antenna]),
        "missing_antenna_events": len([r for r in window_records if not r.position.antenna])
    }
}
```

**Changes**:
- REMOVE: `confidence` field
- ADD: `type`, `user_id`, `window`, `support`, `coverage`
- CHANGE: `coordinates` tuple -> `coord` object
- ADD: `events_in_window` serialized list
- ADD: `direction` and `duration_sec` to closest_event

---

### 1.2 `group_locations_at_time` (colocation.py, lines 538-642)

**Current Problem**: Returns `confidence: 'high'|'medium'|'low'|None` and collapses activity to a phrase like `"call out"`.

**Current Return Structure** (per user):
```python
{
    'antenna_id': antenna_id,
    'coordinates': coordinates,                # tuple or None
    'record_datetime': best_record.datetime,
    'delta_seconds': best_delta,
    'confidence': 'high'|'medium'|'low'|None,  # REMOVE
    'activity_at_time': "call out",            # REMOVE (phrase)
    'correspondent': best_record.correspondent_id
}
```

**Proposed Return Structure**:
```python
{
    "type": "group_locations_at_time",
    "target_ts": target_datetime.isoformat(),
    "window_minutes": window_minutes,
    "users": {
        user_id: {
            "support": {
                "closest_event_delta_sec": best_delta,
                "events_in_window": events_count,
                "has_location": antenna_id is not None
            },
            "location": {
                "antenna_id": antenna_id,
                "coord": {"lat": lat, "lon": lon} if coordinates else None
            },
            "closest_event": {
                "ts": best_record.datetime.isoformat(),
                "interaction": best_record.interaction,
                "direction": best_record.direction,
                "correspondent_id": best_record.correspondent_id,
                "duration_sec": best_record.call_duration,
                "antenna_id": antenna_id
            },
            "events_in_window": [serialize_record(r) for r in user_window_records]
        }
        # ... for each user
    },
    "colocation_summary": {
        # Optional: group users by antenna for quick detection
        "by_antenna": {
            antenna_id: [user_id1, user_id2, ...]
        }
    }
}
```

**Changes**:
- REMOVE: `confidence` field
- REMOVE: `activity_at_time` phrase (replaced with structured `closest_event`)
- ADD: `type`, `target_ts`, `window_minutes`, `support`, `events_in_window`
- CHANGE: `coordinates` -> nested `coord` object
- ADD: `colocation_summary` for quick co-location detection

---

### 1.3 `meeting_detection` (colocation.py, lines 150-217)

**Current Problem**: Returns `confidence: 'high'|'medium'|'low'` based on activity level heuristic. The function name itself implies interpretation.

**Current Return Structure**:
```python
{
    'antenna_id': coloc['antenna_id'],
    'time': meeting_time,
    'coordinates': coloc['coordinates'],
    'delta_seconds': coloc['delta_seconds'],
    'activity_around': activity_level,
    'confidence': 'high' if activity_level < 3 else 'medium' if activity_level < 6 else 'low'  # REMOVE
}
```

**Proposed Return Structure**:
```python
{
    "type": "colocation_with_context",
    "colocation": {
        "antenna_id": coloc['antenna_id'],
        "coord": {"lat": lat, "lon": lon} if coloc['coordinates'] else None,
        "user_a_time": coloc['user_a_time'].isoformat(),
        "user_b_time": coloc['user_b_time'].isoformat(),
        "delta_seconds": coloc['delta_seconds']
    },
    "activity_context": {
        "user_a": {
            "records_around_count": activity_level_a,
            "records_around": [serialize_record(r) for r in a_records_around],
            "gap_window_minutes": gap_threshold_minutes
        },
        "user_b": {
            "records_around_count": activity_level_b,
            "records_around": [serialize_record(r) for r in b_records_around],
            "gap_window_minutes": gap_threshold_minutes
        }
    },
    "pairwise_communication": {
        "in_window_count": 0,  # Count of A<->B comms in window
        "in_window_records": []  # If implemented
    },
    "parameters": {
        "colocation_window_minutes": colocation_window_minutes,
        "gap_threshold_minutes": gap_threshold_minutes
    }
}
```

**Changes**:
- REMOVE: `confidence` field
- RENAME: Consider renaming function to `colocation_with_activity_context`
- ADD: `type`, `activity_context` with both users, `pairwise_communication`
- ADD: `parameters` to expose methodology
- CHANGE: `coordinates` -> `coord` object
- ADD: `records_around` serialized list (the actual evidence)

---

### 1.4 `synchronized_silence` (colocation.py, lines 346-535)

**Current Problem**: Computes and returns `suspicion_score` with subjective time-of-day weighting ("daytime is more suspicious").

**Current Return Structure**:
```python
{
    'start': current_overlap_start,
    'end': overlap_end,
    'duration_minutes': duration_seconds / 60,
    'participants': list(current_participants.keys()),
    'participant_count': len(current_participants),
    'preceding_activity': preceding_activity,      # Contains dicts, good
    'following_activity': following_activity,       # Contains dicts, good
    'suspicion_score': round(suspicion_score, 3)   # REMOVE
}
```

**Proposed Return Structure**:
```python
{
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
        "start_hour": current_overlap_start.hour,
        "is_daytime": 9 <= current_overlap_start.hour <= 21
    },
    "preceding_events": {
        uid: serialize_record_dict(sinfo['last_before'])
        for uid, sinfo in current_participants.items()
    },
    "following_events": {
        uid: serialize_record_dict(sinfo['first_after'])
        for uid, sinfo in current_participants.items()
    }
}
```

**Changes**:
- REMOVE: `suspicion_score` entirely
- ADD: `type`, `silence` object with ISO timestamps
- ADD: `parameters` to expose methodology
- ADD: `support.start_hour`, `support.is_daytime` (raw observables, not scores)
- ADD: `support.participant_ratio` (raw ratio, not weighted score)
- CHANGE: Sort by `start_ts` chronologically, not by suspicion

---

## Phase 2: Medium Priority Refactors

These functions have lossy abstractions that hide useful raw data.

### 2.1 `time_at_locations` (location.py, lines 195-220)

**Current Problem**: Returns only `estimated_hours` based on hardcoded heuristic (each record = 0.5 hours), hiding the raw count.

**Current Return**:
```python
{str(antenna): count * 0.5 for antenna, count in location_counts.items()}
```

**Proposed Return Structure**:
```python
{
    "type": "time_at_locations",
    "locations": {
        antenna_id: {
            "hit_count": count,
            "estimated_hours": count * 0.5,
            "assumption_minutes_per_hit": 30
        }
        # ... for each antenna
    },
    "totals": {
        "total_records_with_location": total_count,
        "unique_antennas": len(location_counts)
    }
}
```

**Changes**:
- ADD: `hit_count` (raw data)
- ADD: `assumption_minutes_per_hit` (exposes heuristic)
- ADD: `totals` summary

---

### 2.2 `unusual_locations` (location.py, lines 102-143)

**Current Problem**: Only returns locations below threshold, hiding the full distribution. "Unusual" is an interpretive label.

**Current Return**: List of locations with `visit_count <= threshold_visits`

**Proposed Return Structure**:
```python
{
    "type": "location_visit_histogram",
    "all_locations": {
        antenna_id: {
            "visit_count": count,
            "coord": {"lat": lat, "lon": lon} if coords else None,
            "timestamps": [ts.isoformat() for ts in sorted_timestamps]
        }
        # ... for ALL antennas
    },
    "parameters": {
        "threshold_visits": threshold_visits
    },
    "filtered_below_threshold": [
        # List of antenna_ids with visit_count <= threshold
    ]
}
```

**Changes**:
- ADD: `all_locations` with full histogram
- ADD: `parameters.threshold_visits` to expose methodology
- ADD: `filtered_below_threshold` as convenience (but full data available)

---

### 2.3 `activity_bursts` (temporal.py, lines 85-147)

**Current Problem**: Classifies windows as "bursts" but doesn't return the baseline/threshold values used.

**Current Return**:
```python
{
    'start': window_start,
    'end': window_end,
    'count': count,
    'contacts': list(set(r.correspondent_id for r in window_records))
}
```

**Proposed Return Structure**:
```python
{
    "type": "activity_bursts",
    "parameters": {
        "window_minutes": window_minutes,
        "threshold_multiplier": threshold_multiplier,
        "computed_avg_rate": avg_rate,
        "computed_threshold": threshold
    },
    "data_span": {
        "first_record": sorted_records[0].datetime.isoformat(),
        "last_record": sorted_records[-1].datetime.isoformat(),
        "total_records": len(records)
    },
    "bursts": [
        {
            "start_ts": window_start.isoformat(),
            "end_ts": window_end.isoformat(),
            "count": count,
            "contacts": contacts_list,
            "events": [serialize_record(r) for r in window_records]
        }
        # ... for each burst
    ]
}
```

**Changes**:
- ADD: `parameters` with `computed_avg_rate` and `computed_threshold`
- ADD: `data_span` showing what data was analyzed
- ADD: `events` with serialized records (the actual evidence)

---

### 2.4 `inter_event_times` (temporal.py, lines 232-253)

**Current Problem**: Returns only `summary_stats(deltas)`, losing the raw delta list.

**Current Return**: `SummaryStats` object (mean, std, min, max, etc.)

**Proposed Return Structure**:
```python
{
    "type": "inter_event_times",
    "deltas_seconds": deltas,  # Raw list
    "summary": {
        "mean": summary.mean,
        "std": summary.std,
        "min": summary.min,
        "max": summary.max,
        "median": summary.median,
        "count": len(deltas)
    }
}
```

**Changes**:
- ADD: `deltas_seconds` raw list
- KEEP: `summary` statistics (but alongside raw data)

---

### 2.5 `activity_around_time` (temporal.py, lines 256-294)

**Current Problem**: Returns raw `Record` objects in `before`/`after` lists, which blocks export and requires ad-hoc interpretation.

**Current Return**:
```python
{
    'before': before_records,      # Raw Record objects
    'after': after_records,        # Raw Record objects
    'contacts_before': Counter(...),
    'contacts_after': Counter(...),
    'count_before': len(before_records),
    'count_after': len(after_records)
}
```

**Proposed Return Structure**:
```python
{
    "type": "activity_around_time",
    "user_id": user.name,
    "window": {
        "center_ts": target_datetime.isoformat(),
        "before_hours": hours_before,
        "after_hours": hours_after
    },
    "support": {
        "events_before": len(before_records),
        "events_after": len(after_records),
        "total_events": len(before_records) + len(after_records)
    },
    "before": {
        "events": [serialize_record(r) for r in before_records],
        "contacts": dict(contacts_before),
        "unique_contacts": len(contacts_before)
    },
    "after": {
        "events": [serialize_record(r) for r in after_records],
        "contacts": dict(contacts_after),
        "unique_contacts": len(contacts_after)
    }
}
```

**Changes**:
- CHANGE: `before`/`after` from Record lists to serialized event lists
- ADD: `type`, `user_id`, `window`, `support`
- ADD: `unique_contacts` counts

---

## Phase 3: Documentation and Consistency Fixes

### 3.1 `relationship_strength` Docstring Fix (relationship.py, lines 17-64)

**Current Problem**: Docstring claims the composite includes "recency" but recency is not implemented. Comment says "20% recency not implemented yet" but weights are 60%/40%.

**Current Code**:
```python
def relationship_strength(user):
    """
    Rank contacts by communication intensity.

    Combines frequency, total call duration, and interaction recency into
    a composite score.  # <-- CLAIMS RECENCY
    ...
    """
    # Weight: 50% frequency, 30% duration, 20% recency not implemented yet
    freq_score = stats['count'] / max_count
    dur_score = stats['duration'] / max_duration
    scores[cid] = (0.6 * freq_score) + (0.4 * dur_score)  # <-- 60/40, no recency
```

**Fix Options**:

**Option A**: Remove recency claims entirely:
```python
def relationship_strength(user):
    """
    Rank contacts by communication intensity.

    Combines frequency and total call duration into a composite score.
    ...
    Returns
    -------
    dict
        correspondent_id -> {
            'score': float,
            'count': int,
            'duration_sec': int,
            'last_contact_ts': datetime or None,
            'score_components': {'count_norm': float, 'duration_norm': float}
        }
    """
```

**Option B**: Actually implement recency and expose components:
```python
# Return raw components alongside score
return {
    cid: {
        'score': score,
        'count': stats['count'],
        'duration_sec': stats['duration'],
        'last_contact_ts': stats['last'].isoformat() if stats['last'] else None,
        'score_components': {
            'count_norm': freq_score,
            'duration_norm': dur_score
            # 'recency_norm': recency_score  # If implemented
        }
    }
    for cid, stats in contact_stats.items()
}
```

**Recommendation**: Option B - expose raw components alongside score.

---

### 3.2 Standardize Coordinate Handling

**Problem**: Coordinates are inconsistently returned as:
- Tuples: `(lat, lon)`
- Position objects: `ant_data.latitude`, `ant_data.longitude`
- Direct from antennas dict (varies by data source)

**Solution**: Create utility function in `utils.py`:

```python
def normalize_coordinates(antenna_id, antennas_dict):
    """
    Extract and normalize coordinates to standard Coord format.

    Parameters
    ----------
    antenna_id : str
        The antenna identifier
    antennas_dict : dict
        User's antennas dictionary

    Returns
    -------
    dict or None
        {"lat": float, "lon": float} or None if not available
    """
    if not antennas_dict or antenna_id not in antennas_dict:
        return None

    ant_data = antennas_dict[antenna_id]

    # Handle Position object
    if hasattr(ant_data, 'latitude') and hasattr(ant_data, 'longitude'):
        return {"lat": ant_data.latitude, "lon": ant_data.longitude}

    # Handle tuple/list
    if isinstance(ant_data, (list, tuple)) and len(ant_data) >= 2:
        return {"lat": ant_data[0], "lon": ant_data[1]}

    # Handle dict
    if isinstance(ant_data, dict):
        if 'lat' in ant_data and 'lon' in ant_data:
            return {"lat": ant_data['lat'], "lon": ant_data['lon']}
        if 'latitude' in ant_data and 'longitude' in ant_data:
            return {"lat": ant_data['latitude'], "lon": ant_data['longitude']}

    return None
```

---

### 3.3 Standardize Record Serialization

**Solution**: Create `serialize_record` utility in `utils.py`:

```python
def serialize_record(record):
    """
    Serialize a Bandicoot Record to standard Event format.

    Parameters
    ----------
    record : bandicoot.core.Record

    Returns
    -------
    dict
        Standardized Event dictionary
    """
    return {
        "ts": record.datetime.isoformat(),
        "interaction": record.interaction,
        "direction": record.direction,
        "correspondent_id": record.correspondent_id,
        "duration_sec": record.call_duration,
        "antenna_id": record.position.antenna if record.position else None
    }


def serialize_record_dict(record_dict):
    """
    Serialize a record-like dictionary (as used in synchronized_silence context).

    Parameters
    ----------
    record_dict : dict
        Dictionary with record-like fields

    Returns
    -------
    dict
        Standardized Event dictionary
    """
    return {
        "ts": record_dict.get('datetime').isoformat() if record_dict.get('datetime') else None,
        "interaction": record_dict.get('interaction'),
        "direction": record_dict.get('direction'),
        "correspondent_id": record_dict.get('correspondent_id'),
        "duration_sec": record_dict.get('call_duration'),
        "antenna_id": record_dict.get('antenna_id')
    }
```

---

## Phase 4: Renderer Layer Implementation

### 4.1 Create `render.py` Module

Create new file: `custom_indicators/render.py`

```python
"""
Evidence Renderer
=================

Transforms structured evidence objects from indicators into
plain-English statements for investigators.

Rules:
- Never use: confidence, suspicious, likely, probably, meeting, coordinated
- Allowed: found, within, closest, same tower, records, window, duration, count
- If data missing: say "unknown" or "no data present", not guesses
"""

from typing import Any, Dict, List, Optional, Callable

Evidence = Dict[str, Any]

# ==============================================================================
# Dispatch System
# ==============================================================================

_RENDERERS: Dict[str, Callable[[Evidence], List[str]]] = {}


def register_renderer(evidence_type: str):
    """Decorator to register a renderer for an evidence type."""
    def decorator(func):
        _RENDERERS[evidence_type] = func
        return func
    return decorator


def render_evidence(e: Evidence) -> List[str]:
    """
    Main entry point. Dispatches on e['type'] and returns human-readable lines.

    Parameters
    ----------
    e : dict
        Evidence object with 'type' field

    Returns
    -------
    list of str
        Human-readable statements about the evidence
    """
    evidence_type = e.get("type", "unknown")
    renderer = _RENDERERS.get(evidence_type)

    if renderer is None:
        return [f"Unknown evidence type: {evidence_type}"]

    return renderer(e)


def render_evidence_compact(e: Evidence) -> str:
    """
    One-liner summary for table cells or quick lists.
    """
    t = e.get("type", "unknown")

    if t == "location_at_time":
        loc = e.get("location", {}) or {}
        s = e.get("support", {}) or {}
        return (
            f"{e.get('user_id', 'user')} | tower {loc.get('antenna_id', 'n/a')} | "
            f"closest delta {_fmt_delta_seconds(s.get('closest_event_delta_sec'))}"
        )

    if t == "colocation_with_context":
        coloc = e.get("colocation", {}) or {}
        return (
            f"Tower {coloc.get('antenna_id', 'n/a')} | "
            f"delta {_fmt_delta_seconds(coloc.get('delta_seconds'))}"
        )

    if t == "synchronized_silence":
        sil = e.get("silence", {}) or {}
        return (
            f"Silence | {_fmt_ts(sil.get('start_ts'))} to {_fmt_ts(sil.get('end_ts'))} | "
            f"{_fmt_minutes(sil.get('duration_minutes'))}"
        )

    return f"{t}"


# ==============================================================================
# Formatting Helpers
# ==============================================================================

def _fmt_ts(ts: Optional[str]) -> str:
    """Format ISO timestamp for display."""
    if not ts:
        return "unknown time"
    # Simple cleanup - remove microseconds and timezone for readability
    return ts.replace("T", " ").split(".")[0]


def _fmt_delta_seconds(sec: Optional[float]) -> str:
    """Format seconds delta as human-readable duration."""
    if sec is None:
        return "unknown"
    sec = abs(int(sec))
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def _fmt_minutes(mins: Optional[float]) -> str:
    """Format minutes as human-readable duration."""
    if mins is None:
        return "unknown"
    mins = float(mins)
    if mins >= 60:
        h = int(mins // 60)
        m = int(round(mins % 60))
        return f"{h}h {m}m" if m else f"{h}h"
    return f"{int(round(mins))}m"


def _fmt_coord(coord: Optional[dict]) -> str:
    """Format coordinate dict for display."""
    if not coord:
        return "no coordinates"
    lat = coord.get("lat")
    lon = coord.get("lon")
    if lat is None or lon is None:
        return "no coordinates"
    return f"{lat:.6f}, {lon:.6f}"


def _safe_int(x: Any, default: int = 0) -> int:
    """Safely convert to int."""
    try:
        return int(x)
    except Exception:
        return default


# ==============================================================================
# Evidence Type Renderers
# ==============================================================================

@register_renderer("location_at_time")
def render_location_at_time(e: Evidence) -> List[str]:
    """Render location_at_time evidence."""
    user_id = e.get("user_id", "unknown user")
    w = e.get("window", {}) or {}
    s = e.get("support", {}) or {}
    loc = e.get("location", {}) or {}
    cov = e.get("coverage", {}) or {}

    lines: List[str] = []
    lines.append(f"User: {user_id}")
    lines.append(
        f"Searched {w.get('before_min', '?')} min before and {w.get('after_min', '?')} min "
        f"after {_fmt_ts(w.get('center_ts'))}."
    )
    lines.append(
        f"Found {_safe_int(s.get('events_in_window'))} phone records in that window; "
        f"closest record is {_fmt_delta_seconds(s.get('closest_event_delta_sec'))} from the time."
    )

    antenna_id = loc.get("antenna_id")
    coord = loc.get("coord")
    if antenna_id:
        lines.append(f"Closest tower near that time: {antenna_id} ({_fmt_coord(coord)}).")
    else:
        lines.append("No tower/location data available near that time.")

    # Coverage note
    total = cov.get("total_events_in_window")
    with_ant = cov.get("events_with_antenna")
    if total is not None and with_ant is not None:
        lines.append(f"Location data present on {with_ant} of {total} records in the window.")

    return lines


@register_renderer("group_locations_at_time")
def render_group_locations_at_time(e: Evidence) -> List[str]:
    """Render group_locations_at_time evidence."""
    lines: List[str] = []
    lines.append(f"Target time: {_fmt_ts(e.get('target_ts'))}")
    lines.append(f"Search window: {e.get('window_minutes', '?')} minutes")
    lines.append("")

    users = e.get("users", {})
    for uid, data in users.items():
        s = data.get("support", {}) or {}
        loc = data.get("location", {}) or {}

        if s.get("has_location"):
            lines.append(
                f"{uid}: Tower {loc.get('antenna_id')} ({_fmt_coord(loc.get('coord'))}), "
                f"closest record {_fmt_delta_seconds(s.get('closest_event_delta_sec'))} from target."
            )
        else:
            lines.append(f"{uid}: No location data within window.")

    return lines


@register_renderer("colocation_with_context")
def render_colocation_with_context(e: Evidence) -> List[str]:
    """Render colocation_with_context evidence (formerly meeting_detection)."""
    coloc = e.get("colocation", {}) or {}
    ctx = e.get("activity_context", {}) or {}
    params = e.get("parameters", {}) or {}

    lines: List[str] = []
    lines.append(
        f"Both devices at tower {coloc.get('antenna_id')} ({_fmt_coord(coloc.get('coord'))})."
    )
    lines.append(
        f"User A time: {_fmt_ts(coloc.get('user_a_time'))}. "
        f"User B time: {_fmt_ts(coloc.get('user_b_time'))}. "
        f"Time difference: {_fmt_delta_seconds(coloc.get('delta_seconds'))}."
    )

    for user_key in ["user_a", "user_b"]:
        user_ctx = ctx.get(user_key, {})
        if user_ctx:
            lines.append(
                f"{user_key.replace('_', ' ').title()}: "
                f"{user_ctx.get('records_around_count', 0)} records within "
                f"{user_ctx.get('gap_window_minutes', '?')} min of co-location."
            )

    return lines


@register_renderer("synchronized_silence")
def render_synchronized_silence(e: Evidence) -> List[str]:
    """Render synchronized_silence evidence."""
    users = e.get("users") or []
    silence = e.get("silence", {}) or {}
    params = e.get("parameters", {}) or {}
    support = e.get("support", {}) or {}

    lines: List[str] = []
    lines.append(f"Devices: {', '.join(users) if users else 'none listed'}")
    lines.append(
        f"No phone records for all listed devices from {_fmt_ts(silence.get('start_ts'))} "
        f"to {_fmt_ts(silence.get('end_ts'))} (duration {_fmt_minutes(silence.get('duration_minutes'))})."
    )

    if params:
        lines.append(
            f"Parameters: min silence {params.get('min_silence_minutes', '?')}m; "
            f"min overlap {params.get('min_overlap_minutes', '?')}m."
        )

    # Context counts
    preceding = e.get("preceding_events", {}) or {}
    following = e.get("following_events", {}) or {}
    for uid in users:
        pre = preceding.get(uid)
        post = following.get(uid)
        pre_ts = _fmt_ts(pre.get('ts')) if pre else "unknown"
        post_ts = _fmt_ts(post.get('ts')) if post else "unknown"
        lines.append(f"{uid}: last activity before gap at {pre_ts}; first after at {post_ts}.")

    return lines


@register_renderer("activity_around_time")
def render_activity_around_time(e: Evidence) -> List[str]:
    """Render activity_around_time evidence."""
    user_id = e.get("user_id", "unknown user")
    w = e.get("window", {}) or {}
    s = e.get("support", {}) or {}
    before = e.get("before", {}) or {}
    after = e.get("after", {}) or {}

    lines: List[str] = []
    lines.append(f"User: {user_id}")
    lines.append(
        f"Window: {w.get('before_hours', '?')} hours before and "
        f"{w.get('after_hours', '?')} hours after {_fmt_ts(w.get('center_ts'))}."
    )
    lines.append(
        f"Records before: {_safe_int(s.get('events_before'))} "
        f"({before.get('unique_contacts', 0)} unique contacts)."
    )
    lines.append(
        f"Records after: {_safe_int(s.get('events_after'))} "
        f"({after.get('unique_contacts', 0)} unique contacts)."
    )

    return lines


@register_renderer("relationship_summary")
def render_relationship_summary(e: Evidence) -> List[str]:
    """Render relationship_summary evidence."""
    user_id = e.get("user_id", "unknown user")
    contact_id = e.get("contact_id", "unknown contact")
    m = e.get("metrics", {}) or {}
    rank = e.get("rank_fields", {}) or {}

    lines: List[str] = []
    lines.append(f"User: {user_id} | Contact: {contact_id}")
    lines.append(
        f"Total interactions: {m.get('total_interactions', 0)} "
        f"({m.get('total_calls', 0)} calls, {m.get('total_texts', 0)} texts)."
    )
    lines.append(
        f"Direction: outgoing {m.get('outgoing_interactions', 0)}, "
        f"incoming {m.get('incoming_interactions', 0)}."
    )
    if m.get("first_contact_ts"):
        lines.append(f"First observed interaction: {_fmt_ts(m.get('first_contact_ts'))}.")
    if m.get("last_contact_ts"):
        lines.append(f"Most recent interaction: {_fmt_ts(m.get('last_contact_ts'))}.")

    if "relationship_strength_score" in rank:
        lines.append(
            f"Computed contact-intensity index: {rank.get('relationship_strength_score')} (deterministic)."
        )

    return lines
```

---

## Phase 5: Testing and Validation

### 5.1 Test New Return Structures

Create test file: `tests/test_data_first_indicators.py`

```python
"""
Tests for data-first indicator return structures.

Validates:
1. No subjective fields (confidence, suspicion_score)
2. Required fields present
3. Coordinates normalized to {"lat": float, "lon": float}
4. Records serialized to Event format
"""

import pytest
from datetime import datetime


def test_location_at_specific_time_no_confidence():
    """Verify location_at_specific_time returns no confidence field."""
    # Setup
    from custom_indicators.location import location_at_specific_time

    # Would need mock user with records
    # result = location_at_specific_time(user, target_datetime)

    # Assertions
    # assert 'confidence' not in result
    # assert 'support' in result
    # assert 'closest_event_delta_sec' in result['support']
    pass


def test_group_locations_no_confidence():
    """Verify group_locations_at_time returns no confidence field."""
    pass


def test_meeting_detection_no_confidence():
    """Verify colocation_with_activity_context returns no confidence field."""
    pass


def test_synchronized_silence_no_suspicion():
    """Verify synchronized_silence returns no suspicion_score."""
    pass


def test_coordinates_normalized():
    """Verify all coordinate returns use {"lat": float, "lon": float} format."""
    pass


def test_records_serialized():
    """Verify records are serialized to Event dicts, not raw Record objects."""
    pass


# Validation helpers

FORBIDDEN_FIELDS = ['confidence', 'suspicion_score', 'suspicion', 'likely', 'probably']


def assert_no_subjective_fields(result, path=""):
    """Recursively check that no subjective fields exist."""
    if isinstance(result, dict):
        for key, value in result.items():
            current_path = f"{path}.{key}" if path else key
            assert key not in FORBIDDEN_FIELDS, f"Forbidden field found at {current_path}"
            assert_no_subjective_fields(value, current_path)
    elif isinstance(result, list):
        for i, item in enumerate(result):
            assert_no_subjective_fields(item, f"{path}[{i}]")


def assert_has_required_fields(result, required_fields):
    """Check that all required fields are present."""
    for field in required_fields:
        parts = field.split('.')
        current = result
        for part in parts:
            assert part in current, f"Missing required field: {field}"
            current = current[part]
```

### 5.2 Validation Checklist

Before marking refactor complete, verify for EACH modified function:

- [ ] No `confidence` field in return
- [ ] No `suspicion_score` field in return
- [ ] No `suspicion` or `likely` or `probably` in any string values
- [ ] Coordinates returned as `{"lat": float, "lon": float}`
- [ ] All Record objects serialized to Event dicts
- [ ] `type` field present for renderer dispatch
- [ ] `parameters` included where methodology needs exposure
- [ ] `support` object includes raw observables

---

## Migration Guide

### For Code Consuming These Indicators

#### Before: Checking Confidence

```python
# OLD CODE
result = location_at_specific_time(user, target)
if result and result['confidence'] == 'high':
    # High confidence location
    process_location(result)
```

#### After: Check Raw Delta

```python
# NEW CODE
result = location_at_specific_time(user, target)
if result:
    delta_sec = result['support']['closest_event_delta_sec']
    if delta_sec < 300:  # Your threshold
        process_location(result)
```

#### Before: Using Activity Phrase

```python
# OLD CODE
results = group_locations_at_time(users, user_ids, target)
for uid, data in results.items():
    print(f"{uid} was doing: {data['activity_at_time']}")
```

#### After: Use Serialized Event

```python
# NEW CODE
results = group_locations_at_time(users, user_ids, target)
for uid, data in results['users'].items():
    event = data['closest_event']
    print(f"{uid}: {event['interaction']} {event['direction']} with {event['correspondent_id']}")
```

#### Before: Sorting by Suspicion

```python
# OLD CODE
silences = synchronized_silence(users, user_ids)
# Already sorted by suspicion_score descending
top_suspicious = silences[0]
```

#### After: Sort by Your Criteria

```python
# NEW CODE
silences = synchronized_silence(users, user_ids)
# Now sorted chronologically - sort by your own criteria
silences.sort(key=lambda x: x['silence']['duration_minutes'], reverse=True)
longest_silence = silences[0]
```

#### Using the Renderer

```python
# NEW: Human-readable output
from custom_indicators.render import render_evidence, render_evidence_compact

result = location_at_specific_time(user, target)
if result:
    # Full multi-line output
    for line in render_evidence(result):
        print(line)

    # Or one-liner for tables
    print(render_evidence_compact(result))
```

---

## Appendix: Function-by-Function Mapping Table

### location.py

| Function | Current Returns | Subjective Fields | Proposed Changes |
|----------|-----------------|-------------------|------------------|
| `location_timeline` | list of dict | None | Add `coord` normalization |
| `frequent_locations_ranked` | list of dict | None | Add `coord` normalization |
| `unusual_locations` | list of dict (filtered) | "unusual" label | Return full histogram + filtered list |
| `location_transitions` | list of dict | None | Add `coord` normalization |
| `time_at_locations` | dict (antenna -> hours) | Hidden heuristic | Add `hit_count`, `assumption` |
| `location_at_specific_time` | dict | **`confidence`** | **REMOVE confidence**, add `type`, `support`, `coverage` |
| `locations_in_time_range` | list of dict | None | Add `coord` normalization |

### colocation.py

| Function | Current Returns | Subjective Fields | Proposed Changes |
|----------|-----------------|-------------------|------------------|
| `antenna_overlap` | list of dict | None | Add `coord` normalization |
| `travel_pattern_match` | list of dict | None | None required |
| `meeting_detection` | list of dict | **`confidence`** | **REMOVE confidence**, add `type`, `activity_context`, `parameters` |
| `multi_user_colocation` | list of dict | None | Add `coord` normalization |
| `proximity_to_location` | list of dict | None | None required |
| `synchronized_silence` | list of dict | **`suspicion_score`** | **REMOVE suspicion_score**, add `type`, `parameters`, serialize events |
| `group_locations_at_time` | dict | **`confidence`**, **`activity_at_time` phrase** | **REMOVE confidence/phrase**, add `type`, `support`, serialize events |

### temporal.py

| Function | Current Returns | Subjective Fields | Proposed Changes |
|----------|-----------------|-------------------|------------------|
| `hourly_activity_profile` | dict | None | None required |
| `communication_gaps` | list of dict | None | None required |
| `activity_bursts` | list of dict | Hidden baseline | Add `parameters` with `avg_rate`, `threshold` |
| `contact_first_appearance` | dict | None | None required |
| `contact_last_appearance` | dict | None | None required |
| `daily_activity_counts` | dict | None | None required |
| `inter_event_times` | SummaryStats | Data lost | Return `deltas_seconds` list + summary |
| `activity_around_time` | dict with Record objects | Raw objects | Serialize to Event dicts |
| `first_contact_after_time` | dict | None | None required |

### relationship.py

| Function | Current Returns | Subjective Fields | Proposed Changes |
|----------|-----------------|-------------------|------------------|
| `relationship_strength` | dict (score only) | Docstring mismatch | Fix docstring, expose components |
| `reciprocity_score` | dict | None | None required |
| `initiation_ratio` | dict | None | None required |
| `first_contact_of_day` | dict | None | None required |
| `last_contact_of_day` | dict | None | None required |
| `contact_interaction_summary` | dict | None | Serialize datetimes to ISO |

### network.py

| Function | Current Returns | Subjective Fields | Proposed Changes |
|----------|-----------------|-------------------|------------------|
| `build_communication_matrix` | dict | None | None required |
| `degree_centrality` | dict | None | None required |
| `communication_chains` | list of dict | None | None required |
| `shared_contacts` | dict | None | None required |
| `communication_volume_matrix` | dict | None | None required |
| `network_timeline` | list of dict | None | Serialize datetimes to ISO |
| `identify_bridges` | list of dict | None | None required |

### utils.py

| Function | Current Role | Proposed Changes |
|----------|--------------|------------------|
| `load_id_mapping` | Support | None required |
| `resolve_contact` | Support | None required |
| `resolve_contacts` | Support | Make recursive for nested structures |
| `records_in_window` | Support | None required |
| `records_around_time` | Support | None required |
| `contacts_in_window` | Support | None required |
| `location_at_time` | Support | Add `coord` normalization |
| `filter_by_*` | Support | None required |
| `parse_datetime` | Support | None required |
| `format_duration` | Support | Move to render.py |
| **NEW** `serialize_record` | - | **ADD** |
| **NEW** `serialize_record_dict` | - | **ADD** |
| **NEW** `normalize_coordinates` | - | **ADD** |

---

## Implementation Order

**Week 1: Core Infrastructure**
1. Add `serialize_record`, `serialize_record_dict`, `normalize_coordinates` to utils.py
2. Create `render.py` with base structure and formatting helpers

**Week 2: Phase 1 High Priority**
1. Refactor `location_at_specific_time`
2. Refactor `group_locations_at_time`
3. Refactor `meeting_detection` (rename to `colocation_with_activity_context`)
4. Refactor `synchronized_silence`
5. Add renderers for each

**Week 3: Phase 2 Medium Priority**
1. Refactor `time_at_locations`
2. Refactor `unusual_locations`
3. Refactor `activity_bursts`
4. Refactor `inter_event_times`
5. Refactor `activity_around_time`

**Week 4: Phase 3 Cleanup**
1. Fix `relationship_strength` docstring and expose components
2. Apply `normalize_coordinates` throughout
3. Apply `serialize_record` throughout
4. ISO format all datetime returns

**Week 5: Testing and Documentation**
1. Write/update tests for all modified functions
2. Verify no subjective fields remain
3. Update any documentation
4. Update migration examples

---

## Summary

This refactor transforms the custom indicators from an "opinion engine" into a "data extraction tool." By removing subjective labels and exposing raw observables, the indicators become:

1. **Defensible**: No claims of intent or truth - just data
2. **Transparent**: Methodology exposed via parameters
3. **Flexible**: Consumers can apply their own thresholds
4. **Exportable**: All data serialized to standard formats
5. **Human-Readable**: Via separate renderer layer

The separation of data extraction (indicators) from presentation (renderer) is the key architectural change. Investigators get plain-English output, but the underlying data remains pure and defensible.
