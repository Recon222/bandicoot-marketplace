---
description: Get quick summary statistics from Bandicoot user data
argument-hint: <user_id> <records_path> [antennas_path]
allowed-tools: Bash
---

# Bandicoot: Quick Statistics

Get a fast overview of key metrics without running full analysis.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing the records CSV
- `antennas_path` (optional): Path to antennas CSV file

## Execution

```python
import bandicoot as bc

# Load user with minimal output
user = bc.read_csv(
    '{user_id}',
    '{records_path}',
    '{antennas_path}' if '{antennas_path}' else None,
    describe=False,
    warnings=False
)

print(f"{'=' * 50}")
print(f"Quick Stats for {user.name}")
print('=' * 50)

# Basic counts
print(f"\n--- Data Overview ---")
print(f"Total records: {len(user.records)}")
print(f"Date range: {user.start_time} to {user.end_time}")

if user.start_time and user.end_time:
    days = (user.end_time - user.start_time).days
    print(f"Observation period: {days} days")

# Record types
calls = sum(1 for r in user.records if r.interaction == 'call')
texts = sum(1 for r in user.records if r.interaction == 'text')
print(f"Calls: {calls}")
print(f"Texts: {texts}")

# Direction
incoming = sum(1 for r in user.records if r.direction == 'in')
outgoing = sum(1 for r in user.records if r.direction == 'out')
print(f"Incoming: {incoming}")
print(f"Outgoing: {outgoing}")

# Contacts
print(f"\n--- Contacts ---")
contacts = bc.individual.number_of_contacts(user, groupby=None)
contact_count = contacts.get('allweek', {}).get('allday', {}).get('callandtext', 0)
print(f"Unique contacts (all): {contact_count}")

call_contacts = contacts.get('allweek', {}).get('allday', {}).get('call', 0)
text_contacts = contacts.get('allweek', {}).get('allday', {}).get('text', 0)
print(f"Call contacts: {call_contacts}")
print(f"Text contacts: {text_contacts}")

# Activity
print(f"\n--- Activity ---")
active = bc.individual.active_days(user, groupby=None)
active_days = active.get('allweek', {}).get('allday', {}).get('callandtext', 0)
print(f"Active days: {active_days}")

if days > 0:
    print(f"Activity rate: {active_days/days*100:.1f}% of days")

# Call metrics
if user.has_call:
    print(f"\n--- Call Metrics ---")
    duration = bc.individual.call_duration(user, groupby=None)
    dur_stats = duration.get('allweek', {}).get('allday', {}).get('call', {})
    if dur_stats:
        print(f"Call duration mean: {dur_stats.get('mean', 0):.1f} seconds")
        print(f"Call duration std: {dur_stats.get('std', 0):.1f} seconds")
        print(f"Call duration min: {dur_stats.get('min', 0):.0f} seconds")
        print(f"Call duration max: {dur_stats.get('max', 0):.0f} seconds")

# Temporal
print(f"\n--- Temporal Patterns ---")
nocturnal = bc.individual.percent_nocturnal(user, groupby=None)
noct_pct = nocturnal.get('allweek', {}).get('allday', {}).get('callandtext', 0)
print(f"Nocturnal activity: {noct_pct*100:.1f}%")

initiated = bc.individual.percent_initiated_interactions(user, groupby=None)
init_pct = initiated.get('allweek', {}).get('allday', {}).get('call', 0)
print(f"Calls initiated: {init_pct*100:.1f}%")

# Spatial (if antennas available)
if user.has_antennas:
    print(f"\n--- Spatial ---")
    print(f"Antennas loaded: {len(user.antennas)}")
    print(f"Has home: {user.has_home}")

    if user.has_home:
        home_pct = bc.spatial.percent_at_home(user, groupby=None)
        at_home = home_pct.get('allweek', {}).get('allday', 0)
        if at_home:
            print(f"Percent at home: {at_home*100:.1f}%")

        rog = bc.spatial.radius_of_gyration(user, groupby=None)
        radius = rog.get('allweek', {}).get('allday', None)
        if radius:
            print(f"Radius of gyration: {radius:.2f} km")

# Data quality
print(f"\n--- Data Quality ---")
print(f"Has calls: {user.has_call}")
print(f"Has texts: {user.has_text}")
print(f"Has home: {user.has_home}")

if user.ignored_records and user.ignored_records.get('all', 0) > 0:
    print(f"Ignored records: {user.ignored_records['all']}")
    for key, count in user.ignored_records.items():
        if key != 'all' and count > 0:
            print(f"  - {key}: {count}")
else:
    print("No records ignored")

print(f"\n{'=' * 50}")
print("Quick stats complete!")
print("\nFor full analysis, run: /bandicoot:analyze")
```

## Examples

### Basic Quick Stats

```
/bandicoot:quick-stats ego demo/data/
```

### With Spatial Information

```
/bandicoot:quick-stats ego demo/data/ demo/data/antennas.csv
```

## Output Explanation

### Data Overview

- **Total records**: All call and text records loaded
- **Date range**: First to last record timestamp
- **Observation period**: Days between first and last record
- **Calls/Texts**: Count of each interaction type
- **Incoming/Outgoing**: Count by direction

### Contacts

- **Unique contacts**: Number of distinct correspondent_ids
- **Call/Text contacts**: Contacts by interaction type

### Activity

- **Active days**: Days with at least one interaction
- **Activity rate**: Percentage of observation days with activity

### Call Metrics

- **Duration mean**: Average call length in seconds
- **Duration std**: Standard deviation (variability)
- **Duration min/max**: Shortest and longest calls

### Temporal Patterns

- **Nocturnal activity**: Percentage during 7pm-7am
- **Calls initiated**: Percentage of calls that are outgoing

### Spatial

- **Antennas loaded**: Count of known tower locations
- **Has home**: Whether home location was detected
- **Percent at home**: Time spent at home location
- **Radius of gyration**: Typical mobility range in km

### Data Quality

- **Has calls/texts**: Whether these record types exist
- **Has home**: Whether home could be detected
- **Ignored records**: Records filtered due to invalid data

## Use Cases

1. **Initial data exploration**: Quickly understand a new dataset
2. **Data quality check**: Identify issues before full analysis
3. **Comparison baseline**: Get basic stats for multiple users
4. **Validation**: Verify data loaded correctly

## Notes

- Quick stats runs faster than full analysis (no aggregation)
- All indicators use `groupby=None` for single values
- Spatial stats only shown if antennas file is provided
- For detailed analysis, use `/bandicoot:analyze`
