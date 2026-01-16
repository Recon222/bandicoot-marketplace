---
description: Analyze social network indicators from Bandicoot user data
argument-hint: <user_id> <records_path> [antennas_path] [--output=network_results.csv]
allowed-tools: Bash
---

# Bandicoot: Network Analysis

Compute social network indicators including clustering coefficients, assortativity, and interaction matrices.

## Arguments

- `user_id` (required): User identifier (filename without .csv)
- `records_path` (required): Directory containing records CSVs
- `antennas_path` (optional): Path to antennas CSV file
- `--output`: Output filename (default: `{user_id}_network.csv`)

## Prerequisites

Network analysis requires:
1. The ego user's records file
2. Correspondent records files in same directory (named `{correspondent_id}.csv`)

## How to Run

Execute commands using:
```
conda run -n bandicoot python -c "import bandicoot as bc; <commands>"
```

Do NOT create script files. Run commands inline and read the output.

## Network Indicator Commands

All functions are in `bc.network` module:

| Command | Returns |
|---------|---------|
| `bc.network.clustering_coefficient_unweighted(user)` | Fraction of closed triplets (binary) |
| `bc.network.clustering_coefficient_weighted(user)` | Weighted by interaction frequency |
| `bc.network.assortativity_indicators(user)` | Behavioral similarity dict |
| `bc.network.matrix_index(user)` | Node labels for matrices |
| `bc.network.matrix_directed_weighted(user)` | Who contacts whom (2D list) |
| `bc.network.matrix_undirected_weighted(user)` | Mutual relationship strength |

## Workflow

### 1. Load User with Network

```
user = bc.read_csv('user_id', 'path/', network=True)
```

The `network=True` parameter is required for network analysis.

### 2. Check Network Loaded

- `user.has_network` - True if network loaded
- `len(user.network)` - number of contacts
- `user.percent_outofnetwork_calls` - calls to unknown contacts
- `user.percent_outofnetwork_texts` - texts to unknown contacts
- `user.percent_outofnetwork_contacts` - contacts without data files

### 3. Run Network Indicators

Run specific network indicators or use `bc.utils.all(user, network=True)`.

### 4. Export Results

```
results = bc.utils.all(user, network=True)
bc.to_csv(results, 'output.csv')
```

## Interpretation Guide

### Clustering Coefficient

Measures how interconnected the user's contacts are.

| Value | Interpretation |
|-------|----------------|
| 0.0 | Star network - contacts isolated |
| 0.1-0.2 | Sparse - few mutual connections |
| 0.2-0.4 | Typical social network |
| 0.4-0.6 | Dense - family/close friends |
| 1.0 | Complete - everyone connected |

### Out-of-Network Percentage

Indicates network coverage quality.

| Percentage | Quality |
|------------|---------|
| < 20% | Excellent coverage |
| 20-50% | Moderate coverage |
| > 50% | Limited coverage |

High values mean many contacts lack data files.

### Assortativity

Measures behavioral similarity between connected users.
- Low variance = similar people connect (homophily)
- High variance = different people connect (heterophily)

## Examples

Basic network analysis:
```
/bandicoot:analyze-network ego demo/data/ demo/data/antennas.csv
```

Custom output:
```
/bandicoot:analyze-network ego demo/data/ --output=my_network_analysis.csv
```

## Troubleshooting

**"Network not loaded" / has_network is False**
- Ensure using `network=True` parameter
- Check correspondent CSV files exist in records directory
- Files must be named `{correspondent_id}.csv`

**High out-of-network percentage**
- Often expected - complete network data is rare
- Analysis valid for in-network portion

**Clustering coefficient is 0**
Could indicate:
- Star network topology (valid result)
- Only one contact in network
- No reciprocated edges

**Assortativity returns None**
- Insufficient network data
- Need multiple correspondents with data files
