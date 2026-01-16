---
description: Export Bandicoot analysis results to CSV or JSON
argument-hint: <user_id> <records_path> [antennas_path] --format=csv|json [--output=filename]
allowed-tools: Bash, Write
---

# Bandicoot: Export Results

Export analysis results to CSV or JSON format.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing the records CSV
- `antennas_path` (optional): Path to antennas CSV file
- `--format`: Output format - `csv` (default), `json`, or `both`
- `--output`: Output filename (default: `{user_id}_results.{format}`)
- `--groupby`: Aggregation level - `week` (default), `month`, `year`, or `none`
- `--flatten`: If set, flatten nested structure (CSV is always flattened)

## Execution

Execute the following Python code inline using `conda run -n bandicoot python -c "..."`.
Do not save this as a separate script file.

```python
import bandicoot as bc
import json

user_id = '{user_id}'
records_path = '{records_path}'
antennas_path = '{antennas_path}' if '{antennas_path}' else None
output_format = '{format}' or 'csv'
output_base = '{output}' if '{output}' else f'{user_id}_results'
groupby = '{groupby}' if '{groupby}' != 'none' else None

# Load and analyze
print(f"Loading user: {user_id}")
user = bc.read_csv(user_id, records_path, antennas_path, describe=False, warnings=True)
print(f"Loaded {len(user.records)} records")

print(f"Computing indicators (groupby={groupby})...")
results = bc.utils.all(user, groupby=groupby)

# Export based on format
if output_format in ('csv', 'both'):
    csv_file = f"{output_base}.csv" if not output_base.endswith('.csv') else output_base
    bc.to_csv(results, csv_file)
    print(f"Exported to CSV: {csv_file}")

    # Show sample of flattened keys
    flat = bc.utils.flatten(results)
    print(f"\nCSV contains {len(flat)} columns. Sample keys:")
    for key in list(flat.keys())[:10]:
        print(f"  - {key}")
    if len(flat) > 10:
        print(f"  ... and {len(flat) - 10} more columns")

if output_format in ('json', 'both'):
    json_file = f"{output_base}.json" if not output_base.endswith('.json') else output_base
    bc.to_json(results, json_file)
    print(f"Exported to JSON: {json_file}")

    # Show structure preview
    print(f"\nJSON structure preview:")
    print(f"  name: {results.get('name')}")
    print(f"  reporting: {len(results.get('reporting', {}))} fields")

    # List indicator keys
    indicator_keys = [k for k in results.keys() if k not in ('name', 'reporting', 'attributes')]
    print(f"  indicators: {len(indicator_keys)} computed")
    for key in indicator_keys[:5]:
        print(f"    - {key}")
    if len(indicator_keys) > 5:
        print(f"    ... and {len(indicator_keys) - 5} more")

print(f"\nExport complete!")
```

## Examples

### Export to CSV (Default)

```
/bandicoot:export ego demo/data/ demo/data/antennas.csv --format=csv
```

### Export to JSON

```
/bandicoot:export ego demo/data/ demo/data/antennas.csv --format=json
```

### Export Both Formats

```
/bandicoot:export ego demo/data/ demo/data/antennas.csv --format=both
```

### Custom Output Filename

```
/bandicoot:export ego demo/data/ --format=csv --output=my_analysis
```

### Without Grouping

```
/bandicoot:export ego demo/data/ --format=json --groupby=none
```

## Output Formats

### CSV Format

The CSV export uses flattened keys with `__` separator:

```csv
name,active_days__allweek__allday__callandtext__mean,call_duration__allweek__allday__call__mean__mean,...
ego,5.5,3776.7,...
```

Key naming convention:
```
{indicator}__{week_split}__{day_split}__{interaction}__{stat}__{inner_stat}
```

Example keys:
- `active_days__allweek__allday__callandtext__mean`
- `call_duration__allweek__allday__call__mean__mean`
- `radius_of_gyration__allweek__allday__mean`

### JSON Format

The JSON export preserves the nested structure:

```json
{
    "ego": {
        "name": "ego",
        "reporting": {
            "version": "0.6.0",
            "number_of_records": 314,
            ...
        },
        "active_days": {
            "allweek": {
                "allday": {
                    "callandtext": {
                        "mean": 5.5,
                        "std": 1.2
                    }
                }
            }
        },
        ...
    }
}
```

## Working with Exported Data

### Loading CSV in Python

```python
import pandas as pd
df = pd.read_csv('user_results.csv')
print(df.columns.tolist())
```

### Loading JSON in Python

```python
import json
with open('user_results.json') as f:
    data = json.load(f)
# Access nested values
active_days = data['ego']['active_days']['allweek']['allday']['callandtext']['mean']
```

### Comparing Multiple Users

Export multiple users and combine:

```python
import bandicoot as bc

users = ['ego', 'user1', 'user2']
results = []

for uid in users:
    user = bc.read_csv(uid, 'demo/data/', 'demo/data/antennas.csv')
    results.append(bc.utils.all(user))

# Export all to single CSV
bc.to_csv(results, 'comparison.csv')
```

## Notes

- CSV always flattens the nested structure
- JSON preserves the original nested structure
- Both formats include all computed indicators and reporting metadata
- Use `--groupby=none` for single values instead of distributions
