# Bandicoot Indicator Meanings

Plain-language explanations of what each Bandicoot indicator measures and reveals
about user behavior.

## Individual Behavior Indicators

### Activity Measures

| Indicator | Plain Meaning |
|-----------|---------------|
| `active_days` | How many days the person used their phone |
| `number_of_interactions` | Total count of calls and texts |
| `number_of_contacts` | How many different people they communicated with |

### Call Behavior

| Indicator | Plain Meaning |
|-----------|---------------|
| `call_duration` | How long their phone calls typically last |
| `percent_initiated_interactions` | How often they make calls vs receive them |

### Text Behavior

| Indicator | Plain Meaning |
|-----------|---------------|
| `response_rate_text` | How reliably they respond to text messages |
| `response_delay_text` | How quickly they respond to texts |
| `percent_initiated_conversations` | How often they start conversations |

### Social Patterns

| Indicator | Plain Meaning |
|-----------|---------------|
| `entropy_of_contacts` | Whether they spread attention evenly across contacts or focus on a few |
| `balance_of_contacts` | Whether relationships are mutual or one-sided |
| `interactions_per_contact` | How much they communicate with each contact |
| `percent_pareto_interactions` | What fraction of contacts get most of their attention |
| `percent_pareto_durations` | What fraction of contacts get most of their call time |

### Temporal Patterns

| Indicator | Plain Meaning |
|-----------|---------------|
| `interevent_time` | How much time passes between phone uses |
| `percent_nocturnal` | What fraction of activity happens at night |

---

## Mobility Indicators

| Indicator | Plain Meaning |
|-----------|---------------|
| `number_of_antennas` | How many different places they use their phone |
| `entropy_of_antennas` | Whether they visit many places equally or stay mostly in one spot |
| `percent_at_home` | How much time they spend at home |
| `radius_of_gyration` | How far they typically travel from their usual center |
| `frequent_antennas` | How many places account for most of their time |
| `churn_rate` | How much their routine changes from week to week |

---

## Network Indicators

| Indicator | Plain Meaning |
|-----------|---------------|
| `clustering_coefficient_unweighted` | How many of their contacts also know each other |
| `clustering_coefficient_weighted` | Same, but weighted by communication frequency |
| `assortativity_indicators` | How similar they are to the people they communicate with |
| `assortativity_attributes` | Whether their contacts share their characteristics |

---

## Recharge Indicators

| Indicator | Plain Meaning |
|-----------|---------------|
| `amount_recharges` | How much money they typically add to their phone |
| `number_of_recharges` | How often they top up their phone balance |
| `interevent_time_recharges` | Time between top-ups |
| `percent_pareto_recharges` | Whether they make many small or few large recharges |
| `average_balance_recharges` | Estimated typical balance they maintain |

---

## What the Numbers Mean

### Low vs High Values

| Indicator | Low Value Suggests | High Value Suggests |
|-----------|-------------------|---------------------|
| active_days | Infrequent user | Daily user |
| number_of_contacts | Small social circle | Large network |
| call_duration | Brief conversations | Long conversations |
| percent_nocturnal | Daytime schedule | Night owl |
| entropy_of_contacts | Focused on few people | Spread across many |
| radius_of_gyration | Stays local | Travels widely |
| percent_at_home | Away often | Home-based |
| clustering_coefficient | Disconnected contacts | Tight-knit network |

### Typical Ranges

| Indicator | What's "Normal" |
|-----------|-----------------|
| active_days | 4-6 days per week |
| number_of_contacts | 10-50 people |
| call_duration mean | 60-180 seconds |
| percent_nocturnal | 20-40% |
| radius_of_gyration | 5-20 km |
| percent_at_home | 30-60% |
| clustering_coefficient | 0.1-0.4 |

---

## Reporting Variables Explained

These aren't behavioral indicators but describe the data itself:

| Variable | What It Tells You |
|----------|-------------------|
| `number_of_records` | How much data you have |
| `bins` | Time periods analyzed |
| `has_call` / `has_text` | What data types are present |
| `has_home` | Whether home location was detected |
| `percent_records_missing_location` | Data quality for spatial analysis |
| `ignored_records` | How much data was invalid |

---

## Reading the Result Structure

### Single Value (groupby=None)

```python
{'allweek': {'allday': {'call': 15.0}}}
```
Means: 15 unique call contacts in total

### Distribution (groupby='week')

```python
{'allweek': {'allday': {'call': {'mean': 5.0, 'std': 1.2}}}}
```
Means: Average 5 call contacts per week, with weekly variation of 1.2

### Summary Stats

```python
{'mean': 125.5, 'std': 45.2, 'min': 10, 'max': 450}
```
Means: Average 125.5 (e.g., seconds), ranging from 10 to 450

---

## Questions These Indicators Answer

| Question | Indicator(s) to Check |
|----------|----------------------|
| How social is this person? | number_of_contacts, interactions_per_contact |
| Are they a day or night person? | percent_nocturnal |
| Do they travel a lot? | radius_of_gyration, churn_rate |
| Do they work from home? | percent_at_home |
| Are their relationships balanced? | balance_of_contacts |
| Do they have a close inner circle? | percent_pareto_interactions |
| How responsive are they? | response_rate_text, response_delay_text |
| Do their contacts know each other? | clustering_coefficient |
