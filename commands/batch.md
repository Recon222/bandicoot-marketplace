---
description: Batch process multiple Bandicoot users with progress tracking
argument-hint: <records_path> [antennas_path] [--output-dir=results/] [--parallel=4]
allowed-tools: Bash, Write
---

# Bandicoot: Batch Processing

Process all users in a directory with progress tracking, error handling, and
consolidated output.

## Arguments

- `records_path` (required): Directory containing records CSVs
- `antennas_path` (optional): Path to antennas CSV file
- `--output-dir`: Directory for results (default: `bandicoot_results/`)
- `--groupby`: Aggregation level - `week`, `month`, `year` (default: `week`)
- `--format`: Output format - `csv`, `json`, or `both` (default: `both`)
- `--network`: Include network analysis - `true` or `false` (default: `false`)
- `--continue`: Continue from previous run, skip already processed users
- `--summary`: Generate summary statistics file

## Execution

```python
import bandicoot as bc
import os
import csv
import json
import time
from datetime import datetime

records_path = '{records_path}'
antennas_path = '{antennas_path}' if '{antennas_path}' else None
output_dir = '{output_dir}' if '{output_dir}' else 'bandicoot_results'
groupby = '{groupby}' if '{groupby}' else 'week'
output_format = '{format}' if '{format}' else 'both'
include_network = '{network}'.lower() == 'true'
continue_mode = '{continue}'.lower() == 'true'
generate_summary = '{summary}'.lower() == 'true'

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Find all users
user_files = [f for f in os.listdir(records_path) if f.endswith('.csv')]
user_ids = [f[:-4] for f in user_files]

print(f"{'=' * 70}")
print(f"Bandicoot Batch Processing")
print(f"{'=' * 70}")
print(f"Records path: {records_path}")
print(f"Antennas: {antennas_path or 'None'}")
print(f"Output directory: {output_dir}")
print(f"Groupby: {groupby}")
print(f"Network analysis: {include_network}")
print(f"Total users found: {len(user_ids)}")
print(f"{'=' * 70}\n")

# Check for already processed (continue mode)
already_processed = set()
if continue_mode:
    for f in os.listdir(output_dir):
        if f.endswith('.csv') or f.endswith('.json'):
            uid = f.rsplit('.', 1)[0].replace('_results', '')
            already_processed.add(uid)
    if already_processed:
        print(f"Continue mode: {len(already_processed)} users already processed")
        user_ids = [u for u in user_ids if u not in already_processed]
        print(f"Remaining users: {len(user_ids)}\n")

if not user_ids:
    print("No users to process!")
else:
    # Processing statistics
    start_time = time.time()
    processed = 0
    failed = 0
    skipped = 0
    errors = []
    all_results = []

    # Process each user
    for i, user_id in enumerate(user_ids, 1):
        progress = f"[{i}/{len(user_ids)}]"

        try:
            # Load user
            user = bc.read_csv(
                user_id,
                records_path,
                antennas_path,
                network=include_network,
                describe=False,
                warnings=False
            )

            # Skip users with no records
            if len(user.records) == 0:
                print(f"{progress} SKIP: {user_id} (no records)")
                skipped += 1
                continue

            # Compute indicators
            results = bc.utils.all(
                user,
                groupby=groupby,
                summary='extended',
                network=include_network
            )

            # Save individual results
            user_output_base = os.path.join(output_dir, f"{user_id}_results")

            if output_format in ('csv', 'both'):
                bc.to_csv(results, f"{user_output_base}.csv", warnings=False)

            if output_format in ('json', 'both'):
                bc.to_json(results, f"{user_output_base}.json", warnings=False)

            # Store for summary
            flat = bc.utils.flatten(results)
            flat['user_id'] = user_id
            flat['record_count'] = len(user.records)
            all_results.append(flat)

            processed += 1
            print(f"{progress} OK: {user_id} ({len(user.records)} records)")

        except Exception as e:
            failed += 1
            error_msg = str(e)
            errors.append({'user_id': user_id, 'error': error_msg})
            print(f"{progress} FAIL: {user_id} - {error_msg[:50]}...")

        # Progress update every 10 users
        if i % 10 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (len(user_ids) - i) / rate if rate > 0 else 0
            print(f"    Progress: {i}/{len(user_ids)} | Rate: {rate:.1f}/sec | ETA: {remaining:.0f}s")

    # Final statistics
    elapsed = time.time() - start_time
    print(f"\n{'=' * 70}")
    print("Batch Processing Complete")
    print(f"{'=' * 70}")
    print(f"Total time: {elapsed:.1f} seconds")
    print(f"Users processed: {processed}")
    print(f"Users failed: {failed}")
    print(f"Users skipped: {skipped}")
    print(f"Processing rate: {processed / elapsed:.2f} users/second")

    # Save error log
    if errors:
        error_file = os.path.join(output_dir, '_errors.json')
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2)
        print(f"\nError log saved to: {error_file}")

    # Generate summary file
    if generate_summary and all_results:
        print(f"\n--- Generating Summary ---")

        # Combined CSV with all users
        summary_csv = os.path.join(output_dir, '_all_users_summary.csv')

        # Get all keys
        all_keys = set()
        for r in all_results:
            all_keys.update(r.keys())
        sorted_keys = ['user_id', 'record_count'] + sorted(k for k in all_keys if k not in ('user_id', 'record_count'))

        with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted_keys, extrasaction='ignore')
            writer.writeheader()
            for r in all_results:
                writer.writerow(r)

        print(f"Summary CSV: {summary_csv}")

        # Aggregate statistics
        stats_file = os.path.join(output_dir, '_aggregate_stats.json')
        import statistics

        aggregate = {
            'meta': {
                'generated': datetime.now().isoformat(),
                'users_processed': processed,
                'users_failed': failed,
                'processing_time_seconds': elapsed
            },
            'indicators': {}
        }

        # Compute stats for numeric indicators
        for key in sorted_keys:
            if key in ('user_id',):
                continue

            values = []
            for r in all_results:
                v = r.get(key)
                if v is not None and v != '' and v != 'None':
                    try:
                        values.append(float(v))
                    except (ValueError, TypeError):
                        pass

            if len(values) >= 2:
                aggregate['indicators'][key] = {
                    'mean': statistics.mean(values),
                    'std': statistics.stdev(values),
                    'min': min(values),
                    'max': max(values),
                    'median': statistics.median(values),
                    'n': len(values)
                }

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(aggregate, f, indent=2)

        print(f"Aggregate stats: {stats_file}")

    print(f"\nResults saved to: {output_dir}/")
    print(f"{'=' * 70}")
```

## Examples

### Basic Batch Processing

```
/bandicoot:batch demo/data/ demo/data/antennas.csv
```

### With Summary Statistics

```
/bandicoot:batch data/records/ data/antennas.csv --summary=true --output-dir=results/
```

### Continue Previous Run

```
/bandicoot:batch data/records/ --continue=true --output-dir=results/
```

### JSON Only Output

```
/bandicoot:batch data/records/ --format=json --output-dir=json_results/
```

### With Network Analysis

```
/bandicoot:batch data/records/ --network=true --output-dir=network_results/
```

## Output Structure

```
bandicoot_results/
  user001_results.csv       # Individual user results
  user001_results.json
  user002_results.csv
  user002_results.json
  ...
  _all_users_summary.csv    # Combined summary (if --summary)
  _aggregate_stats.json     # Population statistics (if --summary)
  _errors.json              # Error log (if any failures)
```

## Summary Files

### _all_users_summary.csv

Combined table with one row per user:

| user_id | record_count | active_days__allweek__allday | ... |
|---------|--------------|------------------------------|-----|
| user001 | 1234         | 25                           | ... |
| user002 | 567          | 12                           | ... |

### _aggregate_stats.json

```json
{
  "meta": {
    "generated": "2024-01-15T10:30:00",
    "users_processed": 100,
    "users_failed": 2,
    "processing_time_seconds": 45.2
  },
  "indicators": {
    "active_days__allweek__allday": {
      "mean": 22.5,
      "std": 8.3,
      "min": 1,
      "max": 31,
      "median": 24,
      "n": 100
    },
    ...
  }
}
```

### _errors.json

```json
[
  {
    "user_id": "user_bad",
    "error": "Invalid datetime format in row 5"
  }
]
```

## Performance Tips

### Large Datasets

For datasets with 1000+ users:

1. **Disable network analysis** (faster):
   ```
   /bandicoot:batch data/ --network=false
   ```

2. **Use continue mode** for resumability:
   ```
   /bandicoot:batch data/ --continue=true
   ```

3. **Process in batches** by subdirectory:
   ```
   /bandicoot:batch data/batch1/
   /bandicoot:batch data/batch2/
   ```

### Memory Management

If running out of memory:
- Process smaller batches
- Avoid network analysis for large networks
- Use simpler groupby (e.g., `none` instead of `week`)

## Error Handling

The batch processor handles errors gracefully:

1. **Per-user errors**: Logged but processing continues
2. **Error log**: All failures saved to `_errors.json`
3. **Continue mode**: Resume from where you left off

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid datetime" | Wrong date format | Fix CSV format |
| "No records" | Empty file | Remove empty files |
| "Memory error" | Too much data | Process in smaller batches |
| "File not found" | Missing antenna file | Check paths |

## Integration

### With Compare Command

After batch processing, compare users:

```
/bandicoot:compare all bandicoot_results/ --output=comparison.csv
```

### With Visualization

Visualize summary statistics:

```
/bandicoot:visualize bandicoot_results/_all_users_summary.csv
```

### Export for External Tools

The summary CSV is ready for:
- R/RStudio analysis
- Python pandas
- Excel pivot tables
- Tableau dashboards
- Machine learning pipelines

## Monitoring Progress

The batch processor outputs:

```
[1/100] OK: user001 (1234 records)
[2/100] OK: user002 (567 records)
[3/100] FAIL: user003 - Invalid datetime format...
[4/100] SKIP: user004 (no records)
    Progress: 10/100 | Rate: 2.3/sec | ETA: 39s
```

Progress updates show:
- Current position
- Processing rate
- Estimated time remaining
