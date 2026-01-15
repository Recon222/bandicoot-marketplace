---
description: Compare behavioral indicators across multiple Bandicoot users
argument-hint: <user_ids...> <records_path> [antennas_path] [--output=comparison.csv]
allowed-tools: Bash, Write
---

# Bandicoot: Compare Users

Compare behavioral indicators across multiple users to identify patterns, outliers,
and group characteristics.

## Arguments

- `user_ids` (required): Space-separated list of user IDs, or `all` for all users in directory
- `records_path` (required): Directory containing records CSVs
- `antennas_path` (optional): Path to antennas CSV file
- `--output`: Output filename (default: `comparison.csv`)
- `--indicators`: Comma-separated list of specific indicators to compare
- `--groupby`: Aggregation level - `week`, `month`, `year`, or `none` (default: `week`)

## Execution

```python
import bandicoot as bc
import os
import csv

# Parse user IDs
user_ids_input = '{user_ids}'
records_path = '{records_path}'
antennas_path = '{antennas_path}' if '{antennas_path}' else None
output_file = '{output}' if '{output}' else 'comparison.csv'
groupby = '{groupby}' if '{groupby}' != 'none' else None
indicators_filter = '{indicators}'.split(',') if '{indicators}' else None

# Get list of users
if user_ids_input.lower() == 'all':
    # Find all CSV files in records directory
    user_ids = [f[:-4] for f in os.listdir(records_path) if f.endswith('.csv')]
    print(f"Found {len(user_ids)} users in {records_path}")
else:
    user_ids = user_ids_input.split()

print(f"Comparing {len(user_ids)} users...")
print(f"Users: {', '.join(user_ids[:10])}{'...' if len(user_ids) > 10 else ''}")

# Load all users
users = []
failed = []

for uid in user_ids:
    try:
        user = bc.read_csv(uid, records_path, antennas_path, describe=False, warnings=False)
        users.append(user)
        print(f"  Loaded: {uid} ({len(user.records)} records)")
    except Exception as e:
        failed.append((uid, str(e)))
        print(f"  FAILED: {uid} - {e}")

if failed:
    print(f"\nWarning: {len(failed)} users could not be loaded")

if not users:
    print("ERROR: No users loaded successfully!")
else:
    print(f"\n{'=' * 70}")
    print(f"Comparison Analysis: {len(users)} users")
    print('=' * 70)

    # Compute indicators for all users
    print("\nComputing indicators...")
    all_results = []

    for user in users:
        try:
            results = bc.utils.all(user, groupby=groupby, summary='extended', network=False)
            flat = bc.utils.flatten(results)
            flat['user_id'] = user.name
            all_results.append(flat)
        except Exception as e:
            print(f"  Warning: Could not compute indicators for {user.name}: {e}")

    if not all_results:
        print("ERROR: No results computed!")
    else:
        # Get all indicator keys
        all_keys = set()
        for r in all_results:
            all_keys.update(r.keys())

        # Filter indicators if specified
        if indicators_filter:
            all_keys = {k for k in all_keys if any(ind in k for ind in indicators_filter)}

        # Sort keys for consistent output
        sorted_keys = sorted(all_keys)

        # Ensure user_id is first
        if 'user_id' in sorted_keys:
            sorted_keys.remove('user_id')
        sorted_keys = ['user_id'] + sorted_keys

        # Statistical summary
        print(f"\n--- Summary Statistics Across Users ---")

        # Compute aggregate stats for key indicators
        key_indicators = [
            'active_days__allweek__allday',
            'number_of_contacts__allweek__allday__call',
            'number_of_contacts__allweek__allday__text',
            'call_duration__allweek__allday__call__mean',
            'percent_nocturnal__allweek__allday',
            'percent_initiated_conversations__allweek__allday',
            'response_delay_text__allweek__allday__mean',
            'number_of_antennas__allweek__allday',
            'radius_of_gyration__allweek__allday',
            'percent_at_home__allweek__allday'
        ]

        import statistics

        for indicator in key_indicators:
            values = []
            for r in all_results:
                v = r.get(indicator)
                if v is not None and v != '' and v != 'None':
                    try:
                        values.append(float(v))
                    except (ValueError, TypeError):
                        pass

            if len(values) >= 2:
                print(f"\n{indicator}:")
                print(f"  Mean: {statistics.mean(values):.4f}")
                print(f"  Std:  {statistics.stdev(values):.4f}")
                print(f"  Min:  {min(values):.4f}")
                print(f"  Max:  {max(values):.4f}")
                print(f"  N:    {len(values)}")
            elif len(values) == 1:
                print(f"\n{indicator}: {values[0]:.4f} (only 1 user)")

        # Identify outliers
        print(f"\n--- Outlier Detection ---")

        for indicator in key_indicators[:5]:  # Check first 5 indicators
            values = []
            user_values = []
            for r in all_results:
                v = r.get(indicator)
                if v is not None and v != '' and v != 'None':
                    try:
                        values.append(float(v))
                        user_values.append((r['user_id'], float(v)))
                    except (ValueError, TypeError):
                        pass

            if len(values) >= 3:
                mean = statistics.mean(values)
                std = statistics.stdev(values)

                if std > 0:
                    outliers = [(u, v) for u, v in user_values if abs(v - mean) > 2 * std]
                    if outliers:
                        print(f"\n{indicator} outliers (>2 std):")
                        for u, v in outliers:
                            direction = "high" if v > mean else "low"
                            z_score = (v - mean) / std
                            print(f"  {u}: {v:.4f} ({direction}, z={z_score:.2f})")

        # Export comparison table
        print(f"\n--- Exporting Results ---")

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted_keys, extrasaction='ignore')
            writer.writeheader()
            for r in all_results:
                writer.writerow(r)

        print(f"Comparison saved to: {output_file}")
        print(f"Columns: {len(sorted_keys)}")
        print(f"Rows: {len(all_results)}")

        # Also save JSON
        json_file = output_file.replace('.csv', '.json')
        import json
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"JSON saved to: {json_file}")

        print(f"\n{'=' * 70}")
        print("Comparison complete!")
```

## Examples

### Compare Specific Users

```
/bandicoot:compare user1 user2 user3 demo/data/ demo/data/antennas.csv
```

### Compare All Users in Directory

```
/bandicoot:compare all demo/data/
```

### Compare Specific Indicators

```
/bandicoot:compare all demo/data/ --indicators=call_duration,active_days
```

### Custom Output

```
/bandicoot:compare user1 user2 demo/data/ --output=my_comparison.csv --groupby=month
```

## Output Format

### CSV Output

The comparison CSV contains one row per user with all flattened indicators:

| user_id | active_days__allweek__allday | number_of_contacts__allweek__allday__call | ... |
|---------|------------------------------|-------------------------------------------|-----|
| user1   | 25                           | 15                                        | ... |
| user2   | 30                           | 22                                        | ... |

### JSON Output

```json
[
  {
    "user_id": "user1",
    "active_days__allweek__allday": 25,
    "number_of_contacts__allweek__allday__call": 15,
    ...
  },
  ...
]
```

## Comparison Metrics

The command computes and displays:

### Summary Statistics

For each key indicator across all users:
- Mean
- Standard deviation
- Min/Max
- Sample size

### Outlier Detection

Identifies users more than 2 standard deviations from the mean for key indicators.

### Key Indicators Compared

| Category | Indicators |
|----------|------------|
| Activity | active_days, number_of_records |
| Social | number_of_contacts, percent_initiated |
| Communication | call_duration, response_delay |
| Mobility | radius_of_gyration, percent_at_home |
| Temporal | percent_nocturnal |

## Use Cases

### Research Cohort Analysis

Compare behavioral patterns across study participants:

```
/bandicoot:compare participant_001 participant_002 ... data/records/
```

### Anomaly Detection

Identify unusual users in a dataset:

```
/bandicoot:compare all production/data/ --output=anomaly_check.csv
```

### Segmentation

Export data for clustering or segmentation analysis:

```
/bandicoot:compare all data/ --groupby=none --output=segmentation_input.csv
```

## Interpretation Guide

### High Variance Indicators

Large standard deviations suggest:
- Diverse user behaviors
- Potential data quality issues
- Natural population heterogeneity

### Outliers

Users identified as outliers may indicate:
- Unusual behavior patterns (legitimate)
- Data collection issues
- Different user types (business vs personal)

### Correlation Patterns

Look for correlated behaviors:
- High activity + many contacts = social hub
- Low mobility + regular calls = routine lifestyle
- High nocturnal + short calls = specific usage pattern

## Troubleshooting

### "No users loaded successfully"

- Check records_path contains CSV files
- Verify CSV format is correct
- Check file permissions

### "Only 1 user" for statistics

Statistics require at least 2 users. Add more users to compare.

### Missing indicators

Some users may lack certain indicators if:
- No location data (spatial indicators)
- No text messages (text-specific indicators)
- Single day of data (temporal indicators)
