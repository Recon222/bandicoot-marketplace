---
description: Display detailed description of loaded Bandicoot user data
argument-hint: <user_id> <records_path> [antennas_path]
allowed-tools: Bash
---

# Bandicoot: Describe User

Display a comprehensive description of user data, including data quality and capabilities.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing the records CSV
- `antennas_path` (optional): Path to antennas CSV file
- `--network`: Also load and describe network data

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Key Commands

### Load with Description

```
user = bc.read_csv('user_id', 'path/', describe=True)
```

The `describe=True` parameter automatically prints Bandicoot's built-in summary.

### Built-in Describe

```
user.describe()
```

Prints native Bandicoot description after loading.

## User Properties to Check

### Basic Information

| Property | Information |
|----------|-------------|
| `user.name` | User identifier |
| `len(user.records)` | Total records |
| `user.start_time` | First record timestamp |
| `user.end_time` | Last record timestamp |

### Data Types

| Property | Meaning |
|----------|---------|
| `user.has_call` | Has call records |
| `user.has_text` | Has text records |
| `user.has_home` | Home location detected |
| `user.has_antennas` | Antenna data loaded |
| `user.has_network` | Network data loaded |
| `user.has_recharges` | Recharge data loaded |
| `user.has_attributes` | User attributes loaded |

### Spatial Data

| Property | Information |
|----------|-------------|
| `len(user.antennas)` | Number of antennas |
| `user.home` | Home antenna location |

### Network Data (if loaded)

| Property | Information |
|----------|-------------|
| `len(user.network)` | Number of correspondents |
| `user.percent_outofnetwork_calls` | Calls to unknown contacts |
| `user.percent_outofnetwork_texts` | Texts to unknown contacts |

### Configuration

| Property | Default |
|----------|---------|
| `user.night_start` | 19 (7pm) |
| `user.night_end` | 7 (7am) |
| `user.weekend` | [6, 7] (Sat, Sun) |

### Data Quality

| Property | Information |
|----------|-------------|
| `user.ignored_records` | Dict of ignored record counts |
| `user.ignored_records['all']` | Total ignored |

## Computed Statistics

Use inline Python to compute:

```
# Record breakdown
calls = sum(1 for r in user.records if r.interaction == 'call')
texts = sum(1 for r in user.records if r.interaction == 'text')
incoming = sum(1 for r in user.records if r.direction == 'in')
outgoing = sum(1 for r in user.records if r.direction == 'out')

# Unique contacts
from collections import Counter
contacts = Counter(r.correspondent_id for r in user.records)
len(contacts)  # unique count
contacts.most_common(5)  # top 5

# Records with location
records_with_loc = sum(1 for r in user.records if r.position.antenna)
```

## Analysis Capabilities

Based on loaded data:

| Data Available | Capabilities |
|----------------|--------------|
| Calls or texts | Individual indicators |
| Antennas + home | Full spatial indicators |
| Antennas only | Limited spatial (no home) |
| Network | Network indicators |
| Recharges | Recharge indicators |

## Examples

Basic description:
```
/bandicoot:describe ego demo/data/
```

With spatial data:
```
/bandicoot:describe ego demo/data/ demo/data/antennas.csv
```

With network:
```
/bandicoot:describe ego demo/data/ demo/data/antennas.csv --network
```

## Use Cases

1. **Data exploration**: Understand new dataset before analysis
2. **Quality assessment**: Identify data issues early
3. **Documentation**: Generate dataset summary for reports
4. **Troubleshooting**: Diagnose why certain indicators are missing
