# Common Data Issues and Solutions

Troubleshooting guide for common data preparation problems.

## Datetime Issues

### Issue: "Invalid datetime format"

**Symptoms**:
- Records ignored during loading
- `user.ignored_records['datetime']` is high

**Common causes**:

| Your Format | Problem | Solution |
|-------------|---------|----------|
| `03/02/2014 07:13:30` | Wrong date order | Convert to `2014-03-02 07:13:30` |
| `2014-3-2 7:13:30` | Missing zeros | Add leading zeros |
| `2014/03/02 07:13:30` | Wrong separator | Use `-` not `/` |
| `1393749210` | Unix timestamp | Convert from epoch |
| `2014-03-02T07:13:30` | ISO format with T | Remove T, add space |
| `Mar 2, 2014 7:13 AM` | Text format | Parse and reformat |

**Python conversion**:
```python
import pandas as pd

df = pd.read_csv('data.csv')

# From various formats
df['datetime'] = pd.to_datetime(df['datetime'])
df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

df.to_csv('fixed_data.csv', index=False)
```

---

### Issue: Timezone problems

**Symptoms**:
- `percent_nocturnal` seems wrong
- Day/night split doesn't match expectations

**Solution**: Ensure all timestamps are in local time:
```python
import pandas as pd

df = pd.read_csv('data.csv')
df['datetime'] = pd.to_datetime(df['datetime'])

# Convert from UTC to local
df['datetime'] = df['datetime'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

df.to_csv('fixed_data.csv', index=False)
```

---

## Interaction Type Issues

### Issue: "Invalid interaction type"

**Symptoms**:
- Records ignored
- `user.ignored_records['interaction']` is high

**Common causes**:

| Your Value | Problem | Solution |
|------------|---------|----------|
| `CALL` | Uppercase | Convert to `call` |
| `SMS` | Wrong term | Convert to `text` |
| `voice` | Wrong term | Convert to `call` |
| `1` or `2` | Numeric codes | Map to strings |
| `MMS` | Not supported | Convert to `text` |

**Python fix**:
```python
# Create mapping
mapping = {
    'CALL': 'call', 'Call': 'call', 'voice': 'call', '1': 'call',
    'SMS': 'text', 'TEXT': 'text', 'MMS': 'text', '2': 'text'
}

df['interaction'] = df['interaction'].str.strip().map(mapping)
```

---

## Direction Issues

### Issue: "Invalid direction"

**Symptoms**:
- Records ignored
- `user.ignored_records['direction']` is high

**Common causes**:

| Your Value | Problem | Solution |
|------------|---------|----------|
| `IN` | Uppercase | Convert to `in` |
| `INCOMING` | Wrong term | Convert to `in` |
| `outgoing` | Wrong term | Convert to `out` |
| `1` or `2` | Numeric codes | Map to strings |
| `sent` | Wrong term | Convert to `out` |

**Python fix**:
```python
mapping = {
    'IN': 'in', 'INCOMING': 'in', 'received': 'in', '1': 'in',
    'OUT': 'out', 'OUTGOING': 'out', 'sent': 'out', '2': 'out'
}

df['direction'] = df['direction'].str.strip().map(mapping)
```

---

## Column Name Issues

### Issue: "Missing required columns"

**Symptoms**:
- Load fails immediately
- Error message lists missing columns

**Solution**: Rename columns to match exactly:
```python
column_mapping = {
    # Your column name: Bandicoot expected name
    'timestamp': 'datetime',
    'date_time': 'datetime',
    'type': 'interaction',
    'call_type': 'interaction',
    'dir': 'direction',
    'in_out': 'direction',
    'contact': 'correspondent_id',
    'number': 'correspondent_id',
    'phone': 'correspondent_id',
    'duration': 'call_duration',
    'length': 'call_duration',
    'tower': 'antenna_id',
    'cell': 'antenna_id',
    'lat': 'latitude',
    'lon': 'longitude',
    'lng': 'longitude'
}

df = df.rename(columns=column_mapping)
```

---

## Antenna Issues

### Issue: "Records missing location"

**Symptoms**:
- Warning about missing locations
- Spatial indicators return None
- `percent_records_missing_location` is high

**Causes and solutions**:

1. **No antenna file provided**:
   ```python
   # Add antenna file to load call
   user = bc.read_csv('user', 'data/', 'antennas.csv')  # Add this
   ```

2. **Antenna IDs don't match**:
   ```python
   # Check what IDs are in your records
   record_antennas = df['antenna_id'].unique()
   print("Record antennas:", record_antennas[:10])

   # Check what IDs are in antennas file
   antennas_df = pd.read_csv('antennas.csv')
   print("Antenna file IDs:", antennas_df['antenna_id'].unique()[:10])

   # Fix mismatches (e.g., case, whitespace, prefix)
   df['antenna_id'] = df['antenna_id'].str.strip().str.lower()
   ```

3. **Antennas file format wrong**:
   ```python
   # Required columns: antenna_id, latitude, longitude
   antennas_df = pd.read_csv('antennas.csv')
   antennas_df = antennas_df.rename(columns={
       'cell_id': 'antenna_id',
       'lat': 'latitude',
       'lon': 'longitude'
   })
   antennas_df.to_csv('antennas_fixed.csv', index=False)
   ```

---

### Issue: "Home not detected"

**Symptoms**:
- `user.has_home` is False
- `percent_at_home` returns None

**Causes**:

1. **No nighttime records with location**:
   ```python
   # Check nighttime records
   night_records = df[
       (pd.to_datetime(df['datetime']).dt.hour >= 19) |
       (pd.to_datetime(df['datetime']).dt.hour < 7)
   ]
   print(f"Night records: {len(night_records)}")
   print(f"Night records with antenna: {night_records['antenna_id'].notna().sum()}")
   ```

2. **Antenna data not loaded correctly**: See above

3. **Change night definition**:
   ```python
   import datetime
   user.night_start = datetime.time(21)  # 9 PM
   user.night_end = datetime.time(6)     # 6 AM
   user.recompute_home()
   ```

---

## Encoding Issues

### Issue: Special characters cause errors

**Symptoms**:
- `UnicodeDecodeError`
- Strange characters in data

**Solution**:
```python
# Try different encodings
for encoding in ['utf-8', 'latin-1', 'cp1252']:
    try:
        df = pd.read_csv('data.csv', encoding=encoding)
        print(f"Success with {encoding}")
        break
    except UnicodeDecodeError:
        continue

# Save with UTF-8
df.to_csv('fixed_data.csv', index=False, encoding='utf-8')
```

---

## Large File Issues

### Issue: Memory errors with large files

**Symptoms**:
- `MemoryError`
- System becomes unresponsive

**Solutions**:

1. **Process in chunks**:
   ```python
   chunks = pd.read_csv('large_file.csv', chunksize=100000)
   processed = []
   for chunk in chunks:
       # Process chunk
       chunk = fix_datetime(chunk)
       processed.append(chunk)

   df = pd.concat(processed)
   ```

2. **Filter unnecessary columns**:
   ```python
   usecols = ['datetime', 'interaction', 'direction', 'correspondent_id',
              'call_duration', 'antenna_id']
   df = pd.read_csv('data.csv', usecols=usecols)
   ```

3. **Sample data for testing**:
   ```python
   df = pd.read_csv('data.csv', nrows=10000)  # First 10k rows
   ```

---

## Duplicate Records

### Issue: Many duplicate records

**Symptoms**:
- Warning about duplicates
- Inflated record counts

**Solution**:
```python
# Remove exact duplicates
df = df.drop_duplicates()

# Or load with drop_duplicates option
user = bc.read_csv('user', 'data/', drop_duplicates=True)
```

---

## Correspondent ID Issues

### Issue: Empty or invalid correspondent IDs

**Symptoms**:
- `user.ignored_records['correspondent_id']` is high
- Number of contacts seems wrong

**Solution**:
```python
# Remove records with empty correspondent
df = df[df['correspondent_id'].notna()]
df = df[df['correspondent_id'] != '']

# Or fill with placeholder for GPS-only records
df['correspondent_id'] = df['correspondent_id'].fillna('unknown')
```

---

## Validation Checklist

Before loading data into Bandicoot:

- [ ] Datetime format is `YYYY-MM-DD HH:MM:SS`
- [ ] Interaction values are lowercase `call` or `text`
- [ ] Direction values are lowercase `in` or `out`
- [ ] All required columns present
- [ ] No NULL or N/A values (use empty instead)
- [ ] Antenna IDs match between records and antennas file
- [ ] File encoding is UTF-8
- [ ] File uses comma delimiter
