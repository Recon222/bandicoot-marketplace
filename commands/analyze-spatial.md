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

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Spatial Indicator Commands

All functions are in `bc.spatial` module:

| Command | Returns |
|---------|---------|
| `bc.spatial.number_of_antennas(user)` | Unique locations visited |
| `bc.spatial.entropy_of_antennas(user)` | Location diversity (Shannon entropy) |
| `bc.spatial.entropy_of_antennas(user, normalize=True)` | Normalized entropy (0-1) |
| `bc.spatial.percent_at_home(user)` | Time at detected home % |
| `bc.spatial.radius_of_gyration(user)` | Mobility range in km |
| `bc.spatial.frequent_antennas(user)` | Locations for 80% of time |
| `bc.spatial.frequent_antennas(user, percentage=0.9)` | Locations for 90% of time |
| `bc.spatial.churn_rate(user)` | Week-to-week location change |

All accept `groupby` parameter: `bc.spatial.radius_of_gyration(user, groupby='week')`

## Workflow

### 1. Load User with Antennas

```
user = bc.read_csv('user_id', 'path/', 'antennas.csv')
```

Antennas file is required for spatial indicators.

### 2. Check Data Quality

- `len(user.antennas)` - antennas loaded
- `user.has_home` - True if home detected
- `user.home` - home antenna location
- Check missing location percentage with helper function

### 3. Run Indicators

Run specific spatial indicators or use `bc.utils.all(user)` for all.

## Data Requirements

### Records CSV
Must have `antenna_id` column linking to antennas file.

### Antennas CSV Format
```csv
antenna_id,latitude,longitude
tower_701,42.361013,-71.097868
tower_702,42.370849,-71.114613
```

## Interpretation Guide

### number_of_antennas
Unique antenna locations visited. Higher = more mobility.

### entropy_of_antennas
Shannon entropy of location distribution.

| Value (normalized) | Interpretation |
|--------------------|----------------|
| 0 - 0.3 | Concentrated (few locations) |
| 0.3 - 0.7 | Moderate diversity |
| 0.7 - 1.0 | High diversity |

### percent_at_home
Fraction at detected home (nighttime mode location).

| Value | Interpretation |
|-------|----------------|
| > 0.5 | Home-based lifestyle |
| 0.3-0.5 | Balanced |
| < 0.3 | Mobile lifestyle |
| None | Home not detected |

### radius_of_gyration
Mobility range in kilometers (standard mobility metric).

| Value | Interpretation |
|-------|----------------|
| 1-5 km | Local (neighborhood) |
| 5-20 km | Urban (city-wide) |
| 20-50 km | Regional (commuter) |
| > 50 km | Long-distance traveler |

### frequent_antennas
Locations accounting for 80% of time. Most people: 2-3 (home + work + regular spots).

### churn_rate
Week-to-week location pattern change (cosine distance).

| Value | Interpretation |
|-------|----------------|
| 0 | Identical weekly pattern |
| 0.3-0.5 | Typical variation |
| > 0.7 | High variability |
| 1.0 | Completely different each week |

## Examples

Basic spatial analysis:
```
/bandicoot:analyze-spatial ego demo/data/ demo/data/antennas.csv
```

Single values (no aggregation):
```
/bandicoot:analyze-spatial ego demo/data/ demo/data/antennas.csv --groupby=none
```

Monthly aggregation:
```
/bandicoot:analyze-spatial ego demo/data/ demo/data/antennas.csv --groupby=month
```

## Troubleshooting

**All spatial indicators are None**
- Check antennas file path is correct
- Verify antenna_id values match between records and antennas file
- Run `/bandicoot:load` to see data quality warnings

**Home not detected**
Home detection requires:
- Records during night hours (7pm-7am)
- Those records must have valid antenna_id
- Antenna must have coordinates in antennas file

**Radius of gyration is 0**
- Only one unique location in data
- All records have same antenna_id
- Check for data quality issues

**High missing location percentage**
- Some records lack antenna_id
- antenna_id values not found in antennas file
- Spatial indicators may be unreliable if > 50% missing
