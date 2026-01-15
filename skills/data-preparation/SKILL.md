---
name: data-preparation
description: |
  Use this skill when preparing data for Bandicoot analysis, converting data
  formats, fixing CSV issues, or understanding data requirements.

  <example>
  Context: User has phone records in wrong format
  user: "My CSV has different column names, how do I convert it?"
  assistant: "[Uses skill to guide format conversion]"
  <commentary>
  Data format conversion guidance.
  </commentary>
  </example>

  <example>
  Context: User encounters data loading errors
  user: "Bandicoot says my datetime format is wrong"
  assistant: "[Uses skill to explain correct format and conversion]"
  <commentary>
  Data format troubleshooting.
  </commentary>
  </example>

allowed-tools: Bash, Read, Write
---

# Bandicoot Data Preparation Skill

You are an expert in preparing data for Bandicoot analysis. Help users convert
their data to the correct format, fix common issues, and understand data
requirements.

## Required Data Formats

### Records CSV (Required)

The primary data file containing call and text records.

**Required columns**:

| Column | Type | Values | Description |
|--------|------|--------|-------------|
| `datetime` | string | `YYYY-MM-DD HH:MM:SS` | Record timestamp |
| `interaction` | string | `call` or `text` | Type of interaction |
| `direction` | string | `in` or `out` | Incoming or outgoing |
| `correspondent_id` | string | any | Unique contact identifier |

**Optional columns**:

| Column | Type | Values | Description |
|--------|------|--------|-------------|
| `call_duration` | integer | seconds | Duration (calls only) |
| `antenna_id` | string | any | Cell tower identifier |
| `latitude` | float | -90 to 90 | GPS latitude |
| `longitude` | float | -180 to 180 | GPS longitude |

**Example**:
```csv
datetime,interaction,direction,correspondent_id,call_duration,antenna_id
2014-03-02 07:13:30,call,out,contact_5,120,tower_701
2014-03-02 09:45:00,text,in,contact_12,,tower_702
2014-03-02 10:30:00,call,in,contact_5,45,tower_701
```

### Antennas CSV (Optional)

Maps antenna IDs to geographic coordinates.

**Required columns**:

| Column | Type | Description |
|--------|------|-------------|
| `antenna_id` | string | Must match antenna_id in records |
| `latitude` | float | Antenna latitude |
| `longitude` | float | Antenna longitude |

**Example**:
```csv
antenna_id,latitude,longitude
tower_701,42.361013,-71.097868
tower_702,42.370849,-71.114613
tower_703,42.355800,-71.101200
```

### Recharges CSV (Optional)

Mobile phone top-up/recharge records.

**Required columns**:

| Column | Type | Description |
|--------|------|-------------|
| `datetime` | string | Recharge timestamp |
| `amount` | float | Recharge amount |

**Optional columns**:

| Column | Type | Description |
|--------|------|-------------|
| `retailer_id` | string | Retailer identifier |

**Example**:
```csv
datetime,amount,retailer_id
2014-03-01 10:00:00,500,retailer_01
2014-03-15 14:30:00,1000,retailer_02
```

### Attributes CSV (Optional)

User metadata/attributes.

**Required columns**:

| Column | Type | Description |
|--------|------|-------------|
| `key` | string | Attribute name |
| `value` | string | Attribute value |

**Example**:
```csv
key,value
age,25
gender,M
income,medium
```

## Common Data Conversion Tasks

### Converting Datetime Formats

**From various formats to Bandicoot format**:

```python
import pandas as pd
from datetime import datetime

df = pd.read_csv('original_data.csv')

# From Unix timestamp (seconds)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

# From Unix timestamp (milliseconds)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

# From other string formats
df['datetime'] = pd.to_datetime(df['date_column'])
df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

# From separate date and time columns
df['datetime'] = df['date'] + ' ' + df['time']

# Save
df.to_csv('converted_data.csv', index=False)
```

### Converting Column Names

```python
import pandas as pd

df = pd.read_csv('original_data.csv')

# Rename columns to match Bandicoot format
column_mapping = {
    'timestamp': 'datetime',
    'type': 'interaction',
    'dir': 'direction',
    'contact': 'correspondent_id',
    'duration': 'call_duration',
    'tower': 'antenna_id'
}

df = df.rename(columns=column_mapping)

# Save
df.to_csv('converted_data.csv', index=False)
```

### Converting Interaction Types

```python
import pandas as pd

df = pd.read_csv('original_data.csv')

# Map different values to 'call' and 'text'
interaction_mapping = {
    'VOICE': 'call',
    'SMS': 'text',
    'MMS': 'text',
    'CALL': 'call',
    '1': 'call',
    '2': 'text'
}

df['interaction'] = df['type'].map(interaction_mapping)

# Save
df.to_csv('converted_data.csv', index=False)
```

### Converting Direction Values

```python
import pandas as pd

df = pd.read_csv('original_data.csv')

# Map different values to 'in' and 'out'
direction_mapping = {
    'INCOMING': 'in',
    'OUTGOING': 'out',
    'IN': 'in',
    'OUT': 'out',
    'RECEIVED': 'in',
    'SENT': 'out',
    '1': 'in',
    '2': 'out'
}

df['direction'] = df['direction_code'].map(direction_mapping)

# Save
df.to_csv('converted_data.csv', index=False)
```

### Converting Call Duration

```python
import pandas as pd

df = pd.read_csv('original_data.csv')

# From minutes to seconds
df['call_duration'] = df['duration_minutes'] * 60

# From HH:MM:SS format
def parse_duration(s):
    if pd.isna(s) or s == '':
        return None
    parts = s.split(':')
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

df['call_duration'] = df['duration_str'].apply(parse_duration)

# Save
df.to_csv('converted_data.csv', index=False)
```

## Data Validation Script

Use this to check your converted data:

```python
import csv
from datetime import datetime

def validate_bandicoot_csv(filepath):
    """Validate CSV for Bandicoot compatibility."""
    print(f"Validating: {filepath}")

    required = {'datetime', 'interaction', 'direction', 'correspondent_id'}
    errors = []

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        # Check columns
        missing = required - set(reader.fieldnames)
        if missing:
            print(f"FAIL: Missing columns: {missing}")
            return False

        # Check rows
        for i, row in enumerate(reader):
            if i >= 100:
                break

            # Datetime
            try:
                datetime.strptime(row['datetime'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                errors.append(f"Row {i+2}: Invalid datetime")

            # Interaction
            if row['interaction'] not in ('call', 'text', ''):
                errors.append(f"Row {i+2}: Invalid interaction")

            # Direction
            if row['direction'] not in ('in', 'out'):
                errors.append(f"Row {i+2}: Invalid direction")

    if errors:
        print(f"FAIL: {len(errors)} errors found")
        for e in errors[:10]:
            print(f"  - {e}")
        return False

    print("PASS: Data format is valid")
    return True

# Run validation
validate_bandicoot_csv('converted_data.csv')
```

## File Organization

### Single User

```
data/
  records/
    user123.csv          # Records file
  antennas.csv           # Shared antennas file
```

Load with:
```python
user = bc.read_csv('user123', 'data/records/', 'data/antennas.csv')
```

### Multiple Users

```
data/
  records/
    user001.csv
    user002.csv
    user003.csv
    ...
  antennas.csv
```

### With Recharges and Attributes

```
data/
  records/
    user123.csv
  recharges/
    user123.csv          # Same filename as records
  attributes/
    user123.csv          # Same filename as records
  antennas.csv
```

Load with:
```python
user = bc.read_csv(
    'user123',
    'data/records/',
    'data/antennas.csv',
    recharges_path='data/recharges/',
    attributes_path='data/attributes/'
)
```

## Common Issues and Fixes

### Issue: "Missing required columns"

**Cause**: Column names don't match expected format

**Fix**: Rename columns to match exactly:
- `datetime` (not `timestamp`, `date`, `time`)
- `interaction` (not `type`, `call_type`)
- `direction` (not `dir`, `in_out`)
- `correspondent_id` (not `contact`, `number`)

### Issue: "Invalid datetime format"

**Cause**: Datetime not in `YYYY-MM-DD HH:MM:SS` format

**Examples of invalid formats**:
- `03/02/2014 7:13:30` (wrong date order, no leading zeros)
- `2014-3-2 7:13:30` (missing leading zeros)
- `2014/03/02 07:13:30` (wrong separator)
- `1393749210` (unix timestamp)

**Fix**: Convert to exact format `2014-03-02 07:13:30`

### Issue: "Invalid interaction type"

**Cause**: Values other than `call` or `text`

**Fix**: Map all values to lowercase `call` or `text`

### Issue: "Many records ignored"

**Cause**: Multiple validation failures

**Check**: `user.ignored_records` for details

### Issue: "Antennas not matching"

**Cause**: `antenna_id` in records doesn't match antennas file

**Fix**: Ensure exact string match (check case, whitespace)

## Large File Handling

For very large files:

```python
import pandas as pd

# Process in chunks
chunksize = 100000
chunks = []

for chunk in pd.read_csv('large_file.csv', chunksize=chunksize):
    # Process chunk
    chunk = process_chunk(chunk)
    chunks.append(chunk)

# Combine and save
df = pd.concat(chunks)
df.to_csv('processed_file.csv', index=False)
```

## Anonymization

Before sharing data, anonymize:

```python
import pandas as pd
import hashlib

df = pd.read_csv('original_data.csv')

# Hash correspondent IDs
def anonymize(value):
    return hashlib.sha256(str(value).encode()).hexdigest()[:16]

df['correspondent_id'] = df['correspondent_id'].apply(anonymize)

# Round timestamps (optional)
df['datetime'] = pd.to_datetime(df['datetime'])
df['datetime'] = df['datetime'].dt.floor('H')  # Round to hour
df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Save
df.to_csv('anonymized_data.csv', index=False)
```
