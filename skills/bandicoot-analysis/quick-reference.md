# Bandicoot Quick Reference Card

Fast reference for common Bandicoot commands and patterns.

## Loading Data

```bash
# Via slash command
/bandicoot:load <user_id> <records_path> [antennas_path] [--network]
```

```python
# Python
import bandicoot as bc

# Basic load
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')

# With network
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv', network=True)

# Full options
user = bc.read_csv(
    'user_id',
    'records_path/',
    antennas_path='antennas.csv',
    attributes_path='attributes/',
    recharges_path='recharges/',
    network=True,
    describe=True,
    warnings=True
)
```

## Running Analysis

```bash
# Via slash command
/bandicoot:analyze <user_id> <records_path> [antennas_path] [--groupby=week]
/bandicoot:quick-stats <user_id> <records_path>
```

```python
# All indicators
results = bc.utils.all(user, groupby='week', summary='default')

# Flattened for export
results = bc.utils.all(user, flatten=True)
```

## Individual Indicators

```python
bc.individual.active_days(user)
bc.individual.number_of_contacts(user)
bc.individual.call_duration(user)
bc.individual.interevent_time(user)
bc.individual.percent_nocturnal(user)
bc.individual.percent_initiated_interactions(user)
bc.individual.response_rate_text(user)
bc.individual.response_delay_text(user)
bc.individual.entropy_of_contacts(user)
bc.individual.balance_of_contacts(user)
bc.individual.interactions_per_contact(user)
bc.individual.percent_pareto_interactions(user)
bc.individual.percent_pareto_durations(user)
bc.individual.number_of_interactions(user)
```

## Spatial Indicators

```python
bc.spatial.number_of_antennas(user)
bc.spatial.entropy_of_antennas(user)
bc.spatial.percent_at_home(user)
bc.spatial.radius_of_gyration(user)
bc.spatial.frequent_antennas(user)
bc.spatial.churn_rate(user)
```

## Network Indicators

```python
# Requires network=True when loading
bc.network.clustering_coefficient_unweighted(user)
bc.network.clustering_coefficient_weighted(user)
bc.network.assortativity_indicators(user)
bc.network.assortativity_attributes(user)
bc.network.matrix_directed_weighted(user)
bc.network.matrix_index(user)
```

## Recharge Indicators

```python
# Requires recharges_path when loading
bc.recharge.amount_recharges(user)
bc.recharge.number_of_recharges(user)
bc.recharge.interevent_time_recharges(user)
bc.recharge.percent_pareto_recharges(user)
bc.recharge.average_balance_recharges(user)
```

## Export

```python
# To CSV
bc.to_csv(results, 'output.csv')
bc.to_csv([result1, result2], 'comparison.csv')

# To JSON
bc.to_json(results, 'output.json')

# Flatten nested dict
flat = bc.utils.flatten(results)
```

## Visualization

```python
# Start web dashboard
bc.visualization.run(user, port=4242)

# Export static files
bc.visualization.export(user, 'viz_output/')
```

## Common Parameters

| Parameter | Values | Default |
|-----------|--------|---------|
| `groupby` | `'week'`, `'month'`, `'year'`, `None` | `'week'` |
| `summary` | `'default'`, `'extended'`, `None` | `'default'` |
| `direction` | `'in'`, `'out'`, `None` | `None` |
| `interaction` | `'call'`, `'text'`, `'callandtext'` | varies |
| `split_week` | `True`, `False` | `False` |
| `split_day` | `True`, `False` | `False` |

## CSV Formats

### Records (required columns)
```
datetime,interaction,direction,correspondent_id,call_duration,antenna_id
2014-03-02 07:13:30,call,out,contact_5,120,tower_701
```

### Antennas
```
antenna_id,latitude,longitude
tower_701,42.361013,-71.097868
```

### Recharges
```
datetime,amount,retailer_id
2014-03-01 10:00:00,500,retailer_01
```

## User Object Quick Checks

```python
len(user.records)      # Number of records
user.start_time        # First record datetime
user.end_time          # Last record datetime
user.has_call          # Has call records?
user.has_text          # Has text records?
user.has_home          # Home location detected?
user.has_network       # Network loaded?
user.ignored_records   # Records filtered out
user.describe()        # Print summary
```

## Environment Check

```bash
# Verify installation
conda run -n bandicoot python -c "import bandicoot as bc; print(bc.__version__)"
```

## Slash Commands Quick List

| Command | Purpose |
|---------|---------|
| `/bandicoot:load` | Load user data |
| `/bandicoot:analyze` | Full analysis |
| `/bandicoot:analyze-individual` | Individual indicators |
| `/bandicoot:analyze-spatial` | Spatial indicators |
| `/bandicoot:analyze-network` | Network indicators |
| `/bandicoot:analyze-recharge` | Recharge indicators |
| `/bandicoot:quick-stats` | Quick summary |
| `/bandicoot:export` | Export results |
| `/bandicoot:visualize` | Start dashboard |
| `/bandicoot:describe` | User description |
| `/bandicoot:validate` | Validate data |
| `/bandicoot:compare` | Compare users |
| `/bandicoot:batch` | Batch processing |
| `/bandicoot:generate-sample` | Generate test data |
