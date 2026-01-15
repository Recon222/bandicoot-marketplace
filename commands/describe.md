---
description: Display detailed description of loaded Bandicoot user data
argument-hint: <user_id> <records_path> [antennas_path]
allowed-tools: Bash
---

# Bandicoot: Describe User

Display a comprehensive description of user data, including data quality
information and capabilities.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing the records CSV
- `antennas_path` (optional): Path to antennas CSV file
- `--network`: Also load and describe network data

## Execution

```python
import bandicoot as bc
from collections import Counter
from datetime import datetime

user_id = '{user_id}'
records_path = '{records_path}'
antennas_path = '{antennas_path}' if '{antennas_path}' else None
load_network = {network_flag}

# Load user
user = bc.read_csv(
    user_id,
    records_path,
    antennas_path,
    network=load_network,
    describe=False,
    warnings=True
)

print(f"{'=' * 60}")
print(f"User Description: {user.name}")
print('=' * 60)

# Basic information
print(f"\n--- Basic Information ---")
print(f"User ID: {user.name}")
print(f"Records path: {records_path}")
if antennas_path:
    print(f"Antennas path: {antennas_path}")

# Record statistics
print(f"\n--- Record Statistics ---")
print(f"Total records: {len(user.records)}")

if user.records:
    print(f"Date range: {user.start_time} to {user.end_time}")
    duration = (user.end_time - user.start_time).days
    print(f"Duration: {duration} days")

    # Breakdown by type
    calls = sum(1 for r in user.records if r.interaction == 'call')
    texts = sum(1 for r in user.records if r.interaction == 'text')
    print(f"Calls: {calls} ({calls/len(user.records)*100:.1f}%)")
    print(f"Texts: {texts} ({texts/len(user.records)*100:.1f}%)")

    # Breakdown by direction
    incoming = sum(1 for r in user.records if r.direction == 'in')
    outgoing = sum(1 for r in user.records if r.direction == 'out')
    print(f"Incoming: {incoming} ({incoming/len(user.records)*100:.1f}%)")
    print(f"Outgoing: {outgoing} ({outgoing/len(user.records)*100:.1f}%)")

# Contact analysis
print(f"\n--- Contact Analysis ---")
contacts = Counter(r.correspondent_id for r in user.records)
print(f"Unique contacts: {len(contacts)}")
print(f"Most active contacts:")
for contact, count in contacts.most_common(5):
    print(f"  {contact}: {count} interactions")
if len(contacts) > 5:
    print(f"  ... and {len(contacts) - 5} more contacts")

# Temporal patterns
print(f"\n--- Temporal Patterns ---")
if user.records:
    # Daily distribution
    days = Counter(r.datetime.weekday() for r in user.records)
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    print("Records by day of week:")
    for i, name in enumerate(day_names):
        count = days.get(i, 0)
        bar = '#' * int(count / max(days.values()) * 20) if days.values() else ''
        print(f"  {name}: {count:4d} {bar}")

    # Hourly distribution
    hours = Counter(r.datetime.hour for r in user.records)
    peak_hour = max(hours, key=hours.get) if hours else None
    if peak_hour is not None:
        print(f"Peak hour: {peak_hour}:00 ({hours[peak_hour]} records)")

    # Night/day
    night_count = sum(1 for r in user.records
                      if r.datetime.hour >= 19 or r.datetime.hour < 7)
    print(f"Night (7pm-7am): {night_count} ({night_count/len(user.records)*100:.1f}%)")

# Spatial information
print(f"\n--- Spatial Information ---")
print(f"Antennas loaded: {len(user.antennas)}")
print(f"Has home: {user.has_home}")

if user.home:
    print(f"Home location: {user.home}")

# Count records with location
records_with_loc = sum(1 for r in user.records
                       if r.position.antenna or r.position.location)
if user.records:
    print(f"Records with location: {records_with_loc} ({records_with_loc/len(user.records)*100:.1f}%)")

if user.antennas:
    # Show sample antennas
    print("Sample antennas:")
    for aid, (lat, lon) in list(user.antennas.items())[:3]:
        print(f"  {aid}: ({lat:.4f}, {lon:.4f})")
    if len(user.antennas) > 3:
        print(f"  ... and {len(user.antennas) - 3} more")

# Network information (if loaded)
if user.has_network:
    print(f"\n--- Network Information ---")
    print(f"Network size: {len(user.network)}")
    loaded = sum(1 for v in user.network.values() if v is not None)
    print(f"Correspondents loaded: {loaded}")
    print(f"Correspondents missing: {len(user.network) - loaded}")
    print(f"Out-of-network calls: {user.percent_outofnetwork_calls:.1%}")
    print(f"Out-of-network texts: {user.percent_outofnetwork_texts:.1%}")

# Data quality
print(f"\n--- Data Quality ---")
print(f"Has calls: {user.has_call}")
print(f"Has texts: {user.has_text}")
print(f"Has home: {user.has_home}")
print(f"Has network: {user.has_network}")
print(f"Has attributes: {user.has_attributes}")
print(f"Has recharges: {user.has_recharges}")

if user.ignored_records:
    total_ignored = user.ignored_records.get('all', 0)
    if total_ignored > 0:
        print(f"\nIgnored records: {total_ignored}")
        for key, count in user.ignored_records.items():
            if key != 'all' and count > 0:
                print(f"  - {key}: {count}")
    else:
        print("\nNo records ignored - data quality good")

# Configuration
print(f"\n--- Configuration ---")
print(f"Night start: {user.night_start}")
print(f"Night end: {user.night_end}")
print(f"Weekend days: {user.weekend}")

# Capabilities summary
print(f"\n--- Analysis Capabilities ---")
capabilities = []
if user.has_call or user.has_text:
    capabilities.append("Individual indicators")
if user.has_antennas and user.has_home:
    capabilities.append("Spatial indicators (full)")
elif user.has_antennas:
    capabilities.append("Spatial indicators (limited - no home)")
if user.has_network:
    capabilities.append("Network indicators")
if user.has_recharges:
    capabilities.append("Recharge indicators")

if capabilities:
    print("Available analyses:")
    for cap in capabilities:
        print(f"  [x] {cap}")
else:
    print("  No analyses available - check data quality")

print(f"\n{'=' * 60}")

# Bandicoot's built-in describe
print("\n--- Bandicoot Native Description ---")
user.describe()
```

## Examples

### Basic Description

```
/bandicoot:describe ego demo/data/
```

### With Spatial Data

```
/bandicoot:describe ego demo/data/ demo/data/antennas.csv
```

### With Network

```
/bandicoot:describe ego demo/data/ demo/data/antennas.csv --network
```

## Output Sections

### Basic Information
- User identifier and file paths

### Record Statistics
- Total record count
- Date range and duration
- Breakdown by type (call/text) and direction (in/out)

### Contact Analysis
- Number of unique contacts
- Most frequently contacted individuals

### Temporal Patterns
- Distribution of activity across days of week
- Peak activity hours
- Day vs night distribution

### Spatial Information
- Number of antenna locations loaded
- Home location detection status
- Records with location data

### Network Information
(Only if `--network` flag used)
- Network size and loading status
- Out-of-network percentages

### Data Quality
- Available data types
- Records ignored during loading
- Reasons for ignored records

### Configuration
- Night time definition
- Weekend definition

### Analysis Capabilities
- Summary of which analyses can be performed based on available data

## Use Cases

1. **Data exploration**: Understand new dataset before analysis
2. **Quality assessment**: Identify data issues early
3. **Documentation**: Generate dataset summary for reports
4. **Troubleshooting**: Diagnose why certain indicators are missing
