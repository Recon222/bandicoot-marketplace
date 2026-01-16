---
description: Run complete Bandicoot analysis on user phone records
argument-hint: <user_id> <records_path> [antennas_path] [--groupby=week] [--output=results.csv]
allowed-tools: Bash, Read, Write
---

# Bandicoot: Complete Analysis

Run all Bandicoot indicators on user phone records and export results.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing the records CSV
- `antennas_path` (optional): Path to antennas CSV file
- `--groupby`: Aggregation level - `week` (default), `month`, `year`, or `none`
- `--summary`: Summary type - `default`, `extended`, or `none`
- `--output`: Output filename (default: `{user_id}_analysis.csv`)
- `--split-week`: Separate weekday/weekend analysis
- `--split-day`: Separate day/night analysis

## Execution

Execute the following Python code inline using `conda run -n bandicoot python -c "..."`.

**Note**: This code demonstrates the analysis workflow. Execute it inline
or via the REPL - do not save it as a separate script file.

### Step 1: Run Complete Analysis

```python
import bandicoot as bc
import os

# Configuration from arguments
user_id = '{user_id}'
records_path = '{records_path}'
antennas_path = '{antennas_path}' if '{antennas_path}' else None
groupby = '{groupby}' if '{groupby}' != 'none' else None
summary = '{summary}' if '{summary}' != 'none' else None
output_csv = '{output}' if '{output}' else f'{user_id}_analysis.csv'
output_json = output_csv.replace('.csv', '.json')

# Load user
print(f"Loading user: {user_id}")
user = bc.read_csv(
    user_id,
    records_path,
    antennas_path,
    describe=False,
    warnings=True
)

print(f"Loaded {len(user.records)} records")
print(f"Date range: {user.start_time} to {user.end_time}")

# Compute all indicators
print(f"\nRunning analysis (groupby={groupby}, summary={summary})...")
results = bc.utils.all(
    user,
    groupby=groupby,
    summary=summary,
    split_week={split_week},
    split_day={split_day}
)

# Export results
bc.to_csv(results, output_csv, warnings=False)
bc.to_json(results, output_json, warnings=False)
print(f"\nResults saved to:")
print(f"  CSV: {output_csv}")
print(f"  JSON: {output_json}")

# Print key findings summary
print(f"\n{'=' * 50}")
print(f"Analysis Summary for {user.name}")
print('=' * 50)

# Reporting metadata
reporting = results.get('reporting', {})
print(f"\nData Overview:")
print(f"  Records: {reporting.get('number_of_records', 'N/A')}")
print(f"  Time bins (weeks): {reporting.get('bins_with_data', 'N/A')}")
print(f"  Has calls: {reporting.get('has_call', 'N/A')}")
print(f"  Has texts: {reporting.get('has_text', 'N/A')}")
print(f"  Has home: {reporting.get('has_home', 'N/A')}")

# Key individual indicators
print(f"\nCommunication Patterns:")
ad = results.get('active_days', {})
if ad:
    val = ad.get('allweek', {}).get('allday', {}).get('callandtext', {})
    if isinstance(val, dict):
        print(f"  Active days: mean={val.get('mean', 'N/A'):.2f}, std={val.get('std', 'N/A'):.2f}")
    else:
        print(f"  Active days: {val}")

nc = results.get('number_of_contacts', {})
if nc:
    val = nc.get('allweek', {}).get('allday', {}).get('call', {})
    if isinstance(val, dict):
        print(f"  Contacts (call): mean={val.get('mean', 'N/A'):.2f}")
    else:
        print(f"  Contacts (call): {val}")

cd = results.get('call_duration', {})
if cd:
    val = cd.get('allweek', {}).get('allday', {}).get('call', {}).get('mean', {})
    if isinstance(val, dict):
        print(f"  Call duration: mean={val.get('mean', 'N/A'):.1f}s")
    else:
        print(f"  Call duration: {val}s")

pn = results.get('percent_nocturnal', {})
if pn:
    val = pn.get('allweek', {}).get('allday', {}).get('callandtext', {})
    if isinstance(val, dict):
        print(f"  Nocturnal activity: {val.get('mean', 0)*100:.1f}%")
    else:
        print(f"  Nocturnal activity: {val*100:.1f}%" if val else "N/A")

# Key spatial indicators
print(f"\nMobility Patterns:")
rog = results.get('radius_of_gyration', {})
if rog:
    val = rog.get('allweek', {}).get('allday', {})
    if isinstance(val, dict):
        print(f"  Radius of gyration: {val.get('mean', 'N/A'):.2f} km")
    else:
        print(f"  Radius of gyration: {val:.2f} km" if val else "N/A")

pah = results.get('percent_at_home', {})
if pah:
    val = pah.get('allweek', {}).get('allday', {})
    if isinstance(val, dict):
        print(f"  Percent at home: {val.get('mean', 0)*100:.1f}%")
    else:
        print(f"  Percent at home: {val*100:.1f}%" if val else "N/A")

na = results.get('number_of_antennas', {})
if na:
    val = na.get('allweek', {}).get('allday', {})
    if isinstance(val, dict):
        print(f"  Unique locations: mean={val.get('mean', 'N/A'):.1f}")
    else:
        print(f"  Unique locations: {val}")

# Data quality notes
if reporting.get('percent_records_missing_location', 0) > 0:
    print(f"\nData Quality Notes:")
    print(f"  Records missing location: {reporting.get('percent_records_missing_location', 0)*100:.1f}%")

if user.ignored_records and user.ignored_records.get('all', 0) > 0:
    print(f"  Ignored records: {user.ignored_records['all']}")

print(f"\n{'=' * 50}")
print("Analysis complete!")
```

### Step 2: Summarize Output

After the script runs, summarize:

1. **Files created**: List the CSV and JSON output files
2. **Key metrics**: Highlight the most important indicators
3. **Data quality**: Note any warnings or issues
4. **Next steps**: Suggest visualization or comparison commands

## Output Structure

The CSV output contains flattened indicators with naming convention:
`{indicator}__{time_split}__{day_split}__{interaction}__{stat}`

Example columns:
- `active_days__allweek__allday__callandtext__mean`
- `call_duration__allweek__allday__call__mean__mean`
- `percent_nocturnal__allweek__allday__callandtext__mean`
- `radius_of_gyration__allweek__allday__mean`

## Examples

### Basic Analysis (Weekly Aggregation)

```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv
```

### Monthly Aggregation

```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --groupby=month
```

### No Aggregation (Raw Values)

```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --groupby=none
```

### Extended Statistics

```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --summary=extended
```

### Custom Output File

```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --output=my_results.csv
```

### With Day/Night Split

```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --split-day
```

## Expected Results (Demo Data)

For the ego user in demo/data/, expect approximately:

| Indicator | Expected Value |
|-----------|----------------|
| active_days mean | ~5.5 |
| number_of_contacts (call) mean | ~5.14 |
| call_duration mean mean | ~3776 seconds |
| radius_of_gyration mean | ~1.45 km |

## Troubleshooting

### Analysis Fails to Start
- Verify file paths are correct
- Check Bandicoot environment is available
- Ensure records file is valid CSV format

### Many None Values in Output
- Check that required data is present (calls for call indicators, locations for spatial)
- Verify datetime format in CSV
- Check for sufficient data (some indicators need multiple records)

### Spatial Indicators Missing
- Antennas path must be provided and valid
- Check antenna_id matching between records and antennas files
