---
name: bandicoot-analysis
description: |
  Use this skill when analyzing mobile phone metadata (Call Detail Records/CDRs),
  computing behavioral indicators from communication patterns, mobility patterns,
  or working with the Bandicoot Python library.

  <example>
  Context: User wants to analyze phone records
  user: "Analyze the call records in demo/data/"
  assistant: "[Uses this skill to load data, compute indicators, and explain results]"
  <commentary>
  The request involves CDR analysis, triggering Bandicoot expertise.
  </commentary>
  </example>

  <example>
  Context: User asks about communication patterns
  user: "What's the radius of gyration for this user?"
  assistant: "[Uses skill to compute and explain the spatial indicator]"
  <commentary>
  Specific Bandicoot indicator mentioned - skill provides context.
  </commentary>
  </example>

  <example>
  Context: User has CSV files with phone records
  user: "I have phone call records in CSV format. Can you analyze them?"
  assistant: "[Uses skill to validate format, load with Bandicoot, and run analysis]"
  <commentary>
  CSV phone records indicate CDR analysis task.
  </commentary>
  </example>

  <example>
  Context: User wants to understand network behavior
  user: "How many unique contacts does this person communicate with?"
  assistant: "[Uses skill to compute number_of_contacts indicator]"
  <commentary>
  Communication contact analysis maps to Bandicoot individual indicators.
  </commentary>
  </example>

allowed-tools: Bash, Read, Glob
---

# Bandicoot Analysis Skill

You are an expert in analyzing mobile phone metadata using **Bandicoot**, a Python
toolbox developed at MIT for extracting behavioral indicators from Call Detail
Records (CDRs). Bandicoot analyzes communication patterns, mobility behavior, and
social networks from phone metadata.

## Environment Setup

**CRITICAL**: Always use `conda run` for cross-platform compatibility (especially on Windows).
Never use `conda activate` in scripts as it requires shell initialization.

### Verify Environment

```bash
conda run -n bandicoot python -c "import bandicoot as bc; print(f'Bandicoot {bc.__version__} ready')"
```

### Alternative Check (if conda unavailable)

```bash
python -c "import bandicoot as bc; print(f'Bandicoot {bc.__version__}')"
```

## CRITICAL: Direct Function Calls, Not Wrapper Scripts

Bandicoot is a complete analysis toolkit. The code examples in this skill
documentation demonstrate Bandicoot's API - they should be executed DIRECTLY
using inline Python commands, not saved as separate script files.

**CORRECT approach** - Execute inline:
```bash
conda run -n bandicoot python -c "
import bandicoot as bc
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')
print(bc.individual.number_of_contacts(user, groupby=None))
"
```

**INCORRECT approach** - Do NOT create wrapper scripts:
```python
# DON'T create a file like "analyze_contacts.py" containing:
import bandicoot as bc
def analyze_contacts(user_id, path):
    user = bc.read_csv(user_id, path)
    return bc.individual.number_of_contacts(user)
```

All Bandicoot functions shown below are built-in. Call them directly.

## Core Commands Reference

### Loading Data

The primary data loading function is `bc.read_csv()`:

```python
import bandicoot as bc

# Basic load - user_id is filename without .csv extension
user = bc.read_csv('user_id', 'records_directory/', 'antennas.csv')

# Full options
user = bc.read_csv(
    'user_id',                    # User identifier (filename without .csv)
    'records_path/',              # Directory containing {user_id}.csv
    antennas_path='antennas.csv', # Optional: antenna location file
    attributes_path='attributes/',# Optional: user attributes directory
    recharges_path='recharges/',  # Optional: recharge data directory
    network=True,                 # Load correspondent network for network analysis
    describe=True,                # Print user description after loading
    warnings=True,                # Show data quality warnings
    errors=False,                 # Return tuple (user, bad_records) if True
    drop_duplicates=False         # Remove duplicate records
)
```

**Important**: The records file must be named `{user_id}.csv` inside the records directory.

### Computing All Indicators

```python
# Run all indicators with weekly aggregation
results = bc.utils.all(user, groupby='week', summary='default')

# Run with different options
results = bc.utils.all(
    user,
    groupby='week',       # 'week', 'month', 'year', or None
    summary='default',    # 'default', 'extended', or None
    network=False,        # Include network indicators
    split_week=False,     # Separate weekday/weekend
    split_day=False,      # Separate day/night
    filter_empty=True,    # Filter empty time periods
    attributes=True,      # Include user attributes
    flatten=False         # Flatten nested dict structure
)
```

### Individual Indicators

Communication behavior metrics from `bc.individual`:

```python
# Active days in period
bc.individual.active_days(user)

# Number of unique contacts
bc.individual.number_of_contacts(user)
bc.individual.number_of_contacts(user, direction='out')  # Outgoing only
bc.individual.number_of_contacts(user, more=5)           # Contacts with >5 interactions

# Call duration statistics
bc.individual.call_duration(user)
bc.individual.call_duration(user, direction='in')  # Incoming only

# Time between interactions
bc.individual.interevent_time(user)

# Nocturnal activity (7pm-7am by default)
bc.individual.percent_nocturnal(user)

# Interaction initiation
bc.individual.percent_initiated_interactions(user)  # Calls only
bc.individual.percent_initiated_conversations(user) # Conversations (calls + texts)

# Text messaging behavior
bc.individual.response_rate_text(user)   # Fraction of texts responded to
bc.individual.response_delay_text(user)  # Time to respond to texts

# Contact distribution
bc.individual.entropy_of_contacts(user)
bc.individual.entropy_of_contacts(user, normalize=True)  # 0-1 range
bc.individual.balance_of_contacts(user)  # Out/total ratio per contact
bc.individual.interactions_per_contact(user)

# Pareto analysis (80/20 rule)
bc.individual.percent_pareto_interactions(user)  # % contacts for 80% interactions
bc.individual.percent_pareto_durations(user)     # % contacts for 80% call time

# Total interactions
bc.individual.number_of_interactions(user)
bc.individual.number_of_interactions(user, direction='in')
bc.individual.number_of_interactions(user, direction='out')
```

### Spatial Indicators

Mobility metrics from `bc.spatial`:

```python
# Number of unique locations
bc.spatial.number_of_antennas(user)

# Location entropy (diversity of places visited)
bc.spatial.entropy_of_antennas(user)
bc.spatial.entropy_of_antennas(user, normalize=True)

# Home-based metrics (requires home detection)
bc.spatial.percent_at_home(user)

# Radius of gyration (mobility range in km)
bc.spatial.radius_of_gyration(user)

# Frequent locations (locations for X% of time)
bc.spatial.frequent_antennas(user)
bc.spatial.frequent_antennas(user, percentage=0.9)  # 90% instead of 80%

# Location churn (week-to-week location change)
bc.spatial.churn_rate(user)
```

### Network Indicators

Social network metrics from `bc.network` (requires `network=True` when loading):

```python
# Clustering coefficients
bc.network.clustering_coefficient_unweighted(user)
bc.network.clustering_coefficient_weighted(user)
bc.network.clustering_coefficient_weighted(user, interaction='call')

# Assortativity (similarity with contacts)
bc.network.assortativity_indicators(user)  # Compare all indicators
bc.network.assortativity_attributes(user)  # Compare attributes

# Interaction matrices
bc.network.matrix_directed_weighted(user)
bc.network.matrix_directed_weighted(user, interaction='call')
bc.network.matrix_directed_unweighted(user)
bc.network.matrix_undirected_weighted(user)
bc.network.matrix_undirected_unweighted(user)

# Matrix index (node labels)
bc.network.matrix_index(user)  # Returns ['ego', 'contact1', 'contact2', ...]
```

### Recharge Indicators

Financial top-up metrics from `bc.recharge` (requires recharges data):

```python
# Recharge amount distribution
bc.recharge.amount_recharges(user)

# Number of recharges
bc.recharge.number_of_recharges(user)

# Time between recharges
bc.recharge.interevent_time_recharges(user)

# Pareto concentration of recharge amounts
bc.recharge.percent_pareto_recharges(user)

# Average daily balance estimate
bc.recharge.average_balance_recharges(user)
```

### Exporting Results

```python
# Export to CSV - accepts single result or list
bc.to_csv(results, 'output.csv')
bc.to_csv([results1, results2], 'comparison.csv')  # Multiple users

# Export to JSON
bc.to_json(results, 'output.json')

# Flatten nested structure for analysis
flat = bc.utils.flatten(results)
```

### Visualization

```python
# Start interactive dashboard (D3.js based)
bc.visualization.run(user, port=4242)
# Access at http://localhost:4242

# Export static visualization files
bc.visualization.export(user, 'viz_output/')
```

## Parameter Reference

### Groupby Options

| Value | Description |
|-------|-------------|
| `'week'` | Aggregate by week (default) |
| `'month'` | Aggregate by month |
| `'year'` | Aggregate by year |
| `None` | No aggregation, compute on all records |

### Summary Options

| Value | Description |
|-------|-------------|
| `'default'` | Returns mean and std |
| `'extended'` | Returns mean, std, median, min, max, skewness, kurtosis |
| `None` | Returns raw distribution |

### Interaction Types

| Value | Description |
|-------|-------------|
| `'call'` | Voice calls only |
| `'text'` | Text messages only |
| `'callandtext'` | Both calls and texts |

### Direction Options

| Value | Description |
|-------|-------------|
| `'in'` | Incoming interactions |
| `'out'` | Outgoing interactions |
| `None` | All interactions |

## Data Format Requirements

### Records CSV Format

Required columns: `datetime`, `interaction`, `direction`, `correspondent_id`
Optional columns: `call_duration`, `antenna_id`, `latitude`, `longitude`

```csv
interaction,direction,correspondent_id,datetime,call_duration,antenna_id
call,out,contact_5,2014-03-02 07:13:30,120,tower_701
text,in,contact_12,2014-03-02 09:45:00,,tower_702
call,in,contact_5,2014-03-02 10:30:00,45,tower_701
```

**Column specifications:**
- `interaction`: `'call'` or `'text'`
- `direction`: `'in'` or `'out'`
- `correspondent_id`: Unique identifier for the contact
- `datetime`: Format `YYYY-MM-DD HH:MM:SS`
- `call_duration`: Duration in seconds (empty for texts)
- `antenna_id`: Tower identifier (optional, for spatial analysis)

### Antennas CSV Format

```csv
antenna_id,latitude,longitude
tower_701,42.361013,-71.097868
tower_702,42.370849,-71.114613
```

### Recharges CSV Format

```csv
datetime,amount,retailer_id
2014-03-01 10:00:00,500,retailer_01
2014-03-15 14:30:00,1000,retailer_02
```

### Attributes CSV Format

```csv
key,value
age,25
gender,M
income,medium
```

## User Object Properties

After loading, the `User` object provides:

```python
# Basic properties
user.name                    # User identifier
user.records                 # List of Record objects
user.antennas               # Dict of antenna locations
user.attributes             # Dict of user attributes
user.recharges              # List of Recharge objects
user.network                # Dict of correspondent User objects

# Time range
user.start_time             # First record datetime
user.end_time               # Last record datetime

# Night definition (for percent_nocturnal)
user.night_start            # Default: datetime.time(19) (7 PM)
user.night_end              # Default: datetime.time(7) (7 AM)

# Weekend definition
user.weekend                # Default: [6, 7] (Saturday, Sunday)

# Status flags
user.has_call               # True if user has call records
user.has_text               # True if user has text records
user.has_home               # True if home location detected
user.has_antennas           # True if antenna locations loaded
user.has_attributes         # True if attributes loaded
user.has_recharges          # True if recharges loaded
user.has_network            # True if network loaded

# Home location
user.home                   # Position object of detected home

# Data quality
user.ignored_records        # Dict counting records filtered out

# Network statistics (when network=True)
user.percent_outofnetwork_calls
user.percent_outofnetwork_texts
user.percent_outofnetwork_contacts
user.percent_outofnetwork_call_durations

# Methods
user.describe()             # Print summary to stdout
user.recompute_home()       # Recalculate home location
user.reset_cache()          # Clear internal cache
```

## Result Structure

Results from `bc.utils.all()` follow this nested structure:

```python
{
    'name': 'user_id',
    'reporting': {
        'version': '0.6.0',
        'groupby': 'week',
        'number_of_records': 314,
        # ... other metadata
    },
    'active_days': {
        'allweek': {
            'allday': {
                'callandtext': {'mean': 5.5, 'std': 1.2}
            }
        }
    },
    'call_duration': {
        'allweek': {
            'allday': {
                'call': {
                    'mean': {'mean': 125.5, 'std': 45.2},
                    'std': {'mean': 80.1, 'std': 30.5}
                }
            }
        }
    }
    # ... other indicators
}
```

### Flattened Keys

When exported to CSV, keys are flattened with `__` separator:

```
call_duration__allweek__allday__call__mean__mean
percent_nocturnal__allweek__allday__callandtext
radius_of_gyration__allweek__allday__mean
```

## Troubleshooting

### Common Issues

1. **FileNotFoundError**: Check that records file exists at `{records_path}/{user_id}.csv`

2. **Empty results / None values**:
   - Verify datetime format is `YYYY-MM-DD HH:MM:SS`
   - Check that interaction is `'call'` or `'text'`
   - Ensure direction is `'in'` or `'out'`

3. **Missing location warnings**:
   - Verify antennas file exists and path is correct
   - Check that `antenna_id` in records matches keys in antennas file

4. **Network indicators are None**:
   - Ensure `network=True` when calling `bc.read_csv()`
   - Network requires correspondent CSV files in same directory

5. **Home location is None**:
   - Need nighttime records (7pm-7am) with antenna data
   - At least some records must have location information

6. **Recharge indicators not computed**:
   - Check recharges file exists at `{recharges_path}/{user_id}.csv`
   - Verify datetime format in recharges file

### Data Quality Checks

```python
# Quick diagnostic
print(f"Records: {len(user.records)}")
print(f"Date range: {user.start_time} to {user.end_time}")
print(f"Has calls: {user.has_call}")
print(f"Has texts: {user.has_text}")
print(f"Has home: {user.has_home}")
print(f"Has network: {user.has_network}")
print(f"Antennas: {len(user.antennas)}")
print(f"Ignored records: {user.ignored_records}")

# Full description
user.describe()
```

### Validation Script (Execute Inline)

Run this validation inline to check data before full analysis:

```python
import bandicoot as bc
import os

def validate_user_data(user_id, records_path, antennas_path=None):
    """Validate user data before analysis."""
    records_file = os.path.join(records_path, f"{user_id}.csv")

    # Check records file
    if not os.path.exists(records_file):
        print(f"ERROR: Records file not found: {records_file}")
        return False

    # Check antennas file
    if antennas_path and not os.path.exists(antennas_path):
        print(f"WARNING: Antennas file not found: {antennas_path}")

    # Try loading with warnings
    try:
        user = bc.read_csv(user_id, records_path, antennas_path,
                          describe=True, warnings=True)
        print(f"SUCCESS: Loaded {len(user.records)} records")
        return True
    except Exception as e:
        print(f"ERROR: Failed to load - {e}")
        return False
```

## Best Practices

1. **Always verify environment** before running analysis
2. **Use `describe=True`** when loading to see data summary
3. **Check `user.ignored_records`** for data quality issues
4. **Start with `groupby=None`** to see raw values
5. **Export both CSV and JSON** - CSV for analysis, JSON for inspection
6. **Use `network=True`** only when needed (slower loading)
7. **Validate data format** before processing large batches

## Example Workflow

```python
import bandicoot as bc

# 1. Load user data
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv',
                   describe=True, warnings=True)

# 2. Quick check
print(f"Loaded {len(user.records)} records")
print(f"Date range: {user.start_time} to {user.end_time}")

# 3. Run analysis
results = bc.utils.all(user, groupby='week', summary='default')

# 4. Export results
bc.to_csv(results, 'analysis_results.csv')
bc.to_json(results, 'analysis_results.json')

# 5. Inspect specific indicators
print(f"Active days: {results['active_days']}")
print(f"Number of contacts: {results['number_of_contacts']}")
print(f"Radius of gyration: {results['radius_of_gyration']}")
```
