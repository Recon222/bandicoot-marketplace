---
description: Batch process multiple Bandicoot users with progress tracking
argument-hint: <records_path> [antennas_path] [--output-dir=results/] [--summary]
allowed-tools: Bash
---

# Bandicoot: Batch Processing

Process all users in a directory with progress tracking, error handling, and consolidated output.

## Arguments

- `records_path` (required): Directory containing records CSVs
- `antennas_path` (optional): Path to antennas CSV file
- `--output-dir`: Directory for results (default: `bandicoot_results/`)
- `--groupby`: Aggregation level - `week`, `month`, `year` (default: `week`)
- `--format`: Output format - `csv`, `json`, or `both` (default: `both`)
- `--network`: Include network analysis (default: `false`)
- `--continue`: Resume from previous run, skip processed users
- `--summary`: Generate summary statistics file

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Batch Processing Workflow

### 1. Find Users

```
import os
user_files = [f for f in os.listdir('path/') if f.endswith('.csv')]
user_ids = [f[:-4] for f in user_files]
```

### 2. Process Each User

```
results = []
for uid in user_ids:
    try:
        user = bc.read_csv(uid, 'path/', describe=False, warnings=False)
        result = bc.utils.all(user, groupby='week')
        bc.to_csv(result, f'output/{uid}_results.csv')
        results.append(result)
        print(f'OK: {uid}')
    except Exception as e:
        print(f'FAIL: {uid} - {e}')
```

### 3. Export Combined Results

```
bc.to_csv(results, 'output/_all_users_summary.csv')
```

## Key Commands

| Command | Purpose |
|---------|---------|
| `bc.read_csv(uid, path, describe=False, warnings=False)` | Load quietly |
| `bc.utils.all(user, groupby='week')` | Compute all indicators |
| `bc.utils.flatten(result)` | Flatten nested dict |
| `bc.to_csv(result, path)` | Export single result |
| `bc.to_csv(results, path)` | Export list (one row per user) |

## Output Structure

```
output_dir/
  user001_results.csv       # Individual user results
  user001_results.json
  user002_results.csv
  ...
  _all_users_summary.csv    # Combined (if --summary)
  _aggregate_stats.json     # Statistics (if --summary)
  _errors.json              # Error log (if failures)
```

## Examples

Basic batch processing:
```
/bandicoot:batch demo/data/ demo/data/antennas.csv
```

With summary statistics:
```
/bandicoot:batch data/records/ data/antennas.csv --summary=true --output-dir=results/
```

Continue previous run:
```
/bandicoot:batch data/records/ --continue=true --output-dir=results/
```

JSON only output:
```
/bandicoot:batch data/records/ --format=json --output-dir=json_results/
```

With network analysis:
```
/bandicoot:batch data/records/ --network=true --output-dir=network_results/
```

## Summary Files

### _all_users_summary.csv

One row per user with all indicators:

| user_id | record_count | active_days__allweek__allday | ... |
|---------|--------------|------------------------------|-----|
| user001 | 1234         | 25                           | ... |

### _aggregate_stats.json

```json
{
  "meta": {
    "users_processed": 100,
    "users_failed": 2,
    "processing_time_seconds": 45.2
  },
  "indicators": {
    "active_days__allweek__allday": {
      "mean": 22.5,
      "std": 8.3,
      "min": 1,
      "max": 31
    }
  }
}
```

## Performance Tips

For large datasets (1000+ users):

1. **Disable network analysis** (faster): `--network=false`
2. **Use continue mode** for resumability: `--continue=true`
3. **Process in batches** by subdirectory

### Memory Management

- Delete user objects after processing: `del user`
- Use simpler groupby: `none` instead of `week`
- Process in smaller batches

## Error Handling

- Per-user errors logged but processing continues
- All failures saved to `_errors.json`
- Continue mode skips already processed users

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid datetime" | Wrong date format | Fix CSV format |
| "No records" | Empty file | Remove empty files |
| "Memory error" | Too much data | Smaller batches |
| "File not found" | Missing antenna | Check paths |

## Progress Output Format

```
[1/100] OK: user001 (1234 records)
[2/100] OK: user002 (567 records)
[3/100] FAIL: user003 - Invalid datetime format...
[4/100] SKIP: user004 (no records)
    Progress: 10/100 | Rate: 2.3/sec | ETA: 39s
```
