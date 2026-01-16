---
description: Analyze individual communication behavior indicators
argument-hint: <user_id> <records_path> [--groupby=week]
allowed-tools: Bash
---

# Bandicoot: Individual Indicators Analysis

Compute individual communication behavior indicators from phone records.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing the records CSV
- `--groupby`: Aggregation level - `week` (default), `month`, `year`, or `none`
- `--summary`: Summary type - `default`, `extended`, or `none`

## Individual Indicators Computed

| Indicator | Description |
|-----------|-------------|
| `active_days` | Days with any activity |
| `number_of_contacts` | Unique contacts |
| `call_duration` | Call length distribution |
| `interevent_time` | Time between interactions |
| `percent_nocturnal` | Nighttime activity percentage |
| `percent_initiated_interactions` | Calls initiated by user |
| `percent_initiated_conversations` | Conversations started by user |
| `response_rate_text` | Text response rate |
| `response_delay_text` | Text response time |
| `entropy_of_contacts` | Contact distribution evenness |
| `balance_of_contacts` | Outgoing/total ratio per contact |
| `interactions_per_contact` | Interactions per contact |
| `percent_pareto_interactions` | Contacts for 80% of interactions |
| `percent_pareto_durations` | Contacts for 80% of call time |
| `number_of_interactions` | Total interaction count |

## Execution

Execute the following Python code inline using `conda run -n bandicoot python -c "..."`.
Do not save this as a separate script file.

```python
import bandicoot as bc

# Load user (no antennas needed for individual indicators)
user = bc.read_csv('{user_id}', '{records_path}', describe=True, warnings=True)

groupby = '{groupby}' if '{groupby}' != 'none' else None

print(f"\n{'=' * 50}")
print(f"Individual Indicators for {user.name}")
print('=' * 50)

# Activity indicators
print("\n--- Activity ---")
ad = bc.individual.active_days(user, groupby=groupby)
print(f"Active days: {ad}")

noi = bc.individual.number_of_interactions(user, groupby=groupby)
print(f"Total interactions: {noi}")

# Contact patterns
print("\n--- Contact Patterns ---")
nc = bc.individual.number_of_contacts(user, groupby=groupby)
print(f"Number of contacts: {nc}")

eoc = bc.individual.entropy_of_contacts(user, groupby=groupby)
print(f"Entropy of contacts: {eoc}")

ipc = bc.individual.interactions_per_contact(user, groupby=groupby)
print(f"Interactions per contact: {ipc}")

boc = bc.individual.balance_of_contacts(user, groupby=groupby)
print(f"Balance of contacts: {boc}")

# Pareto analysis
print("\n--- Pareto Analysis (80/20 Rule) ---")
ppi = bc.individual.percent_pareto_interactions(user, groupby=groupby)
print(f"Percent pareto interactions: {ppi}")

if user.has_call:
    ppd = bc.individual.percent_pareto_durations(user, groupby=groupby)
    print(f"Percent pareto durations: {ppd}")

# Call indicators
if user.has_call:
    print("\n--- Call Behavior ---")
    cd = bc.individual.call_duration(user, groupby=groupby)
    print(f"Call duration: {cd}")

    pii = bc.individual.percent_initiated_interactions(user, groupby=groupby)
    print(f"Percent initiated (calls): {pii}")

# Text indicators
if user.has_text:
    print("\n--- Text Behavior ---")
    rrt = bc.individual.response_rate_text(user, groupby=groupby)
    print(f"Response rate (text): {rrt}")

    rdt = bc.individual.response_delay_text(user, groupby=groupby)
    print(f"Response delay (text): {rdt}")

# Temporal patterns
print("\n--- Temporal Patterns ---")
iet = bc.individual.interevent_time(user, groupby=groupby)
print(f"Interevent time: {iet}")

pn = bc.individual.percent_nocturnal(user, groupby=groupby)
print(f"Percent nocturnal: {pn}")

pic = bc.individual.percent_initiated_conversations(user, groupby=groupby)
print(f"Percent initiated conversations: {pic}")

print(f"\n{'=' * 50}")
print("Individual analysis complete!")
```

## Examples

### Basic Analysis

```
/bandicoot:analyze-individual ego demo/data/
```

### Without Aggregation

```
/bandicoot:analyze-individual ego demo/data/ --groupby=none
```

## Indicator Details

### active_days

Number of days with at least one call or text. High values indicate consistent
usage patterns.

### number_of_contacts

Count of unique people the user communicated with. Can be filtered by direction
(`in`, `out`) or by minimum interactions (`more=5`).

### call_duration

Distribution of call lengths in seconds. Returns mean, std for each time period.
Helps identify communication style (brief calls vs long conversations).

### interevent_time

Seconds between consecutive interactions. Low values indicate frequent
communication, high std indicates irregular patterns.

### percent_nocturnal

Fraction of interactions during night hours (default 7pm-7am). Useful for
identifying work patterns and lifestyle indicators.

### percent_initiated_interactions

Fraction of calls that are outgoing. Values > 0.5 indicate proactive
communication style.

### response_rate_text

Fraction of incoming text conversations that received a response. Measures
responsiveness and engagement.

### response_delay_text

Time in seconds to respond to text messages within conversations. Maximum is
3600 seconds (1 hour) as conversations are bounded.

### entropy_of_contacts

Shannon entropy measuring how evenly interactions are distributed across
contacts. Low entropy = concentrated on few contacts, high = spread evenly.

### balance_of_contacts

For each contact, the ratio of outgoing to total interactions. Measures whether
relationships are balanced or one-sided.

### percent_pareto_interactions

Percentage of contacts that account for 80% of all interactions. Low values
(~0.2) indicate Pareto distribution with few close contacts.

### percent_pareto_durations

Same as above but weighted by call duration instead of count.
