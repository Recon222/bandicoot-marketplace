# Homicide Investigation Indicators Plan

> Custom Bandicoot indicators designed for analyzing production order cell phone records in homicide investigations

---

## Executive Summary

This plan outlines custom indicators to extract investigative insights from cell phone metadata (CDRs) obtained via production orders. The indicators are organized into five categories based on investigative value:

1. **Relationship Analysis** - Quantify and rank connections between subjects
2. **Temporal Patterns** - Detect activity around key dates and behavioral anomalies
3. **Location Intelligence** - Analyze movement, co-location, and proximity
4. **Network Structure** - Identify central figures and communication chains
5. **Event Detection** - Find coordination, bursts, and pattern changes

---

## Reference Materials Glossary

### Documentation Files

| File | Location | Key Content |
|------|----------|-------------|
| `Writing_Custom_Indicators.md` | `bandicoot-FVU docs/Documetation/` | Decorator patterns, Record object properties, return types, helper functions |
| `BANDICOOT_INTERNALS.md` | `bandicoot-FVU docs/Documetation/` | Grouping engine, data models, caching, statistical pipeline |
| `How_Bandicoot_Determines_Home.md` | `bandicoot-FVU docs/Documetation/` | Home inference algorithm (nighttime 30-min binning) |
| `BANDICOOT_COMPLETE_REFERENCE.md` | `bandicoot-FVU docs/Documetation/` | Full API reference, all 40+ built-in indicators |
| `BANDICOOT_COOKBOOK.md` | `bandicoot-FVU docs/Documetation/` | Practical recipes, batch processing, network analysis |

### Source Files

| File | Location | Key Content |
|------|----------|-------------|
| `individual.py` | `bandicoot-FVU/bandicoot/` | 17 individual indicators - templates for communication analysis |
| `spatial.py` | `bandicoot-FVU/bandicoot/` | 6 spatial indicators - templates for location analysis |
| `helper/group.py` | `bandicoot-FVU/bandicoot/helper/` | `@grouping`, `@spatial_grouping` decorator implementations |
| `helper/maths.py` | `bandicoot-FVU/bandicoot/helper/` | `summary_stats`, `entropy`, `great_circle_distance` |
| `helper/tools.py` | `bandicoot-FVU/bandicoot/helper/` | `pairwise` iterator for consecutive records |
| `core.py` | `bandicoot-FVU/bandicoot/` | `User`, `Record`, `Position` data models |

### Key Patterns Learned

```python
# Standard imports for custom indicators
from bandicoot.helper.group import grouping, spatial_grouping
from bandicoot.helper.maths import summary_stats, entropy, great_circle_distance
from bandicoot.helper.tools import pairwise
from collections import Counter, defaultdict

# Record object properties
record.datetime          # datetime object
record.interaction       # 'call' or 'text'
record.direction         # 'in' or 'out'
record.correspondent_id  # contact identifier
record.call_duration     # seconds (None for texts)
record.position          # Position object

# Position object
position.antenna         # antenna ID
position._get_location(user)  # (lat, lon) tuple
```

---

## Category 1: Relationship Analysis

### 1.1 Relationship Strength Score

**Purpose:** Rank all contacts by communication intensity to identify closest associates

**Investigative Value:** Quickly identify who the subject communicates with most - potential witnesses, accomplices, or persons of interest

```python
@grouping
def relationship_strength(records):
    """
    Composite score combining frequency, duration, and recency.
    Returns per-contact scores ranked by strength.
    """
    # Factors: total interactions, total call time, days since last contact
    pass
```

**Output:** Dictionary of correspondent_id -> strength_score, sorted descending

---

### 1.2 Communication Reciprocity

**Purpose:** Measure balance of in/out communication per contact

**Investigative Value:** One-sided relationships (always calling, never receiving) may indicate pursuit, harassment, or hierarchical relationship (e.g., giving orders)

```python
@grouping
def reciprocity_score(records):
    """
    For each contact: min(in, out) / max(in, out)
    1.0 = perfectly balanced, 0.0 = completely one-sided
    """
    pass
```

---

### 1.3 Who Initiates First

**Purpose:** Track who initiates contact in each relationship

**Investigative Value:** The person who always initiates may be the pursuer, coordinator, or dependent party

```python
@grouping
def initiation_ratio(records):
    """
    Per-contact ratio of subject-initiated vs contact-initiated interactions.
    """
    pass
```

---

### 1.4 First/Last Contact of Day

**Purpose:** Identify who the subject contacts first thing in the morning and last thing at night

**Investigative Value:** Often reveals closest personal relationships (partner, family) or urgent business contacts

```python
@grouping(user_kwd=True)
def first_contact_of_day(records, user):
    """
    Most frequent first contact each day.
    """
    pass

@grouping(user_kwd=True)
def last_contact_of_day(records, user):
    """
    Most frequent last contact each day.
    """
    pass
```

---

## Category 2: Temporal Pattern Analysis

### 2.1 Activity Timeline

**Purpose:** Create hour-by-hour activity profile

**Investigative Value:** Establishes routine - deviations from pattern around key dates are significant

```python
@grouping
def hourly_activity_profile(records):
    """
    Returns 24-element array of activity counts per hour.
    """
    pass
```

---

### 2.2 Communication Gaps

**Purpose:** Detect unusual periods of silence

**Investigative Value:** Gaps could indicate incarceration, hospitalization, travel, phone switching, or significant events

```python
@grouping
def communication_gaps(records, threshold_hours=24):
    """
    Returns list of gaps longer than threshold with start/end times.
    """
    pass
```

---

### 2.3 Activity Burst Detection

**Purpose:** Identify periods of unusually high activity

**Investigative Value:** Bursts around key times may indicate coordination, panic, or crisis response

```python
@grouping
def activity_bursts(records, window_minutes=30, threshold_multiplier=3):
    """
    Detect periods where activity exceeds 3x the average rate.
    Returns list of burst periods with timestamps.
    """
    pass
```

---

### 2.4 Pattern Change Detection

**Purpose:** Compare behavior before/after a specific date

**Investigative Value:** Behavioral shifts around date of offence - new contacts appearing, old contacts disappearing, changed communication patterns

```python
@grouping
def pattern_change(records, pivot_date):
    """
    Compare metrics before and after pivot_date.
    Returns dict of changed metrics with before/after values.
    """
    pass
```

---

### 2.5 New Contact Emergence

**Purpose:** Identify when new contacts first appear in the record

**Investigative Value:** New contacts shortly before an event may be significant

```python
@grouping
def contact_first_appearance(records):
    """
    Returns dict of correspondent_id -> first_contact_datetime.
    """
    pass
```

---

### 2.6 Contact Disappearance

**Purpose:** Identify contacts who stop communicating

**Investigative Value:** Sudden cessation of contact with someone may indicate fallout, threat, or victim

```python
@grouping
def contact_last_appearance(records):
    """
    Returns dict of correspondent_id -> last_contact_datetime.
    """
    pass
```

---

## Category 3: Location Intelligence

### 3.1 Location Timeline

**Purpose:** Chronological list of antenna hits with timestamps

**Investigative Value:** Reconstruct movement for alibi verification, proximity to crime scene

```python
@spatial_grouping(user_kwd=True)
def location_timeline(positions, user):
    """
    Returns chronological list of (timestamp, antenna_id, lat, lon).
    """
    pass
```

---

### 3.2 Frequent Locations

**Purpose:** Rank locations by time spent

**Investigative Value:** Identify home, work, and other significant locations

```python
@spatial_grouping(user_kwd=True)
def frequent_locations(positions, user, top_n=5):
    """
    Returns top N locations with time percentage and coordinates.
    """
    pass
```

---

### 3.3 Location at Specific Time

**Purpose:** Determine location at a specific datetime

**Investigative Value:** Where was the subject at the time of the offence?

```python
def location_at_time(user, target_datetime, window_minutes=30):
    """
    Returns location(s) within window of target time.
    Not a grouped indicator - specific query.
    """
    pass
```

---

### 3.4 Unusual Location Visits

**Purpose:** Detect visits to locations outside normal pattern

**Investigative Value:** One-time visits to unusual locations around key dates

```python
@spatial_grouping(user_kwd=True)
def unusual_locations(positions, user, threshold_visits=2):
    """
    Locations visited fewer than threshold times.
    Returns list with timestamps.
    """
    pass
```

---

### 3.5 Travel Patterns

**Purpose:** Detect movement between antennas

**Investigative Value:** Identify travel routes, meeting patterns

```python
@spatial_grouping(user_kwd=True)
def travel_sequences(positions, user):
    """
    Returns list of location transitions with timestamps.
    """
    pass
```

---

## Category 4: Co-Location Analysis (Multi-User)

> These indicators require analyzing multiple users together

### 4.1 Antenna Overlap Detection

**Purpose:** Find times when two subjects hit the same antenna within a time window

**Investigative Value:** Proves two people were in the same location - critical for establishing meetings, coordination

```python
def antenna_overlap(user_a, user_b, window_minutes=30):
    """
    Returns list of overlapping events with timestamps and antenna.
    Not a @grouping indicator - cross-user analysis.
    """
    pass
```

---

### 4.2 Travel Pattern Matching

**Purpose:** Detect when two subjects traverse the same sequence of antennas

**Investigative Value:** Following someone, traveling together

```python
def travel_pattern_match(user_a, user_b, window_minutes=60):
    """
    Find matching antenna sequences between users.
    """
    pass
```

---

### 4.3 Meeting Detection

**Purpose:** Identify likely meetings between subjects based on co-location + communication cessation

**Investigative Value:** When people meet in person, they often stop calling/texting each other

```python
def meeting_detection(user_a, user_b):
    """
    Find co-location events where both users have communication gaps.
    """
    pass
```

---

## Category 5: Network Structure Analysis

> These indicators analyze the collective network of all subjects

### 5.1 Network Centrality

**Purpose:** Identify the most connected/central figures

**Investigative Value:** Find the hub - likely leader, coordinator, or key witness

```python
def degree_centrality(users):
    """
    Count connections per user, rank by most connected.
    """
    pass

def betweenness_centrality(users):
    """
    Identify bridges between otherwise separate groups.
    """
    pass
```

---

### 5.2 Communication Chains

**Purpose:** Detect A -> B -> C communication patterns

**Investigative Value:** Information flow, command structure, intermediaries

```python
def communication_chains(users, time_window_minutes=30):
    """
    Find sequences where A contacts B, then B contacts C.
    """
    pass
```

---

### 5.3 Subgroup Detection

**Purpose:** Identify clusters within the network

**Investigative Value:** Find tight-knit groups, cliques, separate factions

```python
def detect_subgroups(users):
    """
    Cluster users by communication density.
    """
    pass
```

---

### 5.4 Shared Contacts

**Purpose:** Find contacts that multiple subjects have in common

**Investigative Value:** Common associates may be witnesses or co-conspirators

```python
def shared_contacts(users):
    """
    Returns contacts appearing in multiple users' records.
    """
    pass
```

---

## Implementation Priority

### Phase 1: Core Individual Indicators (Immediate Value)

| # | Indicator | Reason |
|---|-----------|--------|
| 1 | `relationship_strength` | Quickly identify key contacts |
| 2 | `contact_first_appearance` | Find new contacts before event |
| 3 | `location_at_time` | Alibi verification |
| 4 | `activity_bursts` | Detect coordination |
| 5 | `communication_gaps` | Identify significant periods |

### Phase 2: Location Analysis

| # | Indicator | Reason |
|---|-----------|--------|
| 6 | `location_timeline` | Movement reconstruction |
| 7 | `frequent_locations` | Home/work identification |
| 8 | `unusual_locations` | One-time significant visits |

### Phase 3: Multi-User Analysis

| # | Indicator | Reason |
|---|-----------|--------|
| 9 | `antenna_overlap` | Co-location proof |
| 10 | `communication_chains` | Information flow |
| 11 | `shared_contacts` | Network mapping |

### Phase 4: Advanced Network

| # | Indicator | Reason |
|---|-----------|--------|
| 12 | `degree_centrality` | Identify hub |
| 13 | `pattern_change` | Before/after analysis |
| 14 | `meeting_detection` | In-person meetings |

---

## Technical Considerations

### Data Requirements

Your dataset has all required fields:
- `datetime` - timestamps present
- `interaction` - call/text present
- `direction` - in/out present
- `correspondent_id` - phone numbers (can map to names via `_ID_MAPPING.csv`)
- `call_duration` - present for calls
- `antenna_id` - present, maps to `antennas.csv` for coordinates

### Three Types of Indicators

| Type | Pattern | Use Case |
|------|---------|----------|
| **Single-User** | `@grouping` decorator | Individual behavioral analysis |
| **Multi-User** | Standalone functions | Co-location, network analysis |
| **Time-Bounded** | Standalone functions | Point-in-time queries |

#### Single-User Pattern (Standard Bandicoot)

```python
from bandicoot.helper.group import grouping

@grouping
def relationship_strength(records):
    """Operates on one user's records."""
    pass
```

#### Multi-User Pattern (Custom)

```python
def antenna_overlap(user_a, user_b, window_minutes=30):
    """
    Accepts multiple User objects - cannot use @grouping decorator.
    """
    overlaps = []
    for rec_a in user_a.records:
        for rec_b in user_b.records:
            # Compare records across users
            pass
    return overlaps
```

#### Time-Bounded Pattern (Specific Queries)

```python
def location_at_specific_time(user, target_datetime, window_minutes=30):
    """
    Point-in-time query - not grouped by week/month.
    """
    window = timedelta(minutes=window_minutes)
    return [r for r in user.records
            if target_datetime - window <= r.datetime <= target_datetime + window]
```

### Module Structure

Indicators are organized in `bandicoot-plugin/custom_indicators/`:

```
custom_indicators/
├── __init__.py           # Exports all modules
├── utils.py              # ID mapping, time windows, formatting
├── relationship.py       # Relationship strength, reciprocity
├── temporal.py           # Gaps, bursts, pattern changes
├── location.py           # Single-user location analysis
├── colocation.py         # Multi-user co-location detection
└── network.py            # Network centrality, chains, subgroups
```

### ID Mapping Integration

Always resolve phone numbers to names for human-readable output:

```python
from custom_indicators.utils import load_id_mapping, resolve_contacts

mapping = load_id_mapping('data/_ID_MAPPING.csv')
results = relationship_strength(user, groupby=None)
named_results = resolve_contacts(results, mapping)
```

### Testing Approach

Each indicator should be tested:
1. With `groupby=None` (single result) - for single-user indicators
2. With `groupby='week'` (distribution) - if applicable
3. With empty records (handle gracefully)
4. Multi-user indicators tested with 2+ users
5. Time-bounded queries tested with specific datetimes

### Integration with Plugin

New indicators are:
1. Written by the `investigation-indicator-developer` agent
2. Tested inline via `conda run -n bandicoot`
3. Saved to the `custom_indicators/` module
4. Called from slash commands or skills

**Agent Reference:**
- `bandicoot-indicator-developer` - General Bandicoot indicator development
- `investigation-indicator-developer` - Homicide investigation specific indicators

---

## Implementation Status

### Implemented (Ready to Use)

| Module | Indicators |
|--------|------------|
| `relationship.py` | `relationship_strength`, `reciprocity_score`, `initiation_ratio`, `first_contact_of_day`, `last_contact_of_day`, `contact_interaction_summary` |
| `temporal.py` | `hourly_activity_profile`, `communication_gaps`, `activity_bursts`, `contact_first_appearance`, `contact_last_appearance`, `daily_activity_counts`, `inter_event_times`, `activity_around_time`, `first_contact_after_time` |
| `location.py` | `location_timeline`, `frequent_locations_ranked`, `unusual_locations`, `location_transitions`, `time_at_locations`, `location_at_specific_time`, `locations_in_time_range` |
| `colocation.py` | `antenna_overlap`, `travel_pattern_match`, `meeting_detection`, `multi_user_colocation`, `proximity_to_location` |
| `network.py` | `build_communication_matrix`, `degree_centrality`, `communication_chains`, `shared_contacts`, `communication_volume_matrix`, `network_timeline`, `identify_bridges` |
| `utils.py` | `load_id_mapping`, `resolve_contacts`, `records_in_window`, `records_around_time`, `contacts_in_window`, `location_at_time`, `filter_by_*`, `parse_datetime`, `format_duration` |

---

## Next Steps

1. Review this plan and prioritize based on current case needs
2. Test implemented indicators against your dataset
3. Refine indicators based on investigative feedback
4. Create slash commands for frequently-used indicators

---

*Plan created for Bandicoot MCP Plugin - Homicide Investigation Use Case*
*Date: January 2026*
*Updated: Added module structure and implementation status*
