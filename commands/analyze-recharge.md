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

## Execution

```python
import bandicoot as bc

user_id = '{user_id}'
records_path = '{records_path}'
recharges_path = '{recharges_path}'
groupby = '{groupby}' if '{groupby}' != 'none' else None

# Load user with recharges
print(f"Loading user with recharges: {user_id}")
user = bc.read_csv(
    user_id,
    records_path,
    recharges_path=recharges_path,
    describe=False,
    warnings=True
)

# Check recharges loaded
if not user.has_recharges:
    print("ERROR: No recharges loaded!")
    print(f"Expected recharges file at: {recharges_path}/{user_id}.csv")
    print("\nRecharges CSV should have columns: datetime, amount, retailer_id")
else:
    print(f"\n{'=' * 60}")
    print(f"Recharge Analysis for {user.name}")
    print('=' * 60)

    # Basic stats
    print(f"\n--- Recharge Overview ---")
    print(f"Total recharges: {len(user.recharges)}")

    if user.recharges:
        first = user.recharges[0].datetime
        last = user.recharges[-1].datetime
        print(f"Date range: {first} to {last}")

        # Total amount
        total_amount = sum(r.amount for r in user.recharges)
        print(f"Total amount recharged: {total_amount:.2f}")

        # Average
        avg_amount = total_amount / len(user.recharges)
        print(f"Average recharge: {avg_amount:.2f}")

    # Recharge indicators
    print(f"\n--- Recharge Indicators (groupby={groupby}) ---")

    # Amount distribution
    amount = bc.recharge.amount_recharges(user, groupby=groupby)
    print(f"\nAmount of recharges:")
    print(f"  {amount}")

    # Number of recharges
    num = bc.recharge.number_of_recharges(user, groupby=groupby)
    print(f"\nNumber of recharges:")
    print(f"  {num}")

    # Interevent time (if multiple recharges)
    if len(user.recharges) >= 2:
        iet = bc.recharge.interevent_time_recharges(user, groupby=groupby)
        print(f"\nTime between recharges (seconds):")
        print(f"  {iet}")

        # Convert to days for readability
        if groupby is None and isinstance(iet.get('allweek', {}).get('allday'), dict):
            mean_seconds = iet['allweek']['allday'].get('mean', 0)
            if mean_seconds:
                mean_days = mean_seconds / 86400
                print(f"  (mean: {mean_days:.1f} days)")

    # Pareto concentration
    pareto = bc.recharge.percent_pareto_recharges(user, groupby=groupby)
    print(f"\nPareto concentration (% recharges for 80% of total):")
    print(f"  {pareto}")

    # Average balance (not groupable)
    if len(user.recharges) >= 2:
        try:
            avg_balance = bc.recharge.average_balance_recharges(user)
            print(f"\nEstimated average daily balance:")
            print(f"  {avg_balance:.2f}")
        except Exception as e:
            print(f"\nAverage balance: Could not compute ({e})")

    # Interpretation
    print(f"\n--- Interpretation ---")

    if len(user.recharges) >= 2:
        # Get raw values for interpretation
        amount_raw = bc.recharge.amount_recharges(user, groupby=None)
        amount_mean = amount_raw.get('allweek', {}).get('allday', {}).get('mean', 0)

        iet_raw = bc.recharge.interevent_time_recharges(user, groupby=None)
        iet_mean = iet_raw.get('allweek', {}).get('allday', {}).get('mean', 0)
        iet_days = iet_mean / 86400 if iet_mean else 0

        pareto_raw = bc.recharge.percent_pareto_recharges(user, groupby=None)
        pareto_val = pareto_raw.get('allweek', {}).get('allday', 0)

        # Recharge frequency
        if iet_days < 7:
            freq_interp = "Frequent recharger (weekly or more)"
        elif iet_days < 30:
            freq_interp = "Regular recharger (monthly)"
        else:
            freq_interp = "Infrequent recharger"
        print(f"Frequency: {freq_interp}")

        # Pareto interpretation
        if pareto_val and pareto_val < 0.3:
            pareto_interp = "Few large recharges dominate"
        elif pareto_val and pareto_val > 0.7:
            pareto_interp = "Many small recharges"
        else:
            pareto_interp = "Mixed recharge amounts"
        print(f"Pattern: {pareto_interp}")

    print(f"\n{'=' * 60}")
    print("Recharge analysis complete!")
```

## Examples

### Basic Recharge Analysis

```
/bandicoot:analyze-recharge ego demo/data/ demo/recharges/
```

### Without Aggregation

```
/bandicoot:analyze-recharge ego demo/data/ demo/recharges/ --groupby=none
```

### Monthly Analysis

```
/bandicoot:analyze-recharge ego demo/data/ demo/recharges/ --groupby=month
```

## Recharge Indicators

| Indicator | Description |
|-----------|-------------|
| `amount_recharges` | Distribution of recharge amounts |
| `number_of_recharges` | Count of top-ups per period |
| `interevent_time_recharges` | Time between consecutive recharges |
| `percent_pareto_recharges` | Concentration (% for 80% of total) |
| `average_balance_recharges` | Estimated average daily balance |

## Indicator Details

### amount_recharges

Distribution statistics of recharge amounts. Helps understand typical top-up size.

- **High mean**: Large recharges (prepaid power user or business)
- **High std**: Variable amounts (opportunistic recharging)
- **Low std**: Consistent amounts (routine behavior)

### number_of_recharges

Count of recharges in each time period. Indicates top-up frequency.

### interevent_time_recharges

Time in seconds between consecutive recharges. Indicates financial behavior:

- **< 7 days**: Frequent small top-ups
- **7-30 days**: Regular monthly pattern
- **> 30 days**: Infrequent large top-ups

### percent_pareto_recharges

Percentage of recharges accounting for 80% of total amount:

- **Low (<30%)**: Few large recharges dominate
- **High (>70%)**: Many small recharges
- **~50%**: Balanced distribution

### average_balance_recharges

Estimated average daily balance assuming linear usage between recharges and
empty balance before each recharge. Provides rough financial indicator.

**Note**: This function does not support groupby parameter.

## Troubleshooting

### "No recharges loaded"

1. Check recharges file exists: `{recharges_path}/{user_id}.csv`
2. Verify file format (datetime, amount, retailer_id columns)
3. Check datetime format matches `YYYY-MM-DD HH:MM:SS`

### "Interevent time unavailable"

Requires at least 2 recharges in the dataset.

### "Average balance could not compute"

Requires at least 2 recharges. Also check for division issues if all recharges
are on the same day.
