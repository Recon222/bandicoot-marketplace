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

Records file: `{records_path}/{user_id}.csv`

Example: if user_id is "ego" and records_path is "demo/data/":
- Records file: `demo/data/ego.csv`
- Antennas file (if provided): `demo/data/antennas.csv`

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Load Commands

| Command | Purpose |
|---------|---------|
| `bc.read_csv('user_id', 'path/')` | Basic load |
| `bc.read_csv('user_id', 'path/', 'antennas.csv')` | With antennas |
| `bc.read_csv('user_id', 'path/', network=True)` | With network |
| `bc.read_csv('user_id', 'path/', 'antennas.csv', network=True)` | Full load |
| `bc.read_csv('user_id', 'path/', describe=True)` | Show summary |
| `bc.read_csv('user_id', 'path/', warnings=False)` | Suppress warnings |

## Properties to Check After Loading

| Property | Meaning |
|----------|---------|
| `user.name` | User identifier |
| `len(user.records)` | Number of records loaded |
| `user.start_time` | First record timestamp |
| `user.end_time` | Last record timestamp |
| `user.has_call` | True if call records present |
| `user.has_text` | True if text records present |
| `user.has_home` | True if home location detected |
| `len(user.antennas)` | Number of antennas loaded |
| `user.has_network` | True if network data loaded |
| `len(user.network)` | Number of correspondents |
| `user.ignored_records` | Dict of ignored record counts |

## Workflow

### 1. Verify Environment

```
import bandicoot as bc; print(f'Bandicoot {bc.__version__} ready')
```

### 2. Verify Files Exist

Use `dir` (Windows) or `ls` (Unix) to check file exists.

### 3. Load User

```
user = bc.read_csv('user_id', 'path/', describe=True)
```

### 4. Check Results

Print key properties to verify successful load.

## Examples

Basic load:
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

Load with network:
```
/bandicoot:load ego demo/data/ demo/data/antennas.csv --network
```

Load without antennas (no spatial indicators):
```
/bandicoot:load ego demo/data/
```

## Troubleshooting

**File Not Found**
- Verify user_id matches CSV filename (without .csv)
- Check records_path is correct
- List directory to see available files

**No Records Loaded (count is 0)**
- Check CSV format: datetime, interaction, direction, correspondent_id columns
- Verify datetime format: `YYYY-MM-DD HH:MM:SS`
- Ensure interaction values: 'call' or 'text'
- Ensure direction values: 'in' or 'out'

**Missing Location Data / Home Not Detected**
- Verify antennas file path
- Check antenna_id values match between records and antennas files
- Ensure antennas file has: antenna_id, latitude, longitude columns

## Notes

- Each command execution is independent - user object does not persist
- For continued analysis, use `/bandicoot:analyze` which handles loading
- Use `--network` only when needed (slower loading)
