---
description: Analyze mobile phone recharge/top-up patterns
argument-hint: <user_id> <records_path> <recharges_path> [--groupby=week]
allowed-tools: Bash
---

# Bandicoot: Recharge Analysis

Analyze financial top-up patterns from mobile recharge data.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing records CSV
- `recharges_path` (required): Directory containing recharges CSV
- `--groupby`: Aggregation level - `week` (default), `month`, `year`, or `none`

## Prerequisites

Recharge analysis requires:
- Records file at `{records_path}/{user_id}.csv`
- Recharges file at `{recharges_path}/{user_id}.csv`

### Recharges CSV Format
```csv
datetime,amount,retailer_id
2014-03-01 10:00:00,500,retailer_01
2014-03-15 14:30:00,1000,retailer_02
```

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Load User with Recharges

```
user = bc.read_csv('user_id', 'records/', recharges_path='recharges/')
```

Check recharges loaded: `user.has_recharges` should be True.

## Recharge Indicator Commands

All functions are in `bc.recharge` module:

| Command | Returns |
|---------|---------|
| `bc.recharge.amount_recharges(user)` | Recharge amount distribution |
| `bc.recharge.number_of_recharges(user)` | Count of top-ups per period |
| `bc.recharge.interevent_time_recharges(user)` | Time between recharges (seconds) |
| `bc.recharge.percent_pareto_recharges(user)` | Concentration (% for 80% of total) |
| `bc.recharge.average_balance_recharges(user)` | Estimated daily balance (no groupby) |

All except `average_balance_recharges` accept `groupby` parameter.

## Quick Stats After Loading

- `len(user.recharges)` - total recharge count
- `user.recharges[0].datetime` - first recharge date
- `user.recharges[-1].datetime` - last recharge date
- `sum(r.amount for r in user.recharges)` - total amount

## Interpretation Guide

### amount_recharges

| Pattern | Interpretation |
|---------|----------------|
| High mean | Large top-ups (power user or business) |
| High std | Variable amounts (opportunistic) |
| Low std | Consistent amounts (routine) |

### interevent_time_recharges

| Value (days) | Interpretation |
|--------------|----------------|
| < 7 | Frequent small top-ups |
| 7-30 | Regular monthly pattern |
| > 30 | Infrequent large top-ups |

### percent_pareto_recharges

| Value | Interpretation |
|-------|----------------|
| < 30% | Few large recharges dominate |
| ~50% | Balanced distribution |
| > 70% | Many small recharges |

### average_balance_recharges

Estimated average daily balance assuming linear usage between recharges.
Note: Does not support groupby parameter.

## Examples

Basic recharge analysis:
```
/bandicoot:analyze-recharge ego demo/data/ demo/recharges/
```

Without aggregation:
```
/bandicoot:analyze-recharge ego demo/data/ demo/recharges/ --groupby=none
```

Monthly analysis:
```
/bandicoot:analyze-recharge ego demo/data/ demo/recharges/ --groupby=month
```

## Troubleshooting

**"No recharges loaded" / has_recharges is False**
- Check recharges file exists: `{recharges_path}/{user_id}.csv`
- Verify file format has datetime, amount, retailer_id columns
- Check datetime format: `YYYY-MM-DD HH:MM:SS`

**"Interevent time unavailable"**
- Requires at least 2 recharges in dataset

**"Average balance could not compute"**
- Requires at least 2 recharges
- Check for division issues if all recharges on same day
