# Bandicoot Claude Code Plugin & Marketplace

A comprehensive Claude Code plugin for analyzing mobile phone metadata using
[Bandicoot](https://github.com/yvesalexandre/bandicoot), the Python toolbox for
Call Detail Records (CDRs) analysis.

This repository serves as both a **plugin** and a **marketplace** for easy distribution.

## Overview

This plugin provides:

- **14 Commands** - Slash commands for data loading, analysis, and export
- **3 Skills** - Auto-triggered contextual help for CDR analysis
- **3 Agents** - Multi-step workflows for complex analyses
- **Hooks** - Validation and quality assurance

## Installation

### Prerequisites

**Python 3.7+** with Bandicoot installed:

```bash
# Create conda environment (recommended)
conda create -n bandicoot python=3.8
conda activate bandicoot

# Install Bandicoot
pip install bandicoot
```

### Install via Marketplace (Recommended)

In Claude Code:

```
/plugin marketplace add YOUR-USERNAME/bandicoot-marketplace
/plugin install bandicoot@bandicoot-marketplace
```

### Verify Installation

```
/bandicoot:validate
```

## Quick Start

### 1. Verify Environment

```
/bandicoot:validate
```

### 2. Load Data

```
/bandicoot:load my_user data/records/ data/antennas.csv
```

### 3. Run Analysis

```
/bandicoot:analyze my_user data/records/ data/antennas.csv
```

### 4. Export Results

```
/bandicoot:export my_user data/records/ --output=results.csv
```

## Commands Reference

### Core Analysis

| Command | Description |
|---------|-------------|
| `/bandicoot:load` | Load user data and show summary |
| `/bandicoot:analyze` | Run full analysis (all indicators) |
| `/bandicoot:analyze-individual` | Individual behavior indicators only |
| `/bandicoot:analyze-spatial` | Mobility/spatial indicators only |
| `/bandicoot:analyze-network` | Social network indicators |
| `/bandicoot:analyze-recharge` | Financial top-up patterns |
| `/bandicoot:quick-stats` | Fast summary without full analysis |

### Data Management

| Command | Description |
|---------|-------------|
| `/bandicoot:validate` | Validate environment and data |
| `/bandicoot:describe` | Detailed user description |
| `/bandicoot:export` | Export results to CSV/JSON |
| `/bandicoot:generate-sample` | Generate synthetic test data |

### Advanced

| Command | Description |
|---------|-------------|
| `/bandicoot:compare` | Compare multiple users |
| `/bandicoot:batch` | Batch process entire directories |
| `/bandicoot:visualize` | Generate visualization dashboard |

## Skills

Skills auto-trigger based on conversation context:

### bandicoot-analysis

**Triggers when**: Working with CDR data, phone records, or Bandicoot library

Provides:
- Data format requirements
- API reference
- Error handling patterns
- Best practices

### result-interpretation

**Triggers when**: Analyzing Bandicoot output or discussing indicator meanings

Provides:
- Plain-language explanations
- Benchmark values
- Pattern recognition guidance

### data-preparation

**Triggers when**: Converting data formats or fixing CSV issues

Provides:
- Format conversion scripts
- Common issue solutions
- Validation procedures

## Agents

For complex multi-step workflows:

### network-analyst

Multi-user network analysis with clustering and community detection.

### batch-processor

Process large datasets with progress tracking and error recovery.

### indicator-developer

Guide for creating custom Bandicoot indicators.

## Data Format

### Records CSV (Required)

```csv
datetime,interaction,direction,correspondent_id,call_duration,antenna_id
2014-03-02 07:13:30,call,out,contact_5,120,tower_701
2014-03-02 09:45:00,text,in,contact_12,,tower_702
```

**Required columns:**
- `datetime` - Format: `YYYY-MM-DD HH:MM:SS`
- `interaction` - Values: `call`, `text`
- `direction` - Values: `in`, `out`
- `correspondent_id` - Unique contact identifier

**Optional columns:**
- `call_duration` - Duration in seconds (calls only)
- `antenna_id` - Cell tower identifier
- `latitude`, `longitude` - GPS coordinates

### Antennas CSV (Optional)

```csv
antenna_id,latitude,longitude
tower_701,42.361013,-71.097868
tower_702,42.370849,-71.114613
```

### Recharges CSV (Optional)

```csv
datetime,amount,retailer_id
2014-03-01 10:00:00,500,retailer_01
```

## Indicators

The plugin computes 36+ behavioral indicators across categories:

### Individual Indicators

| Indicator | Description |
|-----------|-------------|
| `active_days` | Days with at least one record |
| `number_of_contacts` | Unique contacts |
| `call_duration` | Distribution of call lengths |
| `percent_nocturnal` | Night activity (7pm-7am) |
| `percent_initiated_conversations` | Outgoing vs incoming ratio |
| `response_delay_text` | Time to respond to texts |
| `response_rate_text` | Percentage of texts answered |
| `entropy_of_contacts` | Diversity of communication |
| `balance_of_contacts` | In/out ratio per contact |
| `interactions_per_contact` | Average interactions |
| `interevent_time` | Time between events |
| `percent_pareto_interactions` | Concentration (80/20 rule) |
| `percent_pareto_durations` | Duration concentration |
| `number_of_interactions` | Total calls/texts |
| `number_of_interaction_in/out` | Directional counts |

### Spatial Indicators

| Indicator | Description |
|-----------|-------------|
| `number_of_antennas` | Unique cell towers visited |
| `entropy_of_antennas` | Mobility diversity |
| `percent_at_home` | Time at home location |
| `radius_of_gyration` | Mobility range (km) |
| `frequent_antennas` | Regularly visited locations |
| `churn_rate` | Location change frequency |

### Network Indicators

| Indicator | Description |
|-----------|-------------|
| `clustering_coefficient_unweighted` | Network density |
| `clustering_coefficient_weighted` | Weighted density |
| `assortativity_indicators` | Behavioral similarity |
| `assortativity_attributes` | Attribute similarity |

### Recharge Indicators

| Indicator | Description |
|-----------|-------------|
| `amount_recharges` | Top-up amount distribution |
| `number_of_recharges` | Top-up frequency |
| `interevent_time_recharges` | Time between top-ups |
| `percent_pareto_recharges` | Concentration |
| `average_balance_recharges` | Estimated balance |

## Example Workflows

### Single User Analysis

```
/bandicoot:analyze ego data/records/ data/antennas.csv --output=ego_analysis.csv
```

### Cohort Comparison

```
/bandicoot:compare user1 user2 user3 data/records/ --output=cohort_comparison.csv
```

### Full Dataset Processing

```
/bandicoot:batch data/records/ data/antennas.csv --output-dir=results/ --summary=true
```

### Network Analysis

```
/bandicoot:analyze-network ego data/records/ data/antennas.csv
```

## Troubleshooting

### "Bandicoot not found"

```bash
# Activate conda environment
conda activate bandicoot

# Or install Bandicoot
pip install bandicoot
```

### "Invalid datetime format"

Ensure datetime follows `YYYY-MM-DD HH:MM:SS`:
- Correct: `2014-03-02 07:13:30`
- Wrong: `03/02/2014 7:13:30`

### "Missing required columns"

Check your CSV has these exact column names:
- `datetime`
- `interaction`
- `direction`
- `correspondent_id`

### "No spatial indicators"

Requires either:
- `antenna_id` column + antennas file
- `latitude` and `longitude` columns

## File Structure

```
bandicoot-plugin/
  .claude-plugin/
    plugin.json           # Plugin manifest

  commands/
    load.md              # Load user data
    analyze.md           # Full analysis
    analyze-individual.md
    analyze-spatial.md
    analyze-network.md
    analyze-recharge.md
    quick-stats.md
    export.md
    describe.md
    validate.md
    compare.md
    batch.md
    visualize.md
    generate-sample.md

  skills/
    bandicoot-analysis/
      SKILL.md           # Core analysis skill
      indicator-reference.md
      troubleshooting.md
      error-patterns.md
      quick-reference.md
      scripts/
        check-environment.py
        validate-data.py
        validate-path.py

    result-interpretation/
      SKILL.md
      indicator-meanings.md
      benchmarks.md

    data-preparation/
      SKILL.md
      csv-formats.md
      common-issues.md

  agents/
    network-analyst.md
    batch-processor.md
    indicator-developer.md

  hooks/
    hooks.json
    validate-output.py
    validate-input-data.py

  resources/
    sample-data/
      sample_user.csv
      sample_antennas.csv
      sample_recharges.csv
    templates/
      records_template.csv
      antennas_template.csv
      recharges_template.csv
```

## Contributing

Contributions welcome! Areas of interest:

- Additional indicators
- Visualization improvements
- Performance optimizations
- Documentation enhancements

## License

This plugin is provided under the same license as Bandicoot (MIT License).

## Credits

- **Bandicoot**: MIT Media Lab - [bandicoot.mit.edu](http://bandicoot.mit.edu)
- **Plugin**: Created for Claude Code Skills system

## References

- [Bandicoot Documentation](http://bandicoot.mit.edu/docs/)
- [Bandicoot GitHub](https://github.com/yvesalexandre/bandicoot)
- [de Montjoye et al., "bandicoot: a Python Toolbox for Mobile Phone Metadata"](http://bandicoot.mit.edu)
