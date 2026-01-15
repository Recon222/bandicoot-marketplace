# Bandicoot CSV Format Reference

Detailed specifications for all CSV file formats used by Bandicoot.

## Records CSV

The primary data file containing communication records.

### Column Specifications

| Column | Required | Type | Valid Values | Notes |
|--------|----------|------|--------------|-------|
| `datetime` | Yes | string | `YYYY-MM-DD HH:MM:SS` | Must include leading zeros |
| `interaction` | Yes | string | `call`, `text`, empty | Lowercase only |
| `direction` | Yes | string | `in`, `out` | Lowercase only |
| `correspondent_id` | Yes | string | any non-empty | Unique contact identifier |
| `call_duration` | No | integer | >= 0 | Seconds; empty for texts |
| `antenna_id` | No | string | any | Cell tower identifier |
| `latitude` | No | float | -90 to 90 | Direct GPS coordinate |
| `longitude` | No | float | -180 to 180 | Direct GPS coordinate |

### Examples

**Minimal valid records**:
```csv
datetime,interaction,direction,correspondent_id
2014-03-02 07:13:30,call,out,contact_5
2014-03-02 09:45:00,text,in,contact_12
```

**Full records with all fields**:
```csv
datetime,interaction,direction,correspondent_id,call_duration,antenna_id
2014-03-02 07:13:30,call,out,contact_5,120,tower_701
2014-03-02 09:45:00,text,in,contact_12,,tower_702
2014-03-02 10:30:00,call,in,contact_5,45,tower_701
```

**With GPS coordinates (no antenna file needed)**:
```csv
datetime,interaction,direction,correspondent_id,call_duration,latitude,longitude
2014-03-02 07:13:30,call,out,contact_5,120,42.361013,-71.097868
2014-03-02 09:45:00,text,in,contact_12,,,
```

### Datetime Format

The datetime format must be exactly `YYYY-MM-DD HH:MM:SS`:

| Component | Format | Example |
|-----------|--------|---------|
| Year | 4 digits | 2014 |
| Month | 2 digits with leading zero | 03 |
| Day | 2 digits with leading zero | 02 |
| Hour | 2 digits, 24-hour format | 07, 19 |
| Minute | 2 digits with leading zero | 13, 05 |
| Second | 2 digits with leading zero | 30, 00 |

**Valid examples**:
- `2014-03-02 07:13:30`
- `2014-12-31 23:59:59`
- `2014-01-01 00:00:00`

**Invalid examples**:
- `2014-3-2 7:13:30` (missing leading zeros)
- `03/02/2014 07:13:30` (wrong format)
- `2014-03-02T07:13:30` (T separator)
- `1393749210` (unix timestamp)

### Interaction Values

| Value | Description |
|-------|-------------|
| `call` | Voice call |
| `text` | SMS/text message |
| (empty) | GPS point or other non-communication record |

Must be **lowercase**.

### Direction Values

| Value | Description |
|-------|-------------|
| `in` | Incoming (received) |
| `out` | Outgoing (sent/made) |

Must be **lowercase**.

---

## Antennas CSV

Maps antenna identifiers to geographic coordinates.

### Column Specifications

| Column | Required | Type | Valid Values |
|--------|----------|------|--------------|
| `antenna_id` | Yes | string | Must match records |
| `latitude` | Yes | float | -90 to 90 |
| `longitude` | Yes | float | -180 to 180 |

### Example

```csv
antenna_id,latitude,longitude
tower_701,42.361013,-71.097868
tower_702,42.370849,-71.114613
tower_703,42.355800,-71.101200
```

### Notes

- `antenna_id` must **exactly match** values in records file
- String matching is case-sensitive
- Check for trailing whitespace
- Coordinates should be in decimal degrees (not DMS)

---

## Recharges CSV

Mobile phone top-up/recharge records.

### Column Specifications

| Column | Required | Type | Valid Values |
|--------|----------|------|--------------|
| `datetime` | Yes | string | `YYYY-MM-DD HH:MM:SS` or `YYYY-MM-DD` |
| `amount` | Yes | float | >= 0 |
| `retailer_id` | No | string | any |

### Example

```csv
datetime,amount,retailer_id
2014-03-01 10:00:00,500,retailer_01
2014-03-15 14:30:00,1000,retailer_02
2014-03-20,250,retailer_01
```

### Notes

- Datetime can be date-only (`YYYY-MM-DD`)
- Amount is typically in local currency units
- File must be named `{user_id}.csv` in the recharges directory

---

## Attributes CSV

User metadata in key-value format.

### Column Specifications

| Column | Required | Type |
|--------|----------|------|
| `key` | Yes | string |
| `value` | Yes | string |

### Example

```csv
key,value
age,25
gender,M
income,medium
location,urban
occupation,student
```

### Notes

- All values stored as strings
- File must be named `{user_id}.csv` in attributes directory
- Can include any custom attributes

---

## File Encoding

- **Recommended**: UTF-8
- **Alternative**: ASCII, Latin-1

```python
# Reading with explicit encoding
with open('records.csv', 'r', encoding='utf-8') as f:
    ...

# In pandas
df = pd.read_csv('records.csv', encoding='utf-8')
```

---

## Delimiter

- **Default**: Comma (`,`)
- No support for other delimiters in standard functions

If your data uses different delimiter:
```python
import pandas as pd
df = pd.read_csv('data.csv', delimiter=';')  # or '\t' for tabs
df.to_csv('converted.csv', index=False)  # Saves with comma
```

---

## Quoting

- Fields containing commas must be quoted
- Both single and double quotes supported

**Example**:
```csv
datetime,interaction,direction,correspondent_id
2014-03-02 07:13:30,call,out,"contact,with,commas"
```

---

## Empty Values

- Empty cells are read as `None` in Bandicoot
- Use empty string, not "NULL", "N/A", or "None"

**Correct**:
```csv
datetime,interaction,direction,correspondent_id,call_duration
2014-03-02 07:13:30,text,in,contact_5,
```

**Incorrect**:
```csv
datetime,interaction,direction,correspondent_id,call_duration
2014-03-02 07:13:30,text,in,contact_5,NULL
```

---

## Line Endings

- Unix (`\n`) preferred
- Windows (`\r\n`) also supported
- Mac Classic (`\r`) may cause issues

---

## File Naming Convention

For multi-user analysis:

| File Type | Naming Pattern | Example |
|-----------|----------------|---------|
| Records | `{user_id}.csv` | `user123.csv` |
| Recharges | `{user_id}.csv` | `user123.csv` |
| Attributes | `{user_id}.csv` | `user123.csv` |
| Antennas | Any name | `antennas.csv` |

The `user_id` in `bc.read_csv()` must match the filename (without `.csv`).
