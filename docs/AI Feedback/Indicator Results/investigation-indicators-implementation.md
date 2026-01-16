# Investigation Indicators Implementation Documentation

> A comprehensive walkthrough of the custom Bandicoot indicators developed for homicide and criminal investigations

---

## Overview

This document describes the implementation of specialized cell phone metadata analysis indicators built on top of Bandicoot, a Python library for analyzing Call Detail Records (CDRs). These indicators were designed specifically for investigating production order records obtained during criminal investigations, with a focus on extracting evidentiary insights about relationships, movements, and coordination between subjects.

The implementation spans six Python modules containing over 35 functions, organized by investigative purpose:

| Module | Purpose | Function Count |
|--------|---------|----------------|
| `relationship.py` | Quantify and rank connections between subjects | 6 |
| `temporal.py` | Analyze timing patterns and detect anomalies | 9 |
| `location.py` | Track single-user movement and locations | 7 |
| `colocation.py` | Detect when multiple subjects were together | 7 |
| `network.py` | Analyze collective network structure | 7 |
| `utils.py` | Shared utilities for ID mapping and filtering | 11 |

---

## Implementation Architecture

The implementation follows three distinct patterns based on the analytical requirements:

### Single-User Indicators

These analyze one person's behavior and follow standard Bandicoot patterns. Some use the `@grouping` decorator which enables automatic aggregation by time period (week, month), while others are standalone functions that accept a User object directly.

### Multi-User Indicators

These compare multiple subjects simultaneously and cannot use Bandicoot's standard decorators. They accept lists of User objects along with corresponding identifier lists, enabling cross-subject analysis for co-location detection and network mapping.

### Time-Bounded Queries

These answer specific investigative questions about a point in time, such as "Where was the subject at 3:00 PM on January 5th?" They do not aggregate over time periods and return precise answers for specific queries.

---

## Module Walkthroughs

### Relationship Analysis (`relationship.py`)

The relationship module helps investigators quickly identify who matters most to a subject. When you have thousands of phone records, you need to cut through the noise and find the key players.

The **relationship strength** indicator combines three factors into a composite score: how often they communicate (frequency), how long their calls last (duration), and how recently they talked (recency). The current implementation weights frequency at 60% and duration at 40%, producing a normalized score between 0 and 1. Contacts are automatically sorted from strongest to weakest relationship.

**Reciprocity scoring** reveals the balance of power in each relationship. A score of 1.0 means perfectly balanced communication - both parties call and text equally. A score approaching 0.0 indicates a one-sided relationship. This is particularly valuable for identifying pursuit or harassment patterns, or hierarchical relationships where one person is always receiving instructions.

The **initiation ratio** takes this further by tracking specifically who starts the conversations. If a subject always initiates contact with someone but never receives calls from them, that suggests they are the pursuer or requester in the relationship.

**First and last contact of day** indicators identify who the subject reaches out to at the bookends of their day. The first person contacted each morning and the last person contacted each night often reveals intimate relationships or urgent business connections. These indicators track frequency across all days in the dataset, showing which contacts consistently appear in these privileged positions.

The **contact interaction summary** provides a comprehensive dossier for each relationship: total interactions, breakdown of calls versus texts, incoming versus outgoing, total call duration, and the date range of the relationship. This gives investigators everything they need to characterize any particular connection.

### Temporal Pattern Analysis (`temporal.py`)

Temporal indicators help establish what "normal" looks like for a subject, making deviations around key dates stand out.

The **hourly activity profile** creates a 24-element distribution showing when the subject is typically active. If they normally go silent after midnight but suddenly have a flurry of activity at 2 AM on a specific date, that anomaly becomes immediately visible.

**Communication gaps** detection finds periods of unusual silence. The indicator accepts a configurable threshold (default 24 hours) and returns all gaps exceeding that duration with precise start and end times. Gaps could indicate incarceration, hospitalization, travel, phone switching, or deliberate avoidance of communication around a significant event.

In contrast, **activity bursts** find periods of unusually intense communication. Using a sliding window approach (default 30 minutes), the indicator flags periods where activity exceeds 3x the subject's average rate. Each burst includes the timestamp range, interaction count, and the list of contacts involved. This is crucial for detecting coordination - when multiple calls go out in rapid succession, something important is happening.

The **contact first/last appearance** indicators track when relationships begin and end in the data. New contacts appearing shortly before an event may be significant co-conspirators or victims. Contacts who suddenly disappear may indicate a falling out, a threat, or worse.

**Daily activity counts** provides a simple day-by-day breakdown useful for spotting anomalous days at a glance, while **inter-event times** calculates the statistical distribution of time between consecutive interactions, revealing whether the subject has regular communication patterns or erratic behavior.

For targeted analysis around a specific event, **activity around time** retrieves all communications within configurable windows before and after a target datetime, along with contact frequency breakdowns for each period. The companion function **first contact after time** answers the critical question: "Who did they call first after the incident?"

### Location Intelligence (`location.py`)

Location indicators reconstruct the subject's movements using cell tower (antenna) data embedded in their phone records.

The **location timeline** produces a chronological sequence of every antenna hit with timestamps, coordinates (when available), and the associated communication details. This is the foundation for movement reconstruction and alibi verification.

**Frequent locations ranked** identifies where the subject spends most of their time by counting antenna hits. The top locations typically correspond to home, work, and other regular haunts. Each location includes its percentage of total records and coordinates for mapping.

**Unusual locations** takes the opposite approach, finding antennas the subject visited only rarely (configurable threshold, default 2 or fewer visits). One-time visits to unusual locations around key dates are often investigatively significant - a single trip to a remote area the day before an incident, for example.

The **location transitions** indicator detects movement between different antennas, providing from/to antenna pairs with timestamps and calculated distances when coordinates are available. This reveals travel patterns and approximate speeds.

**Time at locations** provides a rough estimate of time spent at each location. Since cell records represent discrete events rather than continuous presence, this uses a heuristic where each record represents approximately 30 minutes of presence.

For point-in-time queries, **location at specific time** finds where the subject was at a target datetime within a configurable search window. It returns the closest matching record with a confidence level (high for records within 5 minutes, medium within 15, low otherwise). **Locations in time range** extends this to retrieve all location data within a specified period.

### Co-Location Analysis (`colocation.py`)

Co-location indicators are among the most valuable for investigations because they can prove two or more subjects were in the same place at the same time.

The **antenna overlap** function compares two users' records and finds instances where both hit the same cell tower within a configurable time window (default 30 minutes). Each overlap event includes both timestamps, the time difference between them, and antenna coordinates. This is critical evidence for establishing meetings, coordination, or presence at a crime scene.

**Travel pattern matching** goes further by detecting when two subjects traverse the same sequence of antennas within a time window. If Subject A moves from Tower 1 to Tower 2 to Tower 3, and Subject B follows the same path within an hour, that suggests they were traveling together or one was following the other.

**Meeting detection** combines co-location with communication analysis. The theory is simple: when people meet in person, they stop calling each other. The indicator finds antenna overlaps and examines communication activity around those times. Low communication activity during a co-location event increases confidence that a face-to-face meeting occurred.

**Multi-user colocation** extends the analysis to three or more subjects, finding times when multiple people from the investigation were at the same antenna simultaneously. Group meetings are often operationally significant.

**Proximity to location** answers the specific question: "Was this subject near a specific antenna (e.g., the crime scene) around a specific time?" It filters the subject's records to those matching the target antenna and optional time window.

The newest additions address coordinated behavior across the entire subject group:

**Synchronized silence** detects periods when multiple subjects all stop communicating simultaneously. This is suspicious because coordinated silence could indicate an in-person meeting (no need to call when together), coordinated criminal activity, or a deliberate communication blackout. The indicator calculates a "suspicion score" based on duration, participant ratio, and time of day (daytime silence is more suspicious than nighttime when people might be sleeping).

**Group locations at time** answers the comprehensive question: "Where was everyone at the time of the crime?" It returns each subject's location at a specific target datetime with confidence levels, enabling investigators to see at a glance who was where when something happened.

### Network Structure Analysis (`network.py`)

Network indicators analyze the collective relationships among all subjects in an investigation rather than focusing on individuals.

**Build communication matrix** constructs a directed graph of who called/texted whom, with edge weights representing communication volume. This is the foundation for more sophisticated network analysis.

**Degree centrality** identifies the most connected figures by counting unique contacts for each subject, distinguishing between in-network contacts (other subjects in the investigation) and out-of-network contacts. The most connected person is often a coordinator, leader, or key witness.

**Communication chains** detects A to B to C patterns where Subject A contacts Subject B, and then B contacts Subject C within a configurable time window. These chains reveal information flow and potential command structures - when information or instructions are passed along a chain rather than broadcast directly.

**Shared contacts** finds phone numbers that appear in multiple subjects' records. Common associates may be witnesses, intermediaries, or unidentified co-conspirators. The indicator counts how many subjects communicate with each external number and ranks them by "sharedness."

**Communication volume matrix** provides a detailed breakdown of communication between every pair, including total interactions, calls, texts, and total call duration. This symmetric view (treating A-to-B and B-to-A as the same relationship) reveals the strongest pairings in the network.

**Network timeline** shows how communication patterns evolve over time by bucketing activity into configurable periods (default 24 hours) and showing which pairs were active in each bucket. This can reveal when new connections form or existing ones go quiet.

**Identify bridges** finds subjects who connect otherwise separate groups - people who have exclusive contacts that no other subject communicates with. These bridges are key information brokers and their role in the network is often strategically important.

### Utilities (`utils.py`)

The utilities module provides essential support functions used throughout the other modules.

**ID mapping functions** convert between phone numbers and human-readable names. Production order data uses phone numbers as identifiers, but investigators need to see names. The `load_id_mapping` function reads from a CSV file containing phone number to name mappings, and `resolve_contacts` transforms indicator results to use names instead of numbers.

**Time window functions** help filter records to specific periods: `records_in_window` extracts all records between two datetimes, `records_around_time` retrieves records within a symmetric window around a target time, and `contacts_in_window` provides a frequency count of which contacts were communicated with during a period.

**Record filtering functions** provide targeted extraction by contact (`filter_by_contact`), direction (`filter_by_direction` for incoming/outgoing), and interaction type (`filter_by_interaction` for calls/texts).

**Formatting functions** handle common conversions: `parse_datetime` converts string representations to datetime objects, and `format_duration` converts raw seconds into human-readable strings like "2h 30m 15s".

---

## Indicator Reference

### Relationship Indicators

| Indicator | Function Signature | Returns |
|-----------|-------------------|---------|
| **Relationship Strength** | `relationship_strength(user)` | `dict` mapping correspondent_id to strength score (0-1), sorted descending |
| **Reciprocity Score** | `reciprocity_score(user)` | `dict` mapping correspondent_id to balance score (0=one-sided, 1=balanced) |
| **Initiation Ratio** | `initiation_ratio(user)` | `dict` mapping correspondent_id to ratio of subject-initiated contact (0-1) |
| **First Contact of Day** | `first_contact_of_day(user)` | `dict` mapping correspondent_id to count of days they were first contact |
| **Last Contact of Day** | `last_contact_of_day(user)` | `dict` mapping correspondent_id to count of days they were last contact |
| **Contact Interaction Summary** | `contact_interaction_summary(user)` | `dict` mapping correspondent_id to detailed stats (total, calls_in, calls_out, texts_in, texts_out, duration, first/last contact dates) |

### Temporal Indicators

| Indicator | Function Signature | Returns |
|-----------|-------------------|---------|
| **Hourly Activity Profile** | `hourly_activity_profile(records)` | `dict` mapping hour (0-23) to interaction count |
| **Communication Gaps** | `communication_gaps(user, threshold_hours=24)` | `list` of gaps with start, end, duration_hours |
| **Activity Bursts** | `activity_bursts(user, window_minutes=30, threshold_multiplier=3)` | `list` of bursts with start, end, count, contacts involved |
| **Contact First Appearance** | `contact_first_appearance(user)` | `dict` mapping correspondent_id to first contact datetime |
| **Contact Last Appearance** | `contact_last_appearance(user)` | `dict` mapping correspondent_id to last contact datetime |
| **Daily Activity Counts** | `daily_activity_counts(user)` | `dict` mapping date to interaction count |
| **Inter-Event Times** | `inter_event_times(records)` | `SummaryStats` object with mean, std, min, max, median of inter-event times in seconds |
| **Activity Around Time** | `activity_around_time(user, target_datetime, hours_before=24, hours_after=24)` | `dict` with before/after records, contact counts, totals |
| **First Contact After Time** | `first_contact_after_time(user, target_datetime)` | `dict` with correspondent_id, datetime, interaction type, direction, delay_seconds |

### Location Indicators

| Indicator | Function Signature | Returns |
|-----------|-------------------|---------|
| **Location Timeline** | `location_timeline(user)` | `list` of entries with datetime, antenna_id, coordinates, interaction, correspondent_id |
| **Frequent Locations Ranked** | `frequent_locations_ranked(user, top_n=10)` | `list` of locations with antenna_id, coordinates, count, percentage |
| **Unusual Locations** | `unusual_locations(positions, user, threshold_visits=2)` | `list` of unusual locations with antenna_id, coordinates, visit_count, timestamps |
| **Location Transitions** | `location_transitions(user)` | `list` of transitions with from/to antennas, times, duration_minutes, distance_km |
| **Time at Locations** | `time_at_locations(user)` | `dict` mapping antenna_id to estimated hours |
| **Location at Specific Time** | `location_at_specific_time(user, target_datetime, window_minutes=30)` | `dict` with antenna_id, coordinates, record_datetime, delta_seconds, confidence level |
| **Locations in Time Range** | `locations_in_time_range(user, start_datetime, end_datetime)` | `list` of location records within the time range |

### Co-Location Indicators

| Indicator | Function Signature | Returns |
|-----------|-------------------|---------|
| **Antenna Overlap** | `antenna_overlap(user_a, user_b, window_minutes=30)` | `list` of overlaps with antenna_id, user_a_time, user_b_time, delta_seconds, coordinates |
| **Travel Pattern Match** | `travel_pattern_match(user_a, user_b, window_minutes=60, min_sequence_length=2)` | `list` of matching transitions with from/to antennas and times for both users |
| **Meeting Detection** | `meeting_detection(user_a, user_b, colocation_window_minutes=30, gap_threshold_minutes=60)` | `list` of probable meetings with antenna, time, coordinates, activity level, confidence |
| **Multi-User Colocation** | `multi_user_colocation(users, window_minutes=30)` | `list` of events with antenna, user_indices, participant_count, time range |
| **Proximity to Location** | `proximity_to_location(user, target_antenna, target_datetime=None, window_minutes=60)` | `list` of records at target location/time |
| **Synchronized Silence** | `synchronized_silence(users, user_ids, min_silence_minutes=60, min_overlap_minutes=30, min_participants=None)` | `list` of silence events with start, end, duration, participants, suspicion_score |
| **Group Locations at Time** | `group_locations_at_time(users, user_ids, target_datetime, window_minutes=30)` | `dict` mapping user_id to location info with confidence level |

### Network Indicators

| Indicator | Function Signature | Returns |
|-----------|-------------------|---------|
| **Build Communication Matrix** | `build_communication_matrix(users, user_ids)` | `dict` mapping (from_id, to_id) tuples to communication count |
| **Degree Centrality** | `degree_centrality(users, user_ids)` | `dict` mapping user_id to contact counts (total, in-network, out-of-network) |
| **Communication Chains** | `communication_chains(users, user_ids, time_window_minutes=30)` | `list` of chains with sequence [A,B,C], times, total_time_seconds |
| **Shared Contacts** | `shared_contacts(users, user_ids, min_shared=2)` | `dict` mapping contact_id to list of user_ids who communicate with them |
| **Communication Volume Matrix** | `communication_volume_matrix(users, user_ids)` | `dict` mapping (user_a, user_b) tuples to volume stats (total, calls, texts, duration) |
| **Network Timeline** | `network_timeline(users, user_ids, time_bucket_hours=24)` | `list` of time buckets with active pairs and communication counts |
| **Identify Bridges** | `identify_bridges(users, user_ids)` | `list` of bridge users with exclusive_contacts, exclusive_count, total_contacts |

### Utility Functions

| Function | Signature | Returns |
|----------|-----------|---------|
| **Load ID Mapping** | `load_id_mapping(mapping_path)` | `dict` mapping phone_number to name |
| **Resolve Contact** | `resolve_contact(phone_number, mapping)` | `str` name or original phone number if not found |
| **Resolve Contacts** | `resolve_contacts(results, mapping)` | Results with phone numbers replaced by names |
| **Records in Window** | `records_in_window(user, start_datetime, end_datetime)` | `list` of Record objects |
| **Records Around Time** | `records_around_time(user, target_datetime, window_minutes=30)` | `list` of Record objects |
| **Contacts in Window** | `contacts_in_window(user, start_datetime, end_datetime)` | `dict` mapping correspondent_id to count |
| **Location at Time** | `location_at_time(user, target_datetime, window_minutes=30)` | `dict` with location info or None |
| **Filter by Contact** | `filter_by_contact(records, correspondent_id)` | `list` of Record objects |
| **Filter by Direction** | `filter_by_direction(records, direction)` | `list` of Record objects |
| **Filter by Interaction** | `filter_by_interaction(records, interaction)` | `list` of Record objects |
| **Parse Datetime** | `parse_datetime(datetime_str, fmt)` | `datetime` object |
| **Format Duration** | `format_duration(seconds)` | `str` human-readable duration |

---

## Usage Examples

### Basic Single-User Analysis

```python
import bandicoot as bc
from custom_indicators import relationship, temporal, location
from custom_indicators.utils import load_id_mapping, resolve_contacts

# Load a user
user = bc.read_csv('416-555-1234', 'data/', 'data/antennas.csv')

# Find their strongest relationships
strength = relationship.relationship_strength(user)

# Load ID mapping and convert to names
mapping = load_id_mapping('data/_ID_MAPPING.csv')
named_strength = resolve_contacts(strength, mapping)

print("Top 5 contacts by relationship strength:")
for contact, score in list(named_strength.items())[:5]:
    print(f"  {contact}: {score:.3f}")
```

### Analyzing Activity Around an Incident

```python
from datetime import datetime
from custom_indicators import temporal

# Define the time of interest
incident_time = datetime(2025, 6, 15, 14, 30, 0)

# What happened in the hours before and after?
activity = temporal.activity_around_time(user, incident_time,
                                          hours_before=6, hours_after=6)

print(f"Activity 6 hours before: {activity['count_before']} interactions")
print(f"Activity 6 hours after: {activity['count_after']} interactions")
print(f"First contact after incident: ")
first = temporal.first_contact_after_time(user, incident_time)
print(f"  {first['correspondent_id']} at {first['datetime']}")
```

### Multi-User Co-Location Analysis

```python
from custom_indicators import colocation

# Load multiple subjects
user_a = bc.read_csv('416-555-1234', 'data/', 'data/antennas.csv')
user_b = bc.read_csv('416-555-5678', 'data/', 'data/antennas.csv')

# Find times they were at the same antenna
overlaps = colocation.antenna_overlap(user_a, user_b, window_minutes=30)

print(f"Found {len(overlaps)} co-location events")
for event in overlaps[:5]:
    print(f"  {event['antenna_id']} - User A: {event['user_a_time']}, "
          f"User B: {event['user_b_time']} (delta: {event['delta_seconds']}s)")
```

### Network Analysis

```python
from custom_indicators import network

# Load all subjects in the investigation
users = [user_a, user_b, user_c, user_d]
user_ids = ['416-555-1234', '416-555-5678', '416-555-9012', '416-555-3456']

# Find the most connected person
centrality = network.degree_centrality(users, user_ids)
print("Network centrality (most connected first):")
for uid, stats in centrality.items():
    print(f"  {uid}: {stats['total_contacts']} contacts "
          f"({stats['in_network_contacts']} in-network)")

# Find shared contacts
shared = network.shared_contacts(users, user_ids, min_shared=2)
print(f"\nContacts shared by 2+ subjects: {len(shared)}")
```

---

## Implementation Notes

### Decorator Usage

The `@grouping` decorator from Bandicoot enables automatic time-based aggregation. When applied to a function, it allows callers to specify `groupby='week'` or `groupby='month'` to get distributions rather than single values. Only the `hourly_activity_profile` and `inter_event_times` indicators use this decorator because their output structure (24-hour profile, time distribution) benefits from period-based aggregation.

The `@spatial_grouping` decorator is used for the `unusual_locations` indicator, which requires access to both position data and the user object for antenna lookups.

Most indicators are implemented as standalone functions because their investigative use cases require precise single-value results rather than statistical distributions.

### Empty Data Handling

All indicators handle empty or minimal data gracefully, returning empty collections or None values rather than raising exceptions. This is important because production order data may have gaps or subjects with limited records.

### Performance Considerations

Multi-user indicators that compare records across subjects use indexing strategies to avoid O(n*m) comparisons where possible. The `antenna_overlap` function, for example, builds an index of records by antenna for the second user before iterating through the first user's records.

### Coordinate Handling

Antenna coordinates may be stored in different formats depending on how Bandicoot was configured. The location indicators handle both tuple/list formats and objects with latitude/longitude attributes.

---

## Relationship to the Implementation Plan

The implementation fully addresses all four phases outlined in the original plan:

**Phase 1 (Core Individual Indicators)**: All five priority indicators are implemented:
- relationship_strength
- contact_first_appearance
- location_at_time (as location_at_specific_time)
- activity_bursts
- communication_gaps

**Phase 2 (Location Analysis)**: All three indicators implemented:
- location_timeline
- frequent_locations (as frequent_locations_ranked)
- unusual_locations

**Phase 3 (Multi-User Analysis)**: All three indicators implemented:
- antenna_overlap
- communication_chains
- shared_contacts

**Phase 4 (Advanced Network)**: All three indicators implemented:
- degree_centrality
- pattern_change functionality (via activity_around_time and related functions)
- meeting_detection

Additionally, the implementation includes several indicators beyond the original plan, particularly the synchronized_silence and group_locations_at_time functions that enable powerful group behavior analysis.

---

*Documentation generated January 2026*
*Implementation: custom_indicators module v0.1.0*
