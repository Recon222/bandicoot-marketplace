---
description: Generate synthetic Bandicoot user data for testing
argument-hint: [--records=500] [--seed=42] [--network] [--output=sample_user]
allowed-tools: Bash
---

# Bandicoot: Generate Sample Data

Generate synthetic user data for testing and experimentation with Bandicoot.

## Arguments

- `--records`: Number of records to generate (default: 500)
- `--seed`: Random seed for reproducibility (default: 42)
- `--network`: Include network data (correspondents also generated)
- `--output`: Base name for output files (default: sample_user)
- `--analyze`: Run analysis on generated data immediately

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Generation Command

```
user = bc.tests.sample_user(number_records=500, seed=42)
```

With network:
```
user = bc.tests.sample_user(number_records=500, seed=42, pct_in_network=0.8)
```

## Key Functions

| Command | Purpose |
|---------|---------|
| `bc.tests.sample_user(number_records=500)` | Generate synthetic user |
| `bc.tests.sample_user(seed=42)` | Reproducible generation |
| `bc.tests.sample_user(pct_in_network=0.8)` | Include network data |
| `user.describe()` | Show generated user summary |

## Properties of Generated User

After generation, check:

| Property | Expected |
|----------|----------|
| `len(user.records)` | Specified count |
| `user.has_call` | True |
| `user.has_text` | True |
| `user.has_home` | True |
| `len(user.antennas)` | ~7 (Boston area) |
| `user.has_network` | True if pct_in_network > 0 |

## Generated Data Characteristics

### Records
- Mix of calls and texts
- Both incoming and outgoing
- Random timestamps over ~2 months
- Various call durations
- Random correspondent IDs

### Antennas
- 7 antenna locations around Boston, MA
- Coordinates: ~42.35N, -71.09W area
- Realistic distribution of visits

### Home Location
- Automatically detected from nighttime patterns
- Based on most frequent nighttime antenna

### Network (if enabled)
- Correspondent users generated for contacts
- Some correspondents may be "missing" (realistic)

## Examples

Basic sample (500 records):
```
/bandicoot:generate-sample
```

Custom record count:
```
/bandicoot:generate-sample --records=1000
```

With network data:
```
/bandicoot:generate-sample --records=500 --network
```

Reproducible generation:
```
/bandicoot:generate-sample --records=500 --seed=12345
```

Generate and analyze:
```
/bandicoot:generate-sample --records=500 --analyze
```

## Use Cases

### Learning Bandicoot

Quick way to get started without real data.

### Testing Analysis Pipelines

Use fixed seed for reproducible testing.

### Network Analysis Testing

Test network indicators with synthetic network.

### Benchmarking

Generate large dataset for performance testing.

## Quick Analysis on Generated Data

```
# Generate
user = bc.tests.sample_user(number_records=500, seed=42)

# Analyze
bc.individual.active_days(user, groupby=None)
bc.individual.number_of_contacts(user, groupby=None)
bc.spatial.radius_of_gyration(user, groupby=None)

# Full analysis
results = bc.utils.all(user)
bc.to_csv(results, 'sample_results.csv')
```

## Notes

- Uses Bandicoot's built-in `bc.tests.sample_user()` function
- Data is internally consistent and valid
- Seed ensures reproducibility across runs
- Generated users have all indicator types available
