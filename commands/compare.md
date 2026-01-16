---
description: Compare behavioral indicators across multiple Bandicoot users
argument-hint: <user_ids...> <records_path> [antennas_path] [--output=comparison.csv]
allowed-tools: Bash
---

# Bandicoot: Compare Users

Compare behavioral indicators across multiple users to identify patterns, outliers, and group characteristics.

## Arguments

- `user_ids` (required): Space-separated list of user IDs, or `all` for all users in directory
- `records_path` (required): Directory containing records CSVs
- `antennas_path` (optional): Path to antennas CSV file
- `--output`: Output filename (default: `comparison.csv`)
- `--indicators`: Comma-separated list of specific indicators to compare
- `--groupby`: Aggregation level - `week`, `month`, `year`, or `none` (default: `week`)

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Comparison Workflow

### 1. Find Users

```
import os
user_ids = [f[:-4] for f in os.listdir('path/') if f.endswith('.csv')]
```

Or use `all` to process all CSV files in directory.

### 2. Load and Analyze Each User

```
users = []
for uid in user_ids:
    user = bc.read_csv(uid, 'path/', describe=False)
    users.append(user)
```

### 3. Compute Indicators

```
results = []
for user in users:
    result = bc.utils.all(user, groupby='week')
    flat = bc.utils.flatten(result)
    flat['user_id'] = user.name
    results.append(flat)
```

### 4. Export Comparison

```
bc.to_csv(results, 'comparison.csv')
```

## Key Commands

| Command | Purpose |
|---------|---------|
| `bc.read_csv(uid, path, describe=False)` | Load user quietly |
| `bc.utils.all(user, groupby='week')` | Compute all indicators |
| `bc.utils.flatten(result)` | Flatten nested dict |
| `bc.to_csv(results, path)` | Export list of results |

## Key Indicators for Comparison

| Category | Indicators |
|----------|------------|
| Activity | `active_days`, `number_of_records` |
| Social | `number_of_contacts`, `percent_initiated` |
| Communication | `call_duration`, `response_delay` |
| Mobility | `radius_of_gyration`, `percent_at_home` |
| Temporal | `percent_nocturnal` |

## Output Format

### CSV Output

One row per user with flattened indicators:

| user_id | active_days__allweek__allday | number_of_contacts__allweek__allday__call | ... |
|---------|------------------------------|-------------------------------------------|-----|
| user1   | 25                           | 15                                        | ... |
| user2   | 30                           | 22                                        | ... |

## Examples

Compare specific users:
```
/bandicoot:compare user1 user2 user3 demo/data/ demo/data/antennas.csv
```

Compare all users in directory:
```
/bandicoot:compare all demo/data/
```

Compare specific indicators:
```
/bandicoot:compare all demo/data/ --indicators=call_duration,active_days
```

Custom output:
```
/bandicoot:compare user1 user2 demo/data/ --output=my_comparison.csv --groupby=month
```

## Interpretation Guide

### High Variance Indicators

Large standard deviations suggest:
- Diverse user behaviors
- Potential data quality issues
- Natural population heterogeneity

### Outliers

Users far from mean may indicate:
- Unusual behavior patterns (legitimate)
- Data collection issues
- Different user types (business vs personal)

### Correlation Patterns

Look for correlated behaviors:
- High activity + many contacts = social hub
- Low mobility + regular calls = routine lifestyle
- High nocturnal + short calls = specific usage pattern

## Use Cases

### Research Cohort Analysis

Compare behavioral patterns across study participants.

### Anomaly Detection

Identify unusual users in a dataset.

### Segmentation

Export data for clustering or segmentation analysis.

## Troubleshooting

**"No users loaded successfully"**
- Check records_path contains CSV files
- Verify CSV format is correct
- Check file permissions

**"Only 1 user" for statistics**
- Statistics require at least 2 users

**Missing indicators**
- Some users may lack certain indicators if no location data, no texts, or insufficient data
