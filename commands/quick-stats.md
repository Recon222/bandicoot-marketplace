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

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Quick Stats Workflow

### 1. Load User

```
user = bc.read_csv('user_id', 'path/', describe=False)
```

### 2. Check Basic Properties

| Property | Information |
|----------|-------------|
| `len(user.records)` | Total records |
| `user.start_time` | First record |
| `user.end_time` | Last record |
| `user.has_call` | Has call data |
| `user.has_text` | Has text data |

### 3. Count Record Types

```
calls = sum(1 for r in user.records if r.interaction == 'call')
texts = sum(1 for r in user.records if r.interaction == 'text')
incoming = sum(1 for r in user.records if r.direction == 'in')
outgoing = sum(1 for r in user.records if r.direction == 'out')
```

### 4. Run Key Indicators (No Groupby)

| Command | Returns |
|---------|---------|
| `bc.individual.number_of_contacts(user, groupby=None)` | Unique contacts |
| `bc.individual.active_days(user, groupby=None)` | Days with activity |
| `bc.individual.call_duration(user, groupby=None)` | Call length stats |
| `bc.individual.percent_nocturnal(user, groupby=None)` | Night activity % |
| `bc.individual.percent_initiated_interactions(user, groupby=None)` | Outgoing % |
| `bc.spatial.percent_at_home(user, groupby=None)` | Home time % |
| `bc.spatial.radius_of_gyration(user, groupby=None)` | Mobility range |

## Output Categories

### Data Overview
- Total records, date range, observation period
- Calls vs texts count
- Incoming vs outgoing count

### Contacts
- Unique contacts (all, call-only, text-only)

### Activity
- Active days count
- Activity rate (% of observation days)

### Call Metrics
- Duration mean, std, min, max (seconds)

### Temporal Patterns
- Nocturnal activity %
- Calls initiated %

### Spatial (requires antennas)
- Antennas loaded count
- Home detected status
- Percent at home
- Radius of gyration (km)

### Data Quality
- Has calls/texts flags
- Home detection status
- Ignored records count

## Examples

Basic quick stats:
```
/bandicoot:quick-stats ego demo/data/
```

With spatial information:
```
/bandicoot:quick-stats ego demo/data/ demo/data/antennas.csv
```

## Use Cases

1. **Initial data exploration**: Understand new dataset quickly
2. **Data quality check**: Identify issues before full analysis
3. **Comparison baseline**: Get basic stats for multiple users
4. **Validation**: Verify data loaded correctly

## Notes

- Faster than full analysis (uses `groupby=None` for single values)
- Spatial stats only shown if antennas file provided
- For detailed analysis, use `/bandicoot:analyze`
