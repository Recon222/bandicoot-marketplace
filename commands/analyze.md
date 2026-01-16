---
description: Run complete Bandicoot analysis on user phone records
argument-hint: <user_id> <records_path> [antennas_path] [--groupby=week] [--output=results.csv]
allowed-tools: Bash, Read
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

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Workflow

### 1. Load User Data

| Command | Purpose |
|---------|---------|
| `user = bc.read_csv('user_id', 'path/')` | Load without antennas |
| `user = bc.read_csv('user_id', 'path/', 'antennas.csv')` | Load with antennas |

### 2. Run Complete Analysis

| Command | Returns |
|---------|---------|
| `bc.utils.all(user)` | All indicators, default grouping |
| `bc.utils.all(user, groupby='week')` | Weekly aggregation |
| `bc.utils.all(user, groupby='month')` | Monthly aggregation |
| `bc.utils.all(user, groupby=None)` | No aggregation (raw) |
| `bc.utils.all(user, summary='extended')` | Extended statistics |
| `bc.utils.all(user, split_week=True)` | Separate weekday/weekend |
| `bc.utils.all(user, split_day=True)` | Separate day/night |

### 3. Export Results

| Command | Output |
|---------|--------|
| `bc.to_csv(results, 'output.csv')` | Flattened CSV format |
| `bc.to_json(results, 'output.json')` | Nested JSON format |

### 4. Check Key Properties

After loading, check:
- `len(user.records)` - number of records
- `user.start_time` / `user.end_time` - date range
- `user.has_call` / `user.has_text` - data types present

After analysis, check in results:
- `results['reporting']['number_of_records']`
- `results['reporting']['has_call']`
- `results['reporting']['has_text']`

## Key Indicators in Results

| Path in Results | Meaning |
|-----------------|---------|
| `active_days.allweek.allday.callandtext` | Days with activity |
| `number_of_contacts.allweek.allday.call` | Unique call contacts |
| `call_duration.allweek.allday.call.mean` | Average call duration |
| `percent_nocturnal.allweek.allday.callandtext` | Nighttime activity % |
| `radius_of_gyration.allweek.allday` | Mobility range (km) |
| `percent_at_home.allweek.allday` | Time at home % |

## Output Structure

CSV output has flattened column names:
`{indicator}__{time_split}__{day_split}__{interaction}__{stat}`

Example columns:
- `active_days__allweek__allday__callandtext__mean`
- `call_duration__allweek__allday__call__mean__mean`
- `radius_of_gyration__allweek__allday__mean`

## Examples

Basic analysis:
```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv
```

Monthly aggregation:
```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --groupby=month
```

Extended statistics:
```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --summary=extended
```

## Expected Results (Demo Data)

| Indicator | Expected Value |
|-----------|----------------|
| active_days mean | ~5.5 |
| number_of_contacts (call) mean | ~5.14 |
| call_duration mean mean | ~3776 seconds |
| radius_of_gyration mean | ~1.45 km |

## Troubleshooting

**Analysis fails to start**
- Verify file paths are correct
- Check Bandicoot environment is available
- Ensure records file is valid CSV format

**Many None values in output**
- Check that required data is present (calls for call indicators, locations for spatial)
- Verify datetime format in CSV
- Check for sufficient data (some indicators need multiple records)

**Spatial indicators missing**
- Antennas path must be provided and valid
- Check antenna_id matching between records and antennas files
