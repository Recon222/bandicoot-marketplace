---
description: Validate Bandicoot data files and environment
argument-hint: [<user_id> <records_path>] [--check-env] [--fix-suggestions]
allowed-tools: Bash, Read
---

# Bandicoot: Validate Data and Environment

Validate CSV data format and Bandicoot environment configuration.

## Arguments

- `user_id` (optional): User identifier to validate
- `records_path` (optional): Directory containing records CSV
- `antennas_path` (optional): Path to antennas file to validate
- `--check-env`: Only check environment, skip data validation
- `--fix-suggestions`: Provide specific suggestions to fix issues

## Execution

### Environment Validation

```python
import sys

print("=" * 60)
print("Bandicoot Environment Validation")
print("=" * 60)

# Check Python version
print(f"\n--- Python Environment ---")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Check Bandicoot import
try:
    import bandicoot as bc
    print(f"Bandicoot version: {bc.__version__}")
    print("[OK] Bandicoot imported successfully")
except ImportError as e:
    print(f"[FAIL] Cannot import bandicoot: {e}")
    print("\nTo install:")
    print("  pip install bandicoot")
    print("  OR")
    print("  conda install -c conda-forge bandicoot")

# Check submodules
modules = ['core', 'individual', 'spatial', 'network', 'recharge', 'io', 'utils']
print(f"\n--- Bandicoot Modules ---")
for mod in modules:
    try:
        __import__(f'bandicoot.{mod}')
        print(f"[OK] bandicoot.{mod}")
    except ImportError as e:
        print(f"[FAIL] bandicoot.{mod}: {e}")

# Check optional dependencies
print(f"\n--- Optional Dependencies ---")
optional = [
    ('numpy', 'Extended statistics'),
    ('scipy', 'Advanced calculations'),
    ('networkx', 'Network analysis'),
]
for mod, desc in optional:
    try:
        __import__(mod)
        print(f"[OK] {mod} ({desc})")
    except ImportError:
        print(f"[--] {mod} not installed ({desc})")
```

### Data Validation

```python
import csv
import os
from datetime import datetime

user_id = '{user_id}'
records_path = '{records_path}'
antennas_path = '{antennas_path}' if '{antennas_path}' else None

print("=" * 60)
print("Bandicoot Data Validation")
print("=" * 60)

if user_id and records_path:
    records_file = os.path.join(records_path, f"{user_id}.csv")

    # Check file exists
    print(f"\n--- File Check ---")
    print(f"Records file: {records_file}")

    if not os.path.exists(records_file):
        print("[FAIL] Records file not found")
        print(f"\nSuggestions:")
        print(f"  1. Check user_id matches filename (without .csv)")
        print(f"  2. Check records_path is correct")

        # List available files
        if os.path.exists(records_path):
            csvs = [f for f in os.listdir(records_path) if f.endswith('.csv')]
            if csvs:
                print(f"\n  Available CSV files in {records_path}:")
                for f in csvs[:10]:
                    print(f"    - {f}")
    else:
        print("[OK] Records file exists")

        # Validate CSV format
        print(f"\n--- CSV Format Validation ---")
        required = {'datetime', 'interaction', 'direction', 'correspondent_id'}
        optional = {'call_duration', 'antenna_id', 'latitude', 'longitude'}

        with open(records_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])

            # Check columns
            missing = required - headers
            if missing:
                print(f"[FAIL] Missing required columns: {missing}")
            else:
                print(f"[OK] All required columns present")

            extra = headers - required - optional
            if extra:
                print(f"[INFO] Extra columns (ignored): {extra}")

            # Validate sample rows
            errors = []
            warnings = []
            row_count = 0

            for i, row in enumerate(reader):
                row_count += 1
                if i >= 100:  # Check first 100 rows
                    break

                # Check datetime
                try:
                    dt = datetime.strptime(row['datetime'], "%Y-%m-%d %H:%M:%S")
                except (ValueError, KeyError):
                    if len(errors) < 5:
                        errors.append(f"Row {i+2}: Invalid datetime '{row.get('datetime', 'MISSING')}'")

                # Check interaction
                if row.get('interaction', '') not in ('call', 'text', ''):
                    if len(errors) < 5:
                        errors.append(f"Row {i+2}: Invalid interaction '{row.get('interaction')}'")

                # Check direction
                if row.get('direction', '') not in ('in', 'out'):
                    if len(errors) < 5:
                        errors.append(f"Row {i+2}: Invalid direction '{row.get('direction')}'")

            print(f"\nRows checked: {min(row_count, 100)}")

            if errors:
                print(f"\n[FAIL] Format errors found:")
                for err in errors:
                    print(f"  - {err}")

                print(f"\nExpected formats:")
                print(f"  datetime: YYYY-MM-DD HH:MM:SS (e.g., 2014-03-02 07:13:30)")
                print(f"  interaction: 'call' or 'text'")
                print(f"  direction: 'in' or 'out'")
            else:
                print(f"[OK] Sample rows validated successfully")

    # Validate antennas file
    if antennas_path:
        print(f"\n--- Antennas File Validation ---")
        print(f"Antennas file: {antennas_path}")

        if not os.path.exists(antennas_path):
            print("[FAIL] Antennas file not found")
        else:
            print("[OK] Antennas file exists")

            with open(antennas_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                ant_headers = set(reader.fieldnames or [])

                ant_required = {'antenna_id', 'latitude', 'longitude'}
                ant_missing = ant_required - ant_headers
                if ant_missing:
                    print(f"[FAIL] Missing columns: {ant_missing}")
                else:
                    print(f"[OK] Required columns present")

                    # Count and validate
                    ant_count = 0
                    for row in reader:
                        ant_count += 1
                        try:
                            lat = float(row['latitude'])
                            lon = float(row['longitude'])
                        except ValueError:
                            print(f"[WARN] Invalid coordinates in row {ant_count + 1}")

                    print(f"Antennas loaded: {ant_count}")

    # Try actual Bandicoot load
    print(f"\n--- Bandicoot Load Test ---")
    try:
        import bandicoot as bc
        user = bc.read_csv(
            user_id, records_path, antennas_path,
            describe=False, warnings=False
        )
        print(f"[OK] Successfully loaded {len(user.records)} records")
        print(f"  Date range: {user.start_time} to {user.end_time}")
        print(f"  Has calls: {user.has_call}")
        print(f"  Has texts: {user.has_text}")
        print(f"  Has home: {user.has_home}")

        if user.ignored_records and user.ignored_records.get('all', 0) > 0:
            print(f"\n[WARN] {user.ignored_records['all']} records were ignored")
            for key, count in user.ignored_records.items():
                if key != 'all' and count > 0:
                    print(f"  - {key}: {count}")
    except Exception as e:
        print(f"[FAIL] Bandicoot load failed: {e}")

else:
    print("\nNo data files specified. Use --check-env for environment-only validation.")

print(f"\n{'=' * 60}")
print("Validation complete!")
```

## Examples

### Environment Check Only

```
/bandicoot:validate --check-env
```

### Validate User Data

```
/bandicoot:validate ego demo/data/
```

### Validate With Antennas

```
/bandicoot:validate ego demo/data/ demo/data/antennas.csv
```

### Get Fix Suggestions

```
/bandicoot:validate ego demo/data/ --fix-suggestions
```

## Validation Checks

### Environment Checks

- Python version and path
- Bandicoot installation and version
- Required submodules (core, individual, spatial, network, recharge, io, utils)
- Optional dependencies (numpy, scipy, networkx)

### Data File Checks

- File existence
- CSV format validity
- Required columns present
- Data type validation (datetime, interaction, direction)
- Sample row validation

### Antennas File Checks

- File existence
- Required columns (antenna_id, latitude, longitude)
- Coordinate validity

### Load Test

- Actual Bandicoot load attempt
- Record count and date range
- Data quality warnings
- Ignored records summary

## Common Issues and Fixes

### "Missing required columns"

Ensure your CSV has these headers:
```csv
datetime,interaction,direction,correspondent_id
```

### "Invalid datetime format"

Convert to: `YYYY-MM-DD HH:MM:SS`
Example: `2014-03-02 07:13:30`

### "Invalid interaction type"

Must be lowercase `call` or `text`

### "Invalid direction"

Must be lowercase `in` or `out`

### "Records file not found"

- Check user_id matches filename (without .csv)
- Verify records_path is correct directory
- Ensure file has .csv extension

### "Many records ignored"

Check `user.ignored_records` for specific issues:
- `datetime`: Invalid timestamp format
- `interaction`: Not 'call' or 'text'
- `direction`: Not 'in' or 'out'
- `correspondent_id`: Empty or missing
