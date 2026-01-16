---
description: Export Bandicoot analysis results to CSV or JSON
argument-hint: <user_id> <records_path> [antennas_path] --format=csv|json [--output=filename]
allowed-tools: Bash
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

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Export Commands

| Command | Purpose |
|---------|---------|
| `bc.to_csv(results, 'output.csv')` | Export to CSV (flattened) |
| `bc.to_json(results, 'output.json')` | Export to JSON (nested) |
| `bc.utils.flatten(results)` | Flatten nested dict to single level |

## Workflow

### 1. Load and Analyze

```
user = bc.read_csv('user_id', 'path/')
results = bc.utils.all(user, groupby='week')
```

### 2. Export

```
bc.to_csv(results, 'output.csv')
bc.to_json(results, 'output.json')
```

### 3. Check Output

For CSV, check columns: `len(bc.utils.flatten(results))`

## Output Formats

### CSV Format

Flattened keys with `__` separator:
```csv
name,active_days__allweek__allday__callandtext__mean,call_duration__allweek__allday__call__mean__mean,...
ego,5.5,3776.7,...
```

Key naming convention:
`{indicator}__{week_split}__{day_split}__{interaction}__{stat}__{inner_stat}`

### JSON Format

Preserves nested structure:
```json
{
    "ego": {
        "name": "ego",
        "reporting": { ... },
        "active_days": {
            "allweek": {
                "allday": {
                    "callandtext": {
                        "mean": 5.5,
                        "std": 1.2
                    }
                }
            }
        }
    }
}
```

## Examples

Export to CSV:
```
/bandicoot:export ego demo/data/ demo/data/antennas.csv --format=csv
```

Export to JSON:
```
/bandicoot:export ego demo/data/ demo/data/antennas.csv --format=json
```

Export both formats:
```
/bandicoot:export ego demo/data/ demo/data/antennas.csv --format=both
```

Custom output filename:
```
/bandicoot:export ego demo/data/ --format=csv --output=my_analysis
```

Without grouping (single values):
```
/bandicoot:export ego demo/data/ --format=json --groupby=none
```

## Working with Exported Data

### Loading CSV in Python

```
import pandas as pd
df = pd.read_csv('user_results.csv')
```

### Loading JSON in Python

```
import json
with open('user_results.json') as f:
    data = json.load(f)
value = data['ego']['active_days']['allweek']['allday']['callandtext']['mean']
```

### Exporting Multiple Users

```
results = []
for uid in ['ego', 'user1', 'user2']:
    user = bc.read_csv(uid, 'path/')
    results.append(bc.utils.all(user))
bc.to_csv(results, 'comparison.csv')  # One row per user
```

## Notes

- CSV always flattens nested structure
- JSON preserves original nested structure
- Both formats include all indicators and reporting metadata
- Use `--groupby=none` for single values instead of distributions
