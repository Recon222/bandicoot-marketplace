# Real Data Validation Results

**Date:** 2026-01-17
**Dataset:** Bandicoot demo dataset (modified)
**Purpose:** Validate refactored data-first indicators against real Bandicoot data

> **Important Context:** This is a modified Bandicoot demo dataset, NOT a criminal network dataset. The effectiveness of these indicators for actual investigation scenarios has not been validated with real law enforcement data.

---

## 1. Dataset Overview

### Files Found

| File Type | Count | Location |
|-----------|-------|----------|
| User record files | 40 | `*.csv` (phone numbers as filenames) |
| Antenna file | 1 | `antennas.csv` |
| ID Mapping | 1 | `_ID_MAPPING.csv` |

### Data Structure

**User Records (e.g., `416-225-5506.csv`):**
| Column | Values |
|--------|--------|
| `datetime` | `YYYY-MM-DD HH:MM:SS` format |
| `interaction` | `call`, `text` |
| `direction` | `in`, `out` |
| `correspondent_id` | Phone numbers (e.g., `416-367-8573`) |
| `call_duration` | Seconds (empty for texts) |
| `antenna_id` | Tower IDs (e.g., `701`, `702`) |

**Antennas (`antennas.csv`):**
| Column | Example |
|--------|---------|
| `antenna_id` | `701` |
| `latitude` | `43.704542` |
| `longitude` | `-79.376765` |

**ID Mapping (`_ID_MAPPING.csv`):**
| Column | Example |
|--------|---------|
| `name` | `Marcus Chen` |
| `phone_number` | `416-225-5506` |

### Dataset Statistics

- **Total users:** 40
- **Antenna towers:** 7
- **Date range:** 2012-01-02 to 2012-02-27 (~57 days)
- **Sample user (416-225-5506):** 150 records

---

## 2. Indicator Execution Results

### Phase 1: High Priority Indicators

#### `location_at_specific_time`

| Metric | Result |
|--------|--------|
| Executed without errors | Yes |
| Has `type` field | Yes (`"location_at_time"`) |
| Subjective fields absent | Yes |
| Coordinates normalized | Yes (`{"lat": ..., "lon": ...}`) |
| Events serialized | Yes |

**Sample Return Structure:**
```json
{
  "type": "location_at_time",
  "user_id": "416-225-5506",
  "window": {
    "center_ts": "2012-01-02T00:25:27",
    "before_min": 60,
    "after_min": 60
  },
  "support": {
    "closest_event_delta_sec": 0.0,
    "events_in_window": 1,
    "has_location": true,
    "location_event_delta_sec": 0.0
  },
  "location": {
    "antenna_id": "703",
    "coord": {"lat": 44.103724, "lon": -79.593519}
  },
  "closest_event": {
    "ts": "2012-01-02T00:25:27",
    "interaction": "call",
    "direction": "in",
    "correspondent_id": "416-367-8573",
    "duration_sec": 323,
    "antenna_id": "703"
  },
  "events_in_window": [...],
  "coverage": {
    "total_events_in_window": 1,
    "events_with_antenna": 1,
    "missing_antenna_events": 0
  }
}
```

**Notes:** Returns `None` when no records exist in the time window (correct behavior).

---

#### `group_locations_at_time`

| Metric | Result |
|--------|--------|
| Executed without errors | Yes |
| Has `type` field | Yes (`"group_locations_at_time"`) |
| Subjective fields absent | Yes |
| Coordinates normalized | Yes |
| Events serialized | Yes |

**Sample Return Structure:**
```json
{
  "type": "group_locations_at_time",
  "target_ts": "2012-01-02T00:25:00",
  "window_minutes": 30,
  "users": {
    "Marcus Chen": {
      "support": {
        "closest_event_delta_sec": 27.0,
        "events_in_window": 1,
        "has_location": true
      },
      "location": {
        "antenna_id": "703",
        "coord": {"lat": 44.103724, "lon": -79.593519}
      },
      "closest_event": {...},
      "events_in_window": [...]
    },
    "Daniel Ng": {...},
    "Lauren Martinez": {...}
  },
  "colocation_summary": {
    "by_antenna": {"703": ["Marcus Chen", "Daniel Ng"]}
  }
}
```

**Notes:** Successfully detected co-location of Marcus Chen and Daniel Ng at tower 703.

---

#### `meeting_detection`

| Metric | Result |
|--------|--------|
| Executed without errors | Yes |
| Has `type` field | Yes (`"colocation_with_context"`) |
| Subjective fields absent | Yes |
| Coordinates normalized | Yes |
| Events serialized | Yes |

**Sample Return Structure:**
```json
{
  "type": "colocation_with_context",
  "colocation": {
    "antenna_id": "703",
    "coord": {"lat": 44.103724, "lon": -79.593519},
    "user_a_time": "2012-01-02T00:25:27",
    "user_b_time": "2012-01-02T00:13:43",
    "delta_seconds": 704.0
  },
  "activity_context": {
    "user_a": {
      "records_around_count": 1,
      "records_around": [...],
      "gap_window_minutes": 120
    },
    "user_b": {
      "records_around_count": 2,
      "records_around": [...],
      "gap_window_minutes": 120
    }
  },
  "parameters": {
    "colocation_window_minutes": 60,
    "gap_threshold_minutes": 120
  }
}
```

**Notes:** Found 95 co-locations between the two test users. The indicator correctly does NOT label these as "meetings" - it provides the raw co-location data with activity context.

---

#### `synchronized_silence`

| Metric | Result |
|--------|--------|
| Executed without errors | Yes |
| Has `type` field | Yes (`"synchronized_silence"`) |
| Subjective fields absent | Yes |
| Events serialized | Yes |

**Notes:** No synchronized silence periods were detected in the test data with the parameters used (180 min silence, 60 min overlap). This is expected for a demo dataset where users are active frequently. The indicator returns an empty list `[]` correctly.

---

### Phase 2: Medium Priority Indicators

#### `time_at_locations`

| Metric | Result |
|--------|--------|
| Executed without errors | Yes |
| Has `type` field | Yes (`"time_at_locations"`) |
| Subjective fields absent | Yes |
| Coordinates normalized | Yes |

**Sample Return Structure:**
```json
{
  "type": "time_at_locations",
  "locations": {
    "703": {
      "hit_count": 23,
      "estimated_hours": 11.5,
      "assumption_minutes_per_hit": 30,
      "coord": {"lat": 44.103724, "lon": -79.593519}
    },
    "706": {...},
    ...
  },
  "totals": {
    "total_records_with_location": 150,
    "unique_antennas": 7
  }
}
```

**Notes:** Correctly exposes the `assumption_minutes_per_hit` parameter used for time estimation.

---

#### `unusual_locations`

| Metric | Result |
|--------|--------|
| Executed without errors | Yes |
| Has `type` field | Yes (`"location_visit_histogram"`) |
| Subjective fields absent | Yes |
| Coordinates normalized | Yes |

**Sample Return Structure:**
```json
{
  "type": "location_visit_histogram",
  "all_locations": {
    "703": {
      "visit_count": 23,
      "coord": {"lat": 44.103724, "lon": -79.593519},
      "timestamps": ["2012-01-02T00:25:27", ...]
    },
    ...
  },
  "parameters": {
    "threshold_visits": 2
  },
  "filtered_below_threshold": []
}
```

**Notes:** With this dataset, no locations had <= 2 visits (all 7 towers were visited frequently). The indicator correctly returns the full histogram and an empty `filtered_below_threshold` list.

---

#### `activity_bursts`

| Metric | Result |
|--------|--------|
| Executed without errors | Yes |
| Has `type` field | Yes (`"activity_bursts"`) |
| Subjective fields absent | Yes |
| Events serialized | Yes |

**Sample Return Structure:**
```json
{
  "type": "activity_bursts",
  "parameters": {
    "window_minutes": 30,
    "threshold_multiplier": 3,
    "computed_avg_rate": 0.0556,
    "computed_threshold": 0.1667
  },
  "data_span": {
    "first_record": "2012-01-02T00:25:27",
    "last_record": "2012-02-27T06:14:06",
    "total_records": 150
  },
  "bursts": [
    {
      "start_ts": "2012-01-02T00:25:27",
      "end_ts": "2012-01-02T00:55:27",
      "count": 1,
      "contacts": ["416-367-8573"],
      "events": [...]
    },
    ...
  ]
}
```

**Notes:** Detected 119 bursts. The indicator correctly exposes `computed_avg_rate` and `computed_threshold` so investigators can understand how bursts were classified.

---

#### `inter_event_times`

| Metric | Result |
|--------|--------|
| Executed without errors | Yes |
| Has `type` field | Yes (`"inter_event_times"`) |
| Subjective fields absent | Yes |

**Sample Return Structure:**
```json
{
  "type": "inter_event_times",
  "deltas_seconds": [24417.0, 63515.0, 3221.0, ...],
  "summary": {
    "mean": 32612.87,
    "std": 50555.94,
    "min": 13.0,
    "max": 419739.0,
    "median": 7661.0,
    "count": 149
  }
}
```

**Notes:** Returns raw delta values plus summary statistics. The large max value (116+ hours) represents the longest gap between activities.

---

#### `activity_around_time`

| Metric | Result |
|--------|--------|
| Executed without errors | Yes |
| Has `type` field | Yes (`"activity_around_time"`) |
| Subjective fields absent | Yes |
| Events serialized | Yes |

**Sample Return Structure:**
```json
{
  "type": "activity_around_time",
  "user_id": "416-225-5506",
  "window": {
    "center_ts": "2012-01-15T14:30:00",
    "before_hours": 24,
    "after_hours": 24
  },
  "support": {
    "events_before": 4,
    "events_after": 5,
    "total_events": 9
  },
  "before": {
    "events": [...],
    "contacts": {"416-367-8573": 2, "416-471-3287": 2},
    "unique_contacts": 2
  },
  "after": {
    "events": [...],
    "contacts": {...},
    "unique_contacts": 2
  }
}
```

---

### Phase 3: Relationship Indicator

#### `relationship_strength`

| Metric | Result |
|--------|--------|
| Executed without errors | Yes |
| Has `type` field | Yes (`"relationship_strength"`) |
| Subjective fields absent | Yes |

**Sample Return Structure:**
```json
{
  "type": "relationship_strength",
  "user_id": "416-225-5506",
  "contacts": {
    "416-367-8573": {
      "score": 1.0,
      "count": 80,
      "duration_sec": 25993,
      "last_contact_ts": "2012-02-27T06:14:06",
      "score_components": {
        "count_norm": 1.0,
        "duration_norm": 1.0
      }
    },
    "416-471-3287": {
      "score": 0.786,
      "count": 62,
      "duration_sec": 20858,
      "last_contact_ts": "2012-02-27T00:06:19",
      "score_components": {
        "count_norm": 0.775,
        "duration_norm": 0.8024
      }
    },
    "416-356-7126": {...}
  },
  "methodology": {
    "count_weight": 0.6,
    "duration_weight": 0.4,
    "recency_weight": 0.0,
    "note": "Recency not implemented"
  }
}
```

**Notes:** Returns sorted contacts by score, exposes the weighting methodology, and includes raw `score_components` for transparency.

---

## 3. Renderer Test Results

All renderers in `render.py` were tested against their respective indicator output types.

### Summary Table

| Indicator | `render_evidence()` | `render_evidence_compact()` |
|-----------|--------------------|-----------------------------|
| `location_at_time` | Yes | Yes |
| `group_locations_at_time` | Yes | Yes |
| `colocation_with_context` | Yes | Yes |
| `synchronized_silence` | Yes | Yes |
| `activity_around_time` | Yes | Yes |
| `relationship_strength` | Yes | Yes |
| `activity_bursts` | Yes | Yes |
| `inter_event_times` | Yes | Yes |
| `time_at_locations` | Yes | Yes |
| `location_visit_histogram` | Yes | Yes |

### Sample Render Output

**`location_at_time`:**
```
User: 416-225-5506
Searched 60 min before and 60 min after 2012-01-02 00:25:27.
Found 1 phone records in that window; closest record is 0s from the target time.
Closest tower near that time: 703 (44.103724, -79.593519).
Location data present on 1 of 1 records in the window.
```
**Compact:** `416-225-5506 | tower 703 | closest delta 0s`

---

**`group_locations_at_time`:**
```
Target time: 2012-01-02 00:25:00
Search window: 30 minutes

Marcus Chen: Tower 703 (44.103724, -79.593519), closest record 27s from target.
Daniel Ng: Tower 703 (44.103724, -79.593519), closest record 27s from target.
Lauren Martinez: No location data within window.

Same tower at target time:
  703: Marcus Chen, Daniel Ng
```
**Compact:** `2/3 users with location at 2012-01-02 00:25:00`

---

**`relationship_strength`:**
```
User: 416-225-5506
Total contacts: 3
Scoring: 60% frequency, 40% call duration.

Top contacts by computed intensity score:
  416-367-8573: score 1.000 (80 interactions, 25993s calls)
  416-471-3287: score 0.786 (62 interactions, 20858s calls)
  416-356-7126: score 0.077 (8 interactions, 1126s calls)
```
**Compact:** `3 contacts ranked`

---

**`inter_event_times`:**
```
Analyzed 149 inter-event gaps.
Mean gap: 9h 3m 32s. Median: 2h 7m 8s.
Range: 13s to 116h 35m 39s.
```
**Compact:** `Inter-event times: mean 9h 3m 32s`

---

## 4. Issues Found

### No Critical Errors

All indicators executed successfully against the real Bandicoot dataset.

### Behavioral Notes

1. **`location_at_specific_time`** returns `None` when no records exist in the specified time window. This is correct behavior.

2. **`synchronized_silence`** returned empty results because the demo dataset has frequent activity with no long overlapping silence periods. Would need real investigation data or longer silence parameters to see meaningful results.

3. **`activity_bursts`** detected 119 bursts, but with a threshold of 0.17 records per 30-min window (3x average of 0.056), even single records qualify. The indicator correctly exposes the computed threshold for investigator review.

4. **Bandicoot Warning:** `4.23% of calls overlap the next call by more than 5 minutes` - This is a data quality note from Bandicoot, not an indicator issue.

---

## 5. Summary

### Overall Validation Status: PASS

| Criterion | Status |
|-----------|--------|
| All indicators have `type` field | PASS |
| No subjective fields (confidence, suspicion_score) | PASS |
| Coordinates normalized to `{lat, lon}` format | PASS |
| Events serialized with standard fields | PASS |
| Renderers produce plain-English output | PASS |
| No execution errors | PASS |

### Key Observations

1. **Data-First Design Working:** All indicators return structured data without embedded interpretations. The `type` field enables proper dispatch to renderers.

2. **Methodology Transparency:** Parameters like `assumption_minutes_per_hit`, `computed_threshold`, and `score_components` are correctly exposed in output.

3. **Serialization Consistent:** Event objects consistently use the format:
   ```json
   {
     "ts": "ISO timestamp",
     "interaction": "call|text",
     "direction": "in|out",
     "correspondent_id": "phone number",
     "duration_sec": number|null,
     "antenna_id": "tower ID"
   }
   ```

4. **Coordinate Normalization Working:** All location data uses `{"lat": float, "lon": float}` format.

5. **Renderer Coverage Complete:** All evidence types have corresponding renderers that produce clear, factual statements without subjective language.

### Disclaimer

This validation was performed on a demo dataset. The indicators' effectiveness for actual criminal investigations has not been tested with real law enforcement data.
