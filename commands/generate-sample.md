---
description: Generate synthetic Bandicoot user data for testing
argument-hint: [--records=500] [--seed=42] [--network] [--output=sample_user]
allowed-tools: Bash, Write
---

# Bandicoot: Generate Sample Data

Generate synthetic user data for testing and experimentation with Bandicoot.

## Arguments

- `--records`: Number of records to generate (default: 500)
- `--seed`: Random seed for reproducibility (default: 42)
- `--network`: Include network data (correspondents also generated)
- `--output`: Base name for output files (default: sample_user)
- `--analyze`: Run analysis on generated data immediately

## Execution

Execute the following Python code inline using `conda run -n bandicoot python -c "..."`.
Do not save this as a separate script file.

```python
import bandicoot as bc
import random

# Configuration
num_records = {records} if {records} else 500
seed = {seed} if {seed} else 42
include_network = {network_flag}
output_base = '{output}' if '{output}' else 'sample_user'
run_analysis = {analyze_flag}

# Set seed for reproducibility
random.seed(seed)

print(f"{'=' * 50}")
print("Bandicoot Sample Data Generator")
print('=' * 50)

print(f"\nGenerating synthetic user data...")
print(f"  Records: {num_records}")
print(f"  Seed: {seed}")
print(f"  Network: {include_network}")

# Generate user using Bandicoot's built-in generator
user = bc.tests.sample_user(
    number_records=num_records,
    seed=seed,
    pct_in_network=0.8 if include_network else 0
)

print(f"\n--- Generated User Summary ---")
print(f"Records: {len(user.records)}")
print(f"Date range: {user.start_time} to {user.end_time}")
print(f"Contacts: {len(set(r.correspondent_id for r in user.records))}")
print(f"Antennas: {len(user.antennas)}")
print(f"Has home: {user.has_home}")
print(f"Has calls: {user.has_call}")
print(f"Has texts: {user.has_text}")

if include_network and user.has_network:
    print(f"Network size: {len(user.network)}")

# Show Bandicoot's description
print(f"\n--- Bandicoot Description ---")
user.describe()

# Quick analysis preview
print(f"\n--- Quick Analysis Preview ---")

# Active days
ad = bc.individual.active_days(user, groupby=None)
print(f"Active days: {ad['allweek']['allday']['callandtext']}")

# Contacts
nc = bc.individual.number_of_contacts(user, groupby=None)
print(f"Contacts (call): {nc['allweek']['allday']['call']}")
print(f"Contacts (text): {nc['allweek']['allday']['text']}")

# Call duration
if user.has_call:
    cd = bc.individual.call_duration(user, groupby=None)
    mean_dur = cd['allweek']['allday']['call']['mean']
    print(f"Mean call duration: {mean_dur:.1f} seconds")

# Spatial
if user.has_home:
    rog = bc.spatial.radius_of_gyration(user, groupby=None)
    print(f"Radius of gyration: {rog['allweek']['allday']:.2f} km")

    pah = bc.spatial.percent_at_home(user, groupby=None)
    print(f"Percent at home: {pah['allweek']['allday']*100:.1f}%")

# Run full analysis if requested
if run_analysis:
    print(f"\n--- Full Analysis ---")
    results = bc.utils.all(user, groupby='week')

    # Export results
    csv_file = f"{output_base}_analysis.csv"
    json_file = f"{output_base}_analysis.json"

    bc.to_csv(results, csv_file, warnings=False)
    bc.to_json(results, json_file, warnings=False)

    print(f"Results exported to:")
    print(f"  {csv_file}")
    print(f"  {json_file}")

print(f"\n{'=' * 50}")
print("Sample generation complete!")
print(f"\nNote: This user object exists only in this session.")
print(f"Use the generated user for immediate analysis or")
print(f"export data to files for persistent storage.")
```

## Examples

### Basic Sample (500 records)

```
/bandicoot:generate-sample
```

### Custom Record Count

```
/bandicoot:generate-sample --records=1000
```

### With Network Data

```
/bandicoot:generate-sample --records=500 --network
```

### Reproducible Generation

```
/bandicoot:generate-sample --records=500 --seed=12345
```

### Generate and Analyze

```
/bandicoot:generate-sample --records=500 --analyze
```

## Generated Data Characteristics

### Records

The sample generator creates:
- Mix of calls and texts
- Both incoming and outgoing records
- Random timestamps over ~2 months
- Various call durations
- Random correspondent IDs

### Antennas

- 7 antenna locations around Boston, MA (default)
- Coordinates: approximately 42.35N, -71.09W area
- Realistic distribution of antenna visits

### Home Location

- Automatically detected from nighttime patterns
- Based on most frequent nighttime antenna

### Network (if enabled)

- Correspondent users generated for contacts
- Network loading simulates real data availability
- Some correspondents may be "missing" (realistic)

## Use Cases

### 1. Learning Bandicoot

```
/bandicoot:generate-sample --records=200
```

Quick way to get started with Bandicoot without real data.

### 2. Testing Analysis Pipelines

```
/bandicoot:generate-sample --records=1000 --seed=42 --analyze
```

Use fixed seed for reproducible testing.

### 3. Network Analysis Testing

```
/bandicoot:generate-sample --records=500 --network
```

Test network indicators with synthetic network.

### 4. Benchmarking

```
/bandicoot:generate-sample --records=10000
```

Generate large dataset for performance testing.

## Notes

- Generated data uses Bandicoot's `bc.tests.sample_user()` function
- Data is internally consistent and valid
- Seed ensures reproducibility across runs
- Network generation creates realistic partial coverage
- Generated users have all indicator types available
