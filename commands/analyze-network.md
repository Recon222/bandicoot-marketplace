---
description: Analyze social network indicators from Bandicoot user data
argument-hint: <user_id> <records_path> [antennas_path] [--output=network_results.csv]
allowed-tools: Bash, Write
---

# Bandicoot: Network Analysis

Compute social network indicators including clustering coefficients, assortativity,
and interaction matrices.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing records CSVs
- `antennas_path` (optional): Path to antennas CSV file
- `--output`: Output filename (default: `{user_id}_network.csv`)

## Prerequisites

Network analysis requires:
1. The ego user's records file
2. Correspondent records files in the same directory (named `{correspondent_id}.csv`)

## Execution

Execute the following Python code inline using `conda run -n bandicoot python -c "..."`.
Do not save this as a separate script file.

```python
import bandicoot as bc

user_id = '{user_id}'
records_path = '{records_path}'
antennas_path = '{antennas_path}' if '{antennas_path}' else None
output_file = '{output}' if '{output}' else f'{user_id}_network.csv'

# Load user WITH network (critical!)
print(f"Loading user with network: {user_id}")
user = bc.read_csv(
    user_id,
    records_path,
    antennas_path,
    network=True,  # MUST be True for network analysis
    describe=True,
    warnings=True
)

# Check network loaded
if not user.has_network:
    print("WARNING: Network not loaded!")
    print("Ensure correspondent CSV files exist in the records directory")
else:
    print(f"\n{'=' * 60}")
    print(f"Network Analysis for {user.name}")
    print('=' * 60)

    # Network summary
    print(f"\n--- Network Summary ---")
    print(f"Network size: {len(user.network)} contacts")

    loaded = sum(1 for v in user.network.values() if v is not None)
    missing = len(user.network) - loaded
    print(f"Correspondents loaded: {loaded}")
    print(f"Correspondents missing: {missing}")

    print(f"\n--- Out-of-Network Statistics ---")
    print(f"Out-of-network calls: {user.percent_outofnetwork_calls:.1%}")
    print(f"Out-of-network texts: {user.percent_outofnetwork_texts:.1%}")
    print(f"Out-of-network contacts: {user.percent_outofnetwork_contacts:.1%}")
    print(f"Out-of-network call duration: {user.percent_outofnetwork_call_durations:.1%}")

    # Clustering coefficients
    print(f"\n--- Clustering Coefficients ---")
    cc_unweighted = bc.network.clustering_coefficient_unweighted(user)
    cc_weighted = bc.network.clustering_coefficient_weighted(user)

    print(f"Unweighted: {cc_unweighted}")
    print(f"Weighted: {cc_weighted}")

    # Interpretation
    if cc_unweighted is not None:
        if cc_unweighted < 0.1:
            interpretation = "Star network - contacts don't know each other"
        elif cc_unweighted < 0.3:
            interpretation = "Sparse network - few interconnections"
        elif cc_unweighted < 0.5:
            interpretation = "Moderate clustering - typical social network"
        else:
            interpretation = "Dense network - contacts are well connected"
        print(f"Interpretation: {interpretation}")

    # Interaction matrices
    print(f"\n--- Network Structure ---")
    labels = bc.network.matrix_index(user)
    print(f"Network nodes: {labels}")

    # Directed weighted matrix
    matrix = bc.network.matrix_directed_weighted(user, interaction='call')
    print(f"\nCall interaction matrix (who calls whom):")
    print(f"  Rows: from, Columns: to")
    for i, label in enumerate(labels[:5]):  # Show first 5
        row = matrix[i][:5]
        print(f"  {label}: {row}")
    if len(labels) > 5:
        print(f"  ... ({len(labels)} total nodes)")

    # Assortativity
    print(f"\n--- Assortativity Analysis ---")
    print("Measuring similarity between connected users...")

    assort = bc.network.assortativity_indicators(user)
    if assort:
        # Show most assortative (lowest variance = most similar)
        sorted_assort = sorted(assort.items(), key=lambda x: x[1])
        print(f"\nMost similar indicators (lowest variance):")
        for key, val in sorted_assort[:5]:
            print(f"  {key}: {val:.4f}")

        print(f"\nLeast similar indicators (highest variance):")
        for key, val in sorted_assort[-5:]:
            print(f"  {key}: {val:.4f}")
    else:
        print("Assortativity could not be computed (insufficient network data)")

    # Export results with network
    print(f"\n--- Exporting Results ---")
    results = bc.utils.all(user, network=True, groupby='week')

    bc.to_csv(results, output_file, warnings=False)
    bc.to_json(results, output_file.replace('.csv', '.json'), warnings=False)

    print(f"Results saved to:")
    print(f"  {output_file}")
    print(f"  {output_file.replace('.csv', '.json')}")

    print(f"\n{'=' * 60}")
    print("Network analysis complete!")
```

## Examples

### Basic Network Analysis

```
/bandicoot:analyze-network ego demo/data/ demo/data/antennas.csv
```

### Custom Output

```
/bandicoot:analyze-network ego demo/data/ --output=my_network_analysis.csv
```

## Network Indicators Computed

| Indicator | Description |
|-----------|-------------|
| `clustering_coefficient_unweighted` | Fraction of closed triplets (binary) |
| `clustering_coefficient_weighted` | Weighted by interaction frequency |
| `assortativity_indicators` | Behavioral similarity with contacts |
| `assortativity_attributes` | Attribute similarity (if loaded) |

## Understanding the Results

### Clustering Coefficient

Measures how interconnected the user's contacts are:

| Value | Interpretation |
|-------|----------------|
| 0.0 | Star network - contacts isolated |
| 0.1-0.2 | Sparse - few mutual connections |
| 0.2-0.4 | Typical social network |
| 0.4-0.6 | Dense - family/close friends |
| 1.0 | Complete - everyone connected |

### Out-of-Network Percentage

Indicates network coverage quality:

| Percentage | Coverage Quality |
|------------|-----------------|
| < 20% | Excellent coverage |
| 20-50% | Moderate coverage |
| > 50% | Limited coverage |

High out-of-network values mean many contacts lack data files.

### Assortativity

Low variance = similar people connect (homophily)
High variance = different people connect (heterophily)

## Troubleshooting

### "Network not loaded"

Ensure:
1. Using `network=True` parameter
2. Correspondent CSV files exist in same directory
3. Files named `{correspondent_id}.csv`

### "High out-of-network percentage"

This is often expected - complete network data is rare. Analysis is still valid
for the in-network portion.

### "Clustering coefficient is 0"

Could indicate:
- Star network topology (valid result)
- Only one contact in network
- No reciprocated edges
