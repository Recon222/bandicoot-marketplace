---
description: Load mobile phone records into Bandicoot for analysis
argument-hint: <user_id> <records_path> [antennas_path] [--network]
allowed-tools: Bash, Read
---

# Bandicoot: Load User Data

Load user phone records from CSV files into Bandicoot and display a summary.

## Arguments

- `user_id` (required): User identifier - the filename without .csv extension
- `records_path` (required): Path to directory containing the records CSV file
- `antennas_path` (optional): Path to the antennas CSV file for location data
- `--network` flag: Also load correspondent data for network analysis

## Expected File Structure

The records file must be located at: `{records_path}/{user_id}.csv`

For example, if user_id is "ego" and records_path is "demo/data/":
- Records file: `demo/data/ego.csv`
- Antennas file (if provided): `demo/data/antennas.csv`

## Execution Steps

### Step 1: Verify Environment

First, check that Bandicoot is available:

```bash
conda run -n bandicoot python -c "import bandicoot as bc; print(f'Bandicoot {bc.__version__} ready')"
```

If conda is not available, try direct Python:

```bash
python -c "import bandicoot as bc; print(f'Bandicoot {bc.__version__} ready')"
```

### Step 2: Verify Files Exist

Check that the records file exists:

```bash
# On Windows
dir "{records_path}\{user_id}.csv"

# On Unix
ls -la "{records_path}/{user_id}.csv"
```

If antennas_path is provided, verify it exists too.

### Step 3: Load User Data

Execute the following Python code, adjusting based on provided arguments:

**With antennas file:**

```python
import bandicoot as bc

user = bc.read_csv(
    '{user_id}',
    '{records_path}',
    '{antennas_path}',
    network={network_flag},  # True if --network provided, else False
    describe=True,
    warnings=True
)

# Additional summary
print(f"\n=== Loading Summary ===")
print(f"User ID: {user.name}")
print(f"Records: {len(user.records)}")
print(f"Date range: {user.start_time} to {user.end_time}")
print(f"Has calls: {user.has_call}")
print(f"Has texts: {user.has_text}")
print(f"Has home: {user.has_home}")
print(f"Antennas: {len(user.antennas)}")

if user.ignored_records and user.ignored_records.get('all', 0) > 0:
    print(f"\nWarning: {user.ignored_records['all']} records were ignored")
    for key, count in user.ignored_records.items():
        if key != 'all' and count > 0:
            print(f"  - {key}: {count}")

if user.has_network:
    print(f"\nNetwork loaded: {len(user.network)} correspondents")
    print(f"Out-of-network calls: {user.percent_outofnetwork_calls:.1%}")
```

**Without antennas file:**

```python
import bandicoot as bc

user = bc.read_csv(
    '{user_id}',
    '{records_path}',
    network={network_flag},
    describe=True,
    warnings=True
)

print(f"\n=== Loading Summary ===")
print(f"User ID: {user.name}")
print(f"Records: {len(user.records)}")
print(f"Date range: {user.start_time} to {user.end_time}")
print(f"Has calls: {user.has_call}")
print(f"Has texts: {user.has_text}")
```

### Step 4: Report Results

After loading, report to the user:

1. **Success indicators**:
   - Number of records loaded
   - Date range of the data
   - Number of unique contacts
   - Whether home location was detected

2. **Data quality notes**:
   - Any ignored/filtered records
   - Missing location data percentage
   - Warnings from Bandicoot

3. **Next steps**: Suggest running `/bandicoot:analyze` or `/bandicoot:quick-stats`

## Examples

### Basic Load

```
/bandicoot:load ego demo/data/ demo/data/antennas.csv
```

Expected output:
```
[x] 314 records from 2014-03-02 07:13:30 to 2014-04-14 12:04:37
[x] 7 contacts
[x] 27 antennas
[x] Has home
[x] Has texts
[x] Has calls
```

### Load with Network

```
/bandicoot:load ego demo/data/ demo/data/antennas.csv --network
```

This will also load correspondent data files from the same directory for network analysis.

### Load Without Antennas

```
/bandicoot:load ego demo/data/
```

Spatial indicators will not be available without antenna location data.

## Troubleshooting

### File Not Found

If the records file is not found:
1. Verify the user_id matches the CSV filename (without .csv extension)
2. Check the records_path is correct
3. List files in the directory to see available users

### No Records Loaded

If records count is 0 or very low:
1. Check CSV format (datetime, interaction, direction, correspondent_id columns)
2. Verify datetime format is YYYY-MM-DD HH:MM:SS
3. Ensure interaction values are 'call' or 'text'
4. Ensure direction values are 'in' or 'out'

### Missing Location Data

If home is not detected or antennas count is 0:
1. Verify antennas file path is correct
2. Check antenna_id values match between records and antennas files
3. Ensure antennas file has antenna_id, latitude, longitude columns

## Notes

- Each command execution is independent - the loaded user object does not persist
- For continued analysis, use `/bandicoot:analyze` which handles loading internally
- Use `--network` only when you need network analysis (slower loading)
