# Bandicoot Troubleshooting Guide

Comprehensive guide for diagnosing and resolving common issues when working with
Bandicoot.

## Environment Issues

### ImportError: No module named 'bandicoot'

**Symptoms**: Python cannot find the bandicoot module.

**Diagnosis**:
```bash
# Check if conda environment exists
conda env list

# Check if bandicoot is installed
conda run -n bandicoot pip list | grep -i bandicoot
```

**Solutions**:

1. Create the conda environment:
```bash
conda create -n bandicoot python=3.8
conda activate bandicoot
pip install bandicoot
```

2. If using pip directly:
```bash
pip install bandicoot
```

3. Verify installation:
```bash
conda run -n bandicoot python -c "import bandicoot as bc; print(bc.__version__)"
```

---

### Conda activation fails on Windows

**Symptoms**: `conda activate` doesn't work in scripts or subprocess calls.

**Cause**: `conda activate` requires shell initialization that isn't available in
subprocess contexts.

**Solution**: Always use `conda run` instead:

```bash
# Instead of:
# conda activate bandicoot && python script.py

# Use:
conda run -n bandicoot python script.py
```

---

## Data Loading Issues

### FileNotFoundError: Records file not found

**Symptoms**: `FileNotFoundError` when calling `bc.read_csv()`.

**Common causes**:

1. **Wrong path format**: The records file must be at `{records_path}/{user_id}.csv`

**Diagnosis**:
```python
import os
records_path = 'demo/data/'
user_id = 'ego'
expected_file = os.path.join(records_path, f"{user_id}.csv")
print(f"Looking for: {expected_file}")
print(f"Exists: {os.path.exists(expected_file)}")
```

**Solutions**:

```python
# Correct: user_id is filename without .csv
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')

# Wrong: don't include .csv in user_id
# user = bc.read_csv('ego.csv', 'demo/data/', ...)

# Wrong: don't include full path
# user = bc.read_csv('demo/data/ego', ...)
```

---

### No records loaded / Empty user

**Symptoms**: `len(user.records)` is 0, or all indicators return None/empty.

**Diagnosis**:
```python
user = bc.read_csv('ego', 'demo/data/', describe=True, warnings=True)
print(f"Records: {len(user.records)}")
print(f"Ignored: {user.ignored_records}")
```

**Common causes and solutions**:

1. **Invalid datetime format**:
   - Required: `YYYY-MM-DD HH:MM:SS`
   - Check your CSV for correct format

2. **Invalid interaction type**:
   - Must be exactly `'call'` or `'text'` (lowercase)

3. **Invalid direction**:
   - Must be exactly `'in'` or `'out'` (lowercase)

4. **Missing required columns**:
   - Required: `datetime`, `interaction`, `direction`, `correspondent_id`

**Validation script**:
```python
import csv

def validate_records_csv(filepath):
    required = {'datetime', 'interaction', 'direction', 'correspondent_id'}

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])

        missing = required - headers
        if missing:
            print(f"Missing columns: {missing}")
            return False

        for i, row in enumerate(reader):
            if i >= 5:
                break
            print(f"Row {i}: {row}")

    return True
```

---

### Missing location warnings

**Symptoms**: Warning about records missing location, or spatial indicators are None.

**Diagnosis**:
```python
from bandicoot.helper.tools import percent_records_missing_location
pct = percent_records_missing_location(user)
print(f"{pct:.1%} records missing location")
```

**Common causes**:

1. **No antennas file provided**:
```python
# Wrong - no antenna locations
user = bc.read_csv('ego', 'demo/data/')

# Correct - include antennas file
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')
```

2. **Mismatched antenna IDs**:
   - `antenna_id` in records must match keys in antennas CSV
   - Check for whitespace, case sensitivity

3. **Antennas file format wrong**:
   - Must have columns: `antenna_id`, `latitude`, `longitude`

**Check antenna matching**:
```python
# Get antenna IDs from records
record_antennas = set(r.position.antenna for r in user.records
                       if r.position.antenna)
# Get antenna IDs from antennas dict
loaded_antennas = set(user.antennas.keys())

# Find mismatches
missing = record_antennas - loaded_antennas
if missing:
    print(f"Antennas in records but not in file: {missing}")
```

---

### Home location not detected

**Symptoms**: `user.has_home` is False, `percent_at_home` returns None.

**Cause**: Home is detected from the most frequent nighttime location. Requires:
- Records during night hours (7pm-7am by default)
- Those records must have antenna/location data

**Diagnosis**:
```python
import datetime

night_records = [r for r in user.records
                 if r.datetime.time() >= datetime.time(19)
                 or r.datetime.time() < datetime.time(7)]
night_with_location = [r for r in night_records
                       if r.position.antenna or r.position.location]

print(f"Night records: {len(night_records)}")
print(f"Night records with location: {len(night_with_location)}")
```

**Solutions**:

1. Ensure antenna data is loaded
2. Check that data includes nighttime records
3. Adjust night definition if needed:
```python
user.night_start = datetime.time(21)  # 9 PM
user.night_end = datetime.time(6)     # 6 AM
user.recompute_home()
```

---

## Network Analysis Issues

### Network indicators return None

**Symptoms**: `clustering_coefficient_*` and other network functions return None.

**Cause**: Network not loaded when calling `bc.read_csv()`.

**Solution**:
```python
# Must set network=True
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv',
                   network=True)
print(f"Has network: {user.has_network}")
print(f"Network size: {len(user.network)}")
```

**Requirements for network loading**:
- Correspondent CSV files must exist in the same directory
- Files named `{correspondent_id}.csv`

---

### High percent_outofnetwork values

**Symptoms**: `user.percent_outofnetwork_calls` > 0.5 indicates many contacts not in network.

**Cause**: Correspondent CSV files not found for many contacts.

**Diagnosis**:
```python
print(f"Out-of-network calls: {user.percent_outofnetwork_calls:.1%}")
print(f"Out-of-network texts: {user.percent_outofnetwork_texts:.1%}")
print(f"Out-of-network contacts: {user.percent_outofnetwork_contacts:.1%}")

# List missing correspondents
from collections import Counter
correspondents = Counter(r.correspondent_id for r in user.records)
for c_id, count in correspondents.most_common():
    if user.network.get(c_id) is None:
        print(f"Missing: {c_id} ({count} records)")
```

**Solution**: This is often expected - complete network data is rarely available.
Focus analysis on indicators that don't require network data.

---

## Recharge Analysis Issues

### Recharge indicators not computed

**Symptoms**: `bc.recharge.*` functions fail or return None.

**Diagnosis**:
```python
print(f"Has recharges: {user.has_recharges}")
print(f"Number of recharges: {len(user.recharges)}")
```

**Solutions**:

1. **Provide recharges path**:
```python
user = bc.read_csv('ego', 'demo/data/', recharges_path='demo/recharges/')
```

2. **Check file location**: Must be at `{recharges_path}/{user_id}.csv`

3. **Verify format**: Required columns: `datetime`, `amount`
   Optional: `retailer_id`

---

## Output Issues

### CSV export has wrong values

**Symptoms**: Exported CSV contains unexpected values or structure.

**Solutions**:

1. **Check rounding**:
```python
bc.to_csv(results, 'output.csv', digits=10)  # More precision
```

2. **Verify result structure**:
```python
import json
print(json.dumps(results, indent=2, default=str))
```

3. **Use flatten for inspection**:
```python
flat = bc.utils.flatten(results)
for key, value in flat.items():
    print(f"{key}: {value}")
```

---

### Results don't match expected values

**Symptoms**: Indicators have different values than expected from known-good data.

**Diagnostic checklist**:

1. **Check groupby setting**:
```python
# Different groupby = different results
results_week = bc.utils.all(user, groupby='week')
results_none = bc.utils.all(user, groupby=None)
```

2. **Check summary setting**:
```python
# Different summary = different output format
results_default = bc.utils.all(user, summary='default')
results_extended = bc.utils.all(user, summary='extended')
```

3. **Check data loading**:
```python
print(f"Records: {len(user.records)}")
print(f"Ignored: {user.ignored_records}")
print(f"Date range: {user.start_time} to {user.end_time}")
```

4. **Compare with reference**:
```python
# Run on demo data
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')
results = bc.utils.all(user, groupby='week')

# Expected values for ego user:
# active_days mean: ~5.5
# number_of_contacts call mean: ~5.14
# call_duration call mean mean: ~3776
```

---

## Performance Issues

### Analysis is very slow

**Symptoms**: `bc.utils.all()` or loading takes excessive time.

**Solutions**:

1. **Avoid network loading if not needed**:
```python
# Much faster without network
user = bc.read_csv('ego', 'demo/data/', network=False)
```

2. **Use filter_empty**:
```python
results = bc.utils.all(user, filter_empty=True)
```

3. **Process in batches**: For multiple users, load and process one at a time:
```python
for user_id in user_ids:
    user = bc.read_csv(user_id, path, describe=False, warnings=False)
    results = bc.utils.all(user)
    # Process results immediately
    user = None  # Allow garbage collection
```

---

### Memory issues with large datasets

**Symptoms**: MemoryError or system slowdown with many users.

**Solutions**:

1. **Process incrementally**:
```python
results_list = []
for user_id in user_ids:
    user = bc.read_csv(user_id, path)
    result = bc.utils.all(user)
    flat = bc.utils.flatten(result)
    results_list.append(flat)
    del user  # Free memory
```

2. **Export as you go**:
```python
import csv

with open('output.csv', 'w', newline='') as f:
    writer = None
    for user_id in user_ids:
        user = bc.read_csv(user_id, path)
        result = bc.utils.all(user)
        flat = bc.utils.flatten(result)

        if writer is None:
            writer = csv.DictWriter(f, fieldnames=flat.keys())
            writer.writeheader()

        writer.writerow(flat)
```

---

## Diagnostic Commands

### Quick Health Check

```python
import bandicoot as bc

def health_check(user_id, records_path, antennas_path=None):
    """Run comprehensive health check on user data."""
    print(f"=== Health Check for {user_id} ===\n")

    try:
        user = bc.read_csv(user_id, records_path, antennas_path,
                          describe=False, warnings=True)
    except Exception as e:
        print(f"FAILED to load: {e}")
        return

    print(f"Records: {len(user.records)}")
    print(f"Date range: {user.start_time} to {user.end_time}")
    print(f"Has calls: {user.has_call}")
    print(f"Has texts: {user.has_text}")
    print(f"Has home: {user.has_home}")
    print(f"Antennas: {len(user.antennas)}")

    if user.ignored_records:
        total_ignored = user.ignored_records.get('all', 0)
        if total_ignored > 0:
            print(f"\nWARNING: {total_ignored} records ignored:")
            for key, count in user.ignored_records.items():
                if key != 'all' and count > 0:
                    print(f"  - {key}: {count}")

    # Test core indicators
    print("\n--- Indicator Tests ---")
    try:
        ad = bc.individual.active_days(user, groupby=None)
        print(f"active_days: OK ({ad})")
    except Exception as e:
        print(f"active_days: FAILED ({e})")

    try:
        nc = bc.individual.number_of_contacts(user, groupby=None)
        print(f"number_of_contacts: OK")
    except Exception as e:
        print(f"number_of_contacts: FAILED ({e})")

    if user.has_antennas:
        try:
            rog = bc.spatial.radius_of_gyration(user, groupby=None)
            print(f"radius_of_gyration: OK")
        except Exception as e:
            print(f"radius_of_gyration: FAILED ({e})")

    print("\n=== Health Check Complete ===")
```

### Data Format Validator

```python
import csv
from datetime import datetime

def validate_csv_format(filepath):
    """Validate CSV format for Bandicoot records."""
    print(f"Validating: {filepath}\n")

    required = {'datetime', 'interaction', 'direction', 'correspondent_id'}
    optional = {'call_duration', 'antenna_id', 'latitude', 'longitude'}

    issues = []

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])

        # Check columns
        missing = required - headers
        if missing:
            issues.append(f"Missing required columns: {missing}")

        extra = headers - required - optional
        if extra:
            print(f"Note: Extra columns will be ignored: {extra}")

        # Validate rows
        for i, row in enumerate(reader):
            if i >= 100:  # Check first 100 rows
                break

            # Datetime
            try:
                datetime.strptime(row['datetime'], "%Y-%m-%d %H:%M:%S")
            except (ValueError, KeyError):
                issues.append(f"Row {i+1}: Invalid datetime '{row.get('datetime')}'")

            # Interaction
            if row.get('interaction') not in ('call', 'text', ''):
                issues.append(f"Row {i+1}: Invalid interaction '{row.get('interaction')}'")

            # Direction
            if row.get('direction') not in ('in', 'out'):
                issues.append(f"Row {i+1}: Invalid direction '{row.get('direction')}'")

    if issues:
        print("ISSUES FOUND:")
        for issue in issues[:20]:  # Show first 20
            print(f"  - {issue}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more issues")
        return False
    else:
        print("VALIDATION PASSED")
        return True
```
