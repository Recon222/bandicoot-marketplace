---
description: Analyze spatial mobility indicators from phone antenna data
argument-hint: <user_id> <records_path> <antennas_path> [--groupby=week]
allowed-tools: Bash
---

# Bandicoot: Spatial Indicators Analysis

Compute spatial mobility indicators from phone records with antenna location data.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing the records CSV
- `antennas_path` (required): Path to antennas CSV file with coordinates
- `--groupby`: Aggregation level - `week` (default), `month`, `year`, or `none`

## Spatial Indicators Computed

| Indicator | Description |
|-----------|-------------|
| `number_of_antennas` | Unique locations visited |
| `entropy_of_antennas` | Diversity of places visited |
| `percent_at_home` | Time spent at detected home |
| `radius_of_gyration` | Typical mobility range (km) |
| `frequent_antennas` | Locations for 80% of time |
| `churn_rate` | Week-to-week location change |

## Execution

```python
import bandicoot as bc

# Load user with antenna data (required for spatial indicators)
user = bc.read_csv(
    '{user_id}',
    '{records_path}',
    '{antennas_path}',
    describe=True,
    warnings=True
)

groupby = '{groupby}' if '{groupby}' != 'none' else None

# Check data availability
print(f"\n=== Spatial Analysis Prerequisites ===")
print(f"Records: {len(user.records)}")
print(f"Antennas loaded: {len(user.antennas)}")
print(f"Has home: {user.has_home}")

if user.home:
    print(f"Home location: {user.home}")

# Calculate missing location percentage
from bandicoot.helper.tools import percent_records_missing_location
pct_missing = percent_records_missing_location(user)
print(f"Records missing location: {pct_missing:.1%}")

if pct_missing > 0.5:
    print("WARNING: More than 50% of records missing location data")
    print("Spatial indicators may be unreliable")

print(f"\n{'=' * 50}")
print(f"Spatial Indicators for {user.name}")
print('=' * 50)

# Location diversity
print("\n--- Location Diversity ---")
na = bc.spatial.number_of_antennas(user, groupby=groupby)
print(f"Number of antennas (unique locations): {na}")

ea = bc.spatial.entropy_of_antennas(user, groupby=groupby)
print(f"Entropy of antennas: {ea}")

ea_norm = bc.spatial.entropy_of_antennas(user, groupby=groupby, normalize=True)
print(f"Entropy of antennas (normalized 0-1): {ea_norm}")

# Home-based metrics
print("\n--- Home-Based Metrics ---")
if user.has_home:
    pah = bc.spatial.percent_at_home(user, groupby=groupby)
    print(f"Percent at home: {pah}")
else:
    print("Home not detected - percent_at_home unavailable")
    print("Tip: Need nighttime records with location data to detect home")

# Mobility range
print("\n--- Mobility Range ---")
rog = bc.spatial.radius_of_gyration(user, groupby=groupby)
print(f"Radius of gyration: {rog}")

# Frequent locations
print("\n--- Frequent Locations ---")
fa = bc.spatial.frequent_antennas(user, groupby=groupby)
print(f"Frequent antennas (80% of time): {fa}")

fa_90 = bc.spatial.frequent_antennas(user, groupby=groupby, percentage=0.9)
print(f"Frequent antennas (90% of time): {fa_90}")

# Location stability
print("\n--- Location Stability ---")
cr = bc.spatial.churn_rate(user)
print(f"Churn rate (week-to-week change): {cr}")

print(f"\n{'=' * 50}")
print("Spatial analysis complete!")

# Interpretation guide
print("\n=== Interpretation Guide ===")
print("- Radius of gyration: ~1-5km = local, ~10-50km = regional, >50km = traveler")
print("- Percent at home: >0.5 = home-based, <0.3 = mobile lifestyle")
print("- Frequent antennas: 2-3 typical (home + work + regular spots)")
print("- Churn rate: 0 = same pattern every week, 1 = completely different")
```

## Examples

### Basic Spatial Analysis

```
/bandicoot:analyze-spatial ego demo/data/ demo/data/antennas.csv
```

### Without Aggregation (Single Values)

```
/bandicoot:analyze-spatial ego demo/data/ demo/data/antennas.csv --groupby=none
```

### Monthly Aggregation

```
/bandicoot:analyze-spatial ego demo/data/ demo/data/antennas.csv --groupby=month
```

## Indicator Details

### number_of_antennas

Count of unique antenna/tower locations where the user had interactions. Higher
values indicate more mobility. Note: This measures antenna diversity, not
geographic distance.

### entropy_of_antennas

Shannon entropy of location distribution. Measures how evenly time is spent
across visited locations.

- Low entropy (0-1): Concentrated in few locations
- High entropy: Time spread evenly across many locations
- Normalized version (0-1) allows comparison across users

### percent_at_home

Fraction of interactions occurring at the detected home location. Home is
automatically detected as the most frequent nighttime (7pm-7am) location.

- High (>0.5): Home-based lifestyle
- Low (<0.3): Away from home frequently
- None: Insufficient nighttime location data to detect home

### radius_of_gyration

The equivalent distance of mass from the center of gravity for all visited
locations, measured in kilometers. This is the standard mobility range metric
from human mobility studies.

Typical values:
- 1-5 km: Local mobility (within city neighborhood)
- 5-20 km: Urban mobility (across city)
- 20-50 km: Regional mobility (commuter)
- 50+ km: Long-distance mobility (frequent traveler)

### frequent_antennas

Number of locations that account for a given percentage of time (default 80%).
Most people have 2-3 frequent locations (home, work, and one or two regular
spots).

### churn_rate

Measures week-to-week consistency of location patterns using cosine distance
between weekly location frequency vectors.

- 0: Identical location pattern every week
- 0.3-0.5: Typical weekly variation
- >0.7: High variability (changing locations)
- 1.0: Completely different locations each week

## Data Requirements

Spatial indicators require:

1. **Records with antenna_id**: Each record should have an `antenna_id` field
2. **Antennas file**: CSV with `antenna_id`, `latitude`, `longitude` columns
3. **Matching IDs**: The `antenna_id` values in records must match keys in
   antennas file

### Antennas CSV Format

```csv
antenna_id,latitude,longitude
tower_701,42.361013,-71.097868
tower_702,42.370849,-71.114613
tower_703,42.355800,-71.101200
```

## Troubleshooting

### All Spatial Indicators are None

1. Check that antennas_path points to a valid file
2. Verify antenna_id values match between records and antennas file
3. Run `/bandicoot:load` first to see data quality warnings

### Home Not Detected

Home detection requires:
- Records during night hours (7pm-7am by default)
- Those records must have valid antenna_id
- The antenna must have coordinates in the antennas file

### Radius of Gyration is 0

- Only one unique location in the data
- All records have the same antenna_id
- Check for data quality issues
