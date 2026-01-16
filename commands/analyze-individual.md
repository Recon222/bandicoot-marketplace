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

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Individual Indicator Commands

All functions are in `bc.individual` module:

| Command | Returns |
|---------|---------|
| `bc.individual.active_days(user)` | Days with any activity |
| `bc.individual.number_of_contacts(user)` | Unique contacts count |
| `bc.individual.call_duration(user)` | Call length distribution |
| `bc.individual.interevent_time(user)` | Time between interactions |
| `bc.individual.percent_nocturnal(user)` | Nighttime activity % |
| `bc.individual.percent_initiated_interactions(user)` | Outgoing call % |
| `bc.individual.percent_initiated_conversations(user)` | Started conversations % |
| `bc.individual.response_rate_text(user)` | Text response rate |
| `bc.individual.response_delay_text(user)` | Text response time (sec) |
| `bc.individual.entropy_of_contacts(user)` | Contact distribution evenness |
| `bc.individual.balance_of_contacts(user)` | Outgoing/total per contact |
| `bc.individual.interactions_per_contact(user)` | Interactions per contact |
| `bc.individual.percent_pareto_interactions(user)` | Contacts for 80% of activity |
| `bc.individual.percent_pareto_durations(user)` | Contacts for 80% call time |
| `bc.individual.number_of_interactions(user)` | Total interaction count |

All accept `groupby` parameter: `bc.individual.active_days(user, groupby='week')`

## Workflow

### 1. Load User

```
user = bc.read_csv('user_id', 'path/')
```

No antennas needed for individual indicators.

### 2. Check Data Types

- `user.has_call` - True if call records present
- `user.has_text` - True if text records present

### 3. Run Indicators

Run specific indicators or use `bc.utils.all(user)` for all.

## Interpretation Guide

### active_days
Days with at least one call or text. High values indicate consistent usage.

### number_of_contacts
Count of unique contacts. Filter options: `direction='in'`, `direction='out'`, `more=5` (minimum interactions).

### call_duration
Call length in seconds. Returns mean, std for each period. Identifies brief vs long conversation style.

### interevent_time
Seconds between consecutive interactions. Low = frequent, high std = irregular patterns.

### percent_nocturnal
Fraction during night hours (7pm-7am). Lifestyle and work pattern indicator.

| Value | Interpretation |
|-------|----------------|
| < 0.2 | Daytime user |
| 0.2-0.4 | Normal mix |
| > 0.4 | Night-active |

### percent_initiated_interactions
Fraction of outgoing calls.

| Value | Interpretation |
|-------|----------------|
| < 0.3 | Passive communicator |
| 0.3-0.7 | Balanced |
| > 0.7 | Proactive communicator |

### response_rate_text
Fraction of incoming texts that get a response. Measures engagement.

### response_delay_text
Response time in seconds (max 3600 as conversations bounded to 1 hour).

### entropy_of_contacts
Shannon entropy of interaction distribution.
- Low (0-1): Concentrated on few contacts
- High: Spread evenly across contacts

### balance_of_contacts
Outgoing/total ratio per contact. Measures relationship balance.
- 0.5: Balanced
- < 0.5: More receiving
- > 0.5: More initiating

### percent_pareto_interactions
Percentage of contacts for 80% of interactions.
- ~0.2: Strong Pareto (few close contacts)
- ~0.5: More distributed

## Examples

Basic analysis:
```
/bandicoot:analyze-individual ego demo/data/
```

Without aggregation:
```
/bandicoot:analyze-individual ego demo/data/ --groupby=none
```

## Troubleshooting

**Call indicators return None**
- Check `user.has_call` is True
- Ensure records contain call data

**Text indicators return None**
- Check `user.has_text` is True
- Ensure records contain text data

**All indicators are None**
- Verify data file loaded correctly
- Check datetime format is valid
