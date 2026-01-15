# Bandicoot Skills Architecture Plan

> A Comprehensive Phased Implementation Plan for Claude Code Skills-Based Bandicoot Integration

**Version:** 1.2 (Comprehensive Revision)
**Date:** January 2026
**Status:** Implementation Plan (All Outstanding Items Addressed)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Skills vs Slash Commands: Design Decision](#skills-vs-slash-commands-design-decision)
4. [Directory Structure](#directory-structure)
5. [Skill File Specifications](#skill-file-specifications)
6. [Slash Command Specifications](#slash-command-specifications)
7. [Agent Specifications](#agent-specifications)
8. [Workflow Encoding Patterns](#workflow-encoding-patterns)
9. [Phase 1: Foundation](#phase-1-foundation)
10. [Phase 2: Core Analysis Commands](#phase-2-core-analysis-commands)
11. [Phase 3: Advanced Workflows](#phase-3-advanced-workflows)
12. [Phase 4: Network Analysis Suite](#phase-4-network-analysis-suite)
13. [Phase 5: Polish and Optimization](#phase-5-polish-and-optimization)
14. [Validation Strategy](#validation-strategy)
15. [Testing Approach](#testing-approach)
16. [Pros and Cons Analysis](#pros-and-cons-analysis)
17. [Comparison with MCP Approach](#comparison-with-mcp-approach)
18. [Risk Mitigation](#risk-mitigation)
19. [Appendix: Reference Commands](#appendix-reference-commands)

---

## Executive Summary

This document outlines a comprehensive plan for wrapping Bandicoot as a suite of Claude Code skills and slash commands. The approach leverages Claude Code's native capability to execute Python commands directly via Bash in a conda environment, which has already been proven functional.

**Key Advantages:**
- Zero additional infrastructure required
- Direct Python execution with full Bandicoot capability access
- Skills encode domain knowledge and best practices
- Slash commands provide user-friendly entry points
- Agents can orchestrate complex multi-step workflows

**Target Outcome:**
A complete plugin package that enables Claude Code agents to analyze mobile phone metadata using Bandicoot through natural language requests, with validated results matching known outputs.

---

## Architecture Overview

### System Architecture

```
+------------------------------------------+
|            Claude Code Agent              |
+------------------------------------------+
                    |
                    v
+------------------------------------------+
|     Skill Tool / Slash Command Trigger    |
+------------------------------------------+
                    |
        +-----------+-----------+
        |           |           |
        v           v           v
+------------+ +-----------+ +------------+
|   Skills   | | Commands  | |   Agents   |
| (Auto-use) | | (User /x) | | (Complex)  |
+------------+ +-----------+ +------------+
        |           |           |
        +-----------+-----------+
                    |
                    v
+------------------------------------------+
|        Bash Tool (Python Execution)       |
+------------------------------------------+
                    |
                    v
+------------------------------------------+
|   Conda Environment: bandicoot (Python)   |
+------------------------------------------+
                    |
                    v
+------------------------------------------+
|         Bandicoot Library (v0.6.0)        |
+------------------------------------------+
                    |
        +-----------+-----------+
        |           |           |
        v           v           v
+------------+ +-----------+ +------------+
| individual | |  spatial  | |  network   |
|    .py     |   .py      |    .py      |
+------------+ +-----------+ +------------+
        |           |           |
        v           v           v
+------------------------------------------+
|    CSV/JSON Results -> User Analysis      |
+------------------------------------------+
```

### Execution Model

Claude Code executes Bandicoot commands through the Bash tool:

```bash
# Cross-platform conda execution (recommended for Windows compatibility)
conda run -n bandicoot python -c "import bandicoot as bc; ..."

# Alternative for interactive shells (Unix-like systems only)
# conda activate bandicoot && python -c "import bandicoot as bc; ..."
```

Skills and commands encode:
1. **What** Bandicoot commands to run
2. **How** to interpret results
3. **When** to apply different analysis patterns
4. **Why** certain parameters matter

---

## Skills vs Slash Commands: Design Decision

### Understanding the Distinction

| Aspect | Slash Commands | Skills |
|--------|----------------|--------|
| **Invocation** | User-triggered (`/command`) | Model-triggered (automatic) |
| **Location** | `.claude/commands/` | `.claude/skills/` |
| **Format** | Single markdown file | Directory with `SKILL.md` + resources |
| **Complexity** | Simple prompts | Complex capabilities with scripts |
| **Best For** | Explicit user actions | Context-aware automation |

### Our Strategy

We will implement **both**:

1. **Slash Commands** for explicit user actions:
   - `/bandicoot:load` - Load user data
   - `/bandicoot:analyze` - Run full analysis
   - `/bandicoot:visualize` - Start dashboard
   - `/bandicoot:export` - Export results

2. **Skills** for automatic context-aware assistance:
   - Bandicoot data analysis skill (auto-triggers on CDR analysis tasks)
   - Result interpretation skill (explains indicator meanings)
   - Troubleshooting skill (diagnoses data quality issues)

3. **Agents** for complex multi-step workflows:
   - Network analysis agent
   - Batch processing agent
   - Custom indicator development agent

---

## Directory Structure

Claude Code plugins follow a specific organizational pattern. The `plugin.json` manifest must be located inside a `.claude-plugin/` directory, not at the root level.

```
bandicoot-plugin/
|
+-- .claude-plugin/
|   +-- plugin.json               # Plugin manifest (REQUIRED location)
|
+-- commands/                      # User-invoked slash commands
|   +-- load.md                    # /bandicoot:load
|   +-- analyze.md                 # /bandicoot:analyze
|   +-- analyze-individual.md     # /bandicoot:analyze-individual
|   +-- analyze-spatial.md        # /bandicoot:analyze-spatial
|   +-- analyze-network.md        # /bandicoot:analyze-network
|   +-- analyze-recharge.md       # /bandicoot:analyze-recharge
|   +-- visualize.md              # /bandicoot:visualize
|   +-- export.md                 # /bandicoot:export
|   +-- compare.md                # /bandicoot:compare
|   +-- batch.md                  # /bandicoot:batch
|   +-- describe.md               # /bandicoot:describe
|   +-- generate-sample.md        # /bandicoot:generate-sample
|   +-- validate.md               # /bandicoot:validate
|   +-- quick-stats.md            # /bandicoot:quick-stats
|
+-- skills/
|   +-- bandicoot-analysis/       # Core analysis skill
|   |   +-- SKILL.md
|   |   +-- indicator-reference.md
|   |   +-- troubleshooting.md
|   |   +-- scripts/
|   |       +-- validate-data.py
|   |       +-- check-environment.py
|   |       +-- validate-path.py
|   |   +-- error-patterns.md
|   |
|   +-- result-interpretation/    # Explains what results mean
|   |   +-- SKILL.md
|   |   +-- indicator-meanings.md
|   |   +-- benchmarks.md
|   |
|   +-- data-preparation/         # Data format guidance
|       +-- SKILL.md
|       +-- csv-formats.md
|       +-- common-issues.md
|
+-- agents/                        # Subagent definitions (.md files)
|   +-- network-analyst.md        # Multi-user network analysis
|   +-- batch-processor.md        # Process multiple users
|   +-- indicator-developer.md    # Create custom indicators
|
+-- hooks/
|   +-- hooks.json                # Hook definitions (wrapper format required)
|   +-- validate-output.sh        # Validate results on export
|
+-- resources/
|   +-- sample-data/              # Sample datasets for testing
|   +-- expected-outputs/         # Known-good outputs for validation
|   +-- templates/                # Output templates
|
+-- README.md                     # Plugin documentation
```

**Note:** For single-project usage (not a shared plugin), skills and commands can alternatively be placed in `.claude/skills/` and `.claude/commands/` directories at the project root.

---

## Skill File Specifications

### Core Analysis Skill: `skills/bandicoot-analysis/SKILL.md`

```markdown
---
name: bandicoot-analysis
description: |
  Use this skill when analyzing mobile phone metadata (Call Detail Records/CDRs),
  computing behavioral indicators from communication patterns, or working with
  the Bandicoot Python library.

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

allowed-tools: Bash, Read, Write
---

# Bandicoot Analysis Skill

You are an expert in analyzing mobile phone metadata using Bandicoot,
a Python toolbox from MIT for extracting behavioral indicators from
Call Detail Records (CDRs).

## Environment Setup

Always verify the conda environment before running Bandicoot. Use `conda run` for cross-platform compatibility (especially on Windows):

```bash
conda run -n bandicoot python -c "import bandicoot as bc; print(f'Bandicoot {bc.__version__}')"
```

## Core Commands Reference

### Loading Data

```python
import bandicoot as bc

# Basic load
user = bc.read_csv('user_id', 'records_path/', 'antennas.csv')

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

### Computing Indicators

```python
# All indicators
results = bc.utils.all(user, groupby='week', summary='default')

# Individual indicators
bc.individual.call_duration(user)
bc.individual.number_of_contacts(user)
bc.individual.percent_nocturnal(user)
bc.individual.entropy_of_contacts(user)

# Spatial indicators
bc.spatial.radius_of_gyration(user)
bc.spatial.percent_at_home(user)
bc.spatial.number_of_antennas(user)

# Network indicators (requires network=True)
bc.network.clustering_coefficient_unweighted(user)
```

### Exporting Results

```python
# To CSV (for multiple users)
bc.to_csv([results], 'output.csv')

# To JSON
bc.to_json(results, 'output.json')

# Flatten nested structure
flat = bc.utils.flatten(results)
```

### Visualization

```python
# Start dashboard server
bc.visualization.run(user, port=4242)

# Export dashboard files
bc.visualization.export(user, 'viz_directory/')
```

## Parameter Reference

### Groupby Options
- `'week'` - Weekly aggregation (default)
- `'month'` - Monthly aggregation
- `'year'` - Yearly aggregation
- `None` - No grouping (raw values)

### Summary Options
- `'default'` - Mean and std
- `'extended'` - Mean, std, median, min, max, skewness, kurtosis
- `None` - Raw distribution

### Split Options
- `split_week=True` - Separate weekday/weekend analysis
- `split_day=True` - Separate day/night analysis

## Indicator Categories

### Individual Indicators (15)
Communication behavior metrics: active_days, number_of_contacts, call_duration,
interevent_time, percent_nocturnal, percent_initiated_interactions,
response_rate_text, response_delay_text, percent_initiated_conversations,
entropy_of_contacts, balance_of_contacts, interactions_per_contact,
percent_pareto_interactions, percent_pareto_durations, number_of_interactions

### Spatial Indicators (6)
Mobility metrics: number_of_antennas, entropy_of_antennas, percent_at_home,
radius_of_gyration, frequent_antennas, churn_rate

### Network Indicators (10)
Social network metrics: clustering_coefficient_unweighted,
clustering_coefficient_weighted, assortativity_indicators,
assortativity_attributes, matrix_* functions

### Recharge Indicators (5)
Financial metrics: number_of_recharges, amount_recharges,
interevent_time_recharges, percent_pareto_recharges, average_balance_recharges

## Data Format Requirements

### Records CSV
```csv
interaction,direction,correspondent_id,datetime,call_duration,antenna_id
call,out,contact_5,2014-03-02 07:13:30,120,tower_701
text,in,contact_12,2014-03-02 09:45:00,,tower_702
```

### Antennas CSV
```csv
antenna_id,latitude,longitude
tower_701,42.361013,-71.097868
tower_702,42.370849,-71.114613
```

## Troubleshooting

### Common Issues

1. **Missing location warnings**: Check antenna file path and antenna_id matching
2. **Empty results**: Verify datetime format (YYYY-MM-DD HH:MM:SS)
3. **Network indicators None**: Ensure network=True when loading
4. **Home location None**: Need nighttime records with antenna data

### Data Quality Checks

```python
# Check data quality
print(f"Records: {len(user.records)}")
print(f"Has calls: {user.has_call}")
print(f"Has texts: {user.has_text}")
print(f"Has home: {user.has_home}")
print(f"Ignored records: {user.ignored_records}")
```
```

### Path Validation Script: `scripts/validate-path.py`

```python
#!/usr/bin/env python
"""
Security utility for validating file paths before Bandicoot operations.
Prevents directory traversal attacks and ensures paths are within allowed directories.
"""
import os
import sys

def validate_path(path, allowed_base_dirs=None):
    """
    Validate that a path is safe to use.

    Parameters
    ----------
    path : str
        The path to validate
    allowed_base_dirs : list of str, optional
        List of allowed base directories. If None, allows current working directory.

    Returns
    -------
    str
        The validated absolute path

    Raises
    ------
    ValueError
        If path is outside allowed directories or contains dangerous patterns
    """
    # Convert to absolute path and normalize
    abs_path = os.path.abspath(os.path.expanduser(path))

    # Handle Windows paths (UNC paths, drive letters)
    if sys.platform == 'win32':
        abs_path = os.path.normpath(abs_path)
        # Check for UNC path attempts
        if abs_path.startswith('\\\\') and not any(
            abs_path.startswith(os.path.normpath(d)) for d in (allowed_base_dirs or [os.getcwd()])
        ):
            raise ValueError(f"UNC paths not allowed: {path}")

    # Default allowed directory is current working directory
    if allowed_base_dirs is None:
        allowed_base_dirs = [os.getcwd()]

    # Normalize all allowed directories
    allowed_base_dirs = [os.path.abspath(os.path.expanduser(d)) for d in allowed_base_dirs]

    # Check path is within allowed directories
    is_allowed = False
    for allowed_dir in allowed_base_dirs:
        # Ensure we're checking against normalized paths
        if sys.platform == 'win32':
            allowed_dir = os.path.normpath(allowed_dir)

        if abs_path.startswith(allowed_dir + os.sep) or abs_path == allowed_dir:
            is_allowed = True
            break

    if not is_allowed:
        raise ValueError(
            f"Path '{path}' is outside allowed directories: {allowed_base_dirs}"
        )

    # Check for dangerous patterns
    dangerous_patterns = ['..', '~root', '/etc/', '/var/', 'C:\\Windows\\']
    for pattern in dangerous_patterns:
        if pattern in path and pattern not in abs_path:
            raise ValueError(f"Suspicious pattern in path: {pattern}")

    return abs_path


def validate_csv_path(path, allowed_base_dirs=None):
    """Validate path and ensure it's a CSV file or directory containing CSVs."""
    validated = validate_path(path, allowed_base_dirs)

    if os.path.isfile(validated):
        if not validated.lower().endswith('.csv'):
            raise ValueError(f"File is not a CSV: {validated}")

    return validated


if __name__ == "__main__":
    # Command-line validation
    if len(sys.argv) < 2:
        print("Usage: python validate-path.py <path> [allowed_base_dir...]")
        sys.exit(1)

    test_path = sys.argv[1]
    allowed_dirs = sys.argv[2:] if len(sys.argv) > 2 else None

    try:
        validated = validate_path(test_path, allowed_dirs)
        print(f"Valid: {validated}")
        sys.exit(0)
    except ValueError as e:
        print(f"Invalid: {e}")
        sys.exit(1)
```

### Error Handling Patterns: `error-patterns.md`

```markdown
# Bandicoot Error Handling Patterns

This document defines standard error handling patterns for all commands and skills.

## Error Types and Recovery

### 1. File Not Found Errors

**Pattern**: Check file existence before loading, provide clear guidance.

```python
import os

def safe_load_user(user_id, records_path, antennas_path=None):
    """Load user with proper error handling."""
    records_file = os.path.join(records_path, f"{user_id}.csv")

    if not os.path.exists(records_file):
        raise FileNotFoundError(
            f"Records file not found: {records_file}\n"
            f"Expected format: {records_path}/{user_id}.csv\n"
            f"Hint: Check that user_id matches the filename (without .csv)"
        )

    if antennas_path and not os.path.exists(antennas_path):
        print(f"Warning: Antennas file not found: {antennas_path}")
        print("Proceeding without antenna locations...")
        antennas_path = None

    return bc.read_csv(user_id, records_path, antennas_path, warnings=True)
```

### 2. Invalid CSV Format Errors

**Pattern**: Validate CSV structure before full processing.

```python
import csv

def validate_records_csv(filepath):
    """Validate records CSV format before loading."""
    required_columns = {'datetime', 'interaction', 'direction', 'correspondent_id'}
    optional_columns = {'call_duration', 'antenna_id', 'latitude', 'longitude'}

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])

        missing = required_columns - headers
        if missing:
            raise ValueError(
                f"Missing required columns: {missing}\n"
                f"Found columns: {headers}\n"
                f"Required: {required_columns}"
            )

        # Check first few rows for data quality
        for i, row in enumerate(reader):
            if i >= 5:
                break

            # Validate datetime format
            try:
                datetime.strptime(row['datetime'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(
                    f"Invalid datetime format in row {i+1}: '{row['datetime']}'\n"
                    f"Expected format: YYYY-MM-DD HH:MM:SS"
                )

            # Validate interaction type
            if row['interaction'] not in ('call', 'text', ''):
                raise ValueError(
                    f"Invalid interaction type in row {i+1}: '{row['interaction']}'\n"
                    f"Expected: 'call' or 'text'"
                )

    return True
```

### 3. Bandicoot Runtime Exceptions

**Pattern**: Catch and translate library exceptions into user-friendly messages.

```python
def run_indicator_safely(indicator_func, user, **kwargs):
    """Run a Bandicoot indicator with proper error handling."""
    try:
        return indicator_func(user, **kwargs)

    except ZeroDivisionError:
        return {
            'error': 'Insufficient data',
            'message': f'Not enough data to compute {indicator_func.__name__}',
            'suggestion': 'Ensure user has sufficient records for this indicator'
        }

    except KeyError as e:
        return {
            'error': 'Missing data',
            'message': f'Required data missing: {e}',
            'suggestion': 'Check that user data includes required fields'
        }

    except Exception as e:
        return {
            'error': type(e).__name__,
            'message': str(e),
            'suggestion': 'Review the error message and check input data'
        }
```

### 4. Network Analysis Errors

**Pattern**: Handle missing network data gracefully.

```python
def safe_network_analysis(user):
    """Run network analysis with proper checks."""
    if not user.has_network:
        return {
            'error': 'Network not loaded',
            'message': 'User was loaded without network data',
            'suggestion': 'Reload with bc.read_csv(..., network=True)'
        }

    results = {}

    try:
        results['clustering_unweighted'] = bc.network.clustering_coefficient_unweighted(user)
    except Exception as e:
        results['clustering_unweighted'] = {'error': str(e)}

    try:
        results['clustering_weighted'] = bc.network.clustering_coefficient_weighted(user)
    except Exception as e:
        results['clustering_weighted'] = {'error': str(e)}

    return results
```

## Standard Output Formatting

All commands should return results in consistent formats:

### Success Output
```python
{
    'status': 'success',
    'user_id': user.name,
    'indicator': 'call_duration',
    'result': {
        'allweek': {
            'allday': {
                'call': {'mean': 125.5, 'std': 45.2, 'min': 10, 'max': 450}
            }
        }
    }
}
```

### Error Output
```python
{
    'status': 'error',
    'user_id': user_id,
    'error_type': 'FileNotFoundError',
    'message': 'Records file not found: data/user123.csv',
    'suggestion': 'Check that the file exists and path is correct'
}
```

### Partial Success Output (Batch Processing)
```python
{
    'status': 'partial',
    'total': 10,
    'successful': 8,
    'failed': 2,
    'results': [...],
    'errors': [
        {'user_id': 'user5', 'error': 'FileNotFoundError'},
        {'user_id': 'user9', 'error': 'Invalid CSV format'}
    ]
}
```
```

---

## Slash Command Specifications

### Load Command: `commands/load.md`

```markdown
---
description: Load mobile phone records into Bandicoot for analysis
argument-hint: <user_id> <records_path> [antennas_path] [--network]
allowed-tools: Bash, Read
---

# Bandicoot: Load User Data

Load user phone records from CSV files into Bandicoot.

## Arguments
- `$1` or first argument: User ID (filename without .csv extension)
- `$2` or second argument: Path to directory containing records
- `$3` or third argument (optional): Path to antennas CSV file
- `--network` flag: Also load correspondent data for network analysis

## Execution

1. First, verify the conda environment is available:
```bash
conda run -n bandicoot python -c "import bandicoot as bc; print('Environment ready')"
```

2. Check that the records file exists:
```bash
ls "$2/$1.csv"
```

3. Load the user data with appropriate options based on arguments:

If antennas path provided ($3):
```python
import bandicoot as bc
user = bc.read_csv('$1', '$2', '$3', network=$NETWORK, describe=True)
```

If no antennas path:
```python
import bandicoot as bc
user = bc.read_csv('$1', '$2', describe=True)
```

4. Report the loading summary to the user, including:
   - Number of records loaded
   - Date range of records
   - Number of contacts
   - Whether home location was determined
   - Any warnings about data quality

## Examples

Load demo user:
```
/bandicoot:load ego demo/data/ demo/data/antennas.csv
```

Load with network:
```
/bandicoot:load ego demo/data/ demo/data/antennas.csv --network
```
```

### Analyze Command: `commands/analyze.md`

```markdown
---
description: Run complete Bandicoot analysis on loaded user data
argument-hint: <user_id> <records_path> [antennas_path] [--groupby=week] [--output=results.csv]
allowed-tools: Bash, Read, Write
---

# Bandicoot: Complete Analysis

Run all Bandicoot indicators on user phone records and export results.

## Arguments
- `$1`: User ID (filename without .csv)
- `$2`: Records directory path
- `$3` (optional): Antennas CSV path
- `--groupby`: Aggregation level (week/month/year/none), default: week
- `--output`: Output filename, default: {user_id}_analysis.csv

## Execution Steps

1. Run analysis using cross-platform conda execution:
```bash
conda run -n bandicoot python << 'EOF'
import bandicoot as bc

# Load user
user = bc.read_csv('$1', '$2', '$3' if '$3' else None, describe=True)

# Compute all indicators
results = bc.utils.all(user, groupby='$GROUPBY', summary='default')

# Export to CSV (bc.to_csv accepts single object or list)
bc.to_csv(results, '$OUTPUT')

# Also export to JSON for detailed inspection
bc.to_json(results, '$OUTPUT'.replace('.csv', '.json'))

print(f"Analysis complete. Results saved to $OUTPUT")
EOF
```

2. Summarize key findings:
   - Total records analyzed
   - Active days
   - Number of contacts
   - Average call duration
   - Percent nocturnal activity
   - Radius of gyration (mobility)
   - Percent at home

3. Highlight any data quality issues from the reporting section.

## Output Structure

The CSV output contains flattened indicators with naming convention:
`{indicator}__{time_split}__{day_split}__{interaction}__{stat}`

Example columns:
- `call_duration__allweek__allday__call__mean__mean`
- `percent_nocturnal__allweek__allday__call__mean`
- `radius_of_gyration__allweek__allday__mean`

## Examples

Basic analysis:
```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv
```

Monthly grouping:
```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --groupby=month
```

Custom output:
```
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --output=my_analysis.csv
```
```

### Quick Stats Command: `commands/quick-stats.md`

```markdown
---
description: Get quick summary statistics from Bandicoot user data
argument-hint: <user_id> <records_path> [antennas_path]
allowed-tools: Bash
---

# Bandicoot: Quick Statistics

Get a fast overview of key metrics without full analysis.

## Execution

```python
import bandicoot as bc

user = bc.read_csv('$1', '$2', '$3' if '$3' else None, describe=False, warnings=False)

# Quick stats
print(f"=== Quick Stats for {user.name} ===")
print(f"Records: {len(user.records)}")
print(f"Date range: {user.start_time} to {user.end_time}")
print(f"Unique contacts: {bc.individual.number_of_contacts(user, groupby=None)['allweek']['allday']['call']}")
print(f"Has calls: {user.has_call}")
print(f"Has texts: {user.has_text}")
print(f"Has home: {user.has_home}")

if user.has_call:
    duration = bc.individual.call_duration(user, groupby=None)
    print(f"Avg call duration: {duration['allweek']['allday']['call']['mean']:.1f}s")

if user.has_home:
    home_pct = bc.spatial.percent_at_home(user, groupby=None)
    print(f"Percent at home: {home_pct['allweek']['allday']:.1%}")
```
```

### Visualize Command: `commands/visualize.md`

```markdown
---
description: Start Bandicoot interactive visualization dashboard
argument-hint: <user_id> <records_path> [antennas_path] [--port=4242]
allowed-tools: Bash
---

# Bandicoot: Visualization Dashboard

Start the interactive D3.js visualization dashboard.

## Arguments
- `$1`: User ID
- `$2`: Records path
- `$3` (optional): Antennas path
- `--port`: Server port (default: 4242)

## Important Notes

1. The visualization runs a local HTTP server
2. Access via browser at http://localhost:{port}
3. Press Ctrl+C in terminal to stop the server
4. On Windows, use `localhost` not `0.0.0.0`

## Execution

```python
import bandicoot as bc

user = bc.read_csv('$1', '$2', '$3' if '$3' else None, describe=True)
print("Starting visualization server...")
print("Open http://localhost:$PORT in your browser")
print("Press Ctrl+C to stop")
bc.visualization.run(user, port=$PORT)
```

## Alternative: Export Static Files

To export without running server:
```python
path = bc.visualization.export(user, 'viz_output/')
print(f"Visualization exported to: {path}")
print("Start a local server with: python -m http.server 8000")
```
```

### Analyze Recharge Command: `commands/analyze-recharge.md`

```markdown
---
description: Analyze mobile phone recharge/top-up patterns
argument-hint: <user_id> <records_path> <recharges_path> [--groupby=week]
allowed-tools: Bash
---

# Bandicoot: Recharge Analysis

Analyze financial top-up patterns from mobile recharge data.

## Arguments
- `$1`: User ID
- `$2`: Records path
- `$3`: Recharges path (directory containing recharge CSV files)
- `--groupby`: Aggregation level (week/month/year/none)

## Execution

```python
import bandicoot as bc

user = bc.read_csv('$1', '$2', recharges_path='$3', describe=False, warnings=False)

if not user.has_recharges:
    print("Error: No recharges loaded. Check that recharges CSV exists at: $3/$1.csv")
    print("Expected format: datetime,amount,retailer_id")
else:
    print(f"=== Recharge Analysis for {user.name} ===")
    print(f"Total recharges: {len(user.recharges)}")

    # Compute recharge indicators
    amount = bc.recharge.amount_recharges(user, groupby='$GROUPBY')
    print(f"Amount stats: {amount}")

    num_recharges = bc.recharge.number_of_recharges(user, groupby='$GROUPBY')
    print(f"Number of recharges: {num_recharges}")

    interevent = bc.recharge.interevent_time_recharges(user, groupby='$GROUPBY')
    print(f"Time between recharges: {interevent}")

    pareto = bc.recharge.percent_pareto_recharges(user, groupby='$GROUPBY')
    print(f"Pareto concentration: {pareto}")

    if len(user.recharges) >= 2:
        avg_balance = bc.recharge.average_balance_recharges(user)
        print(f"Average daily balance: {avg_balance}")
```

## Notes

Recharge indicators measure:
- `amount_recharges`: Distribution of recharge amounts
- `number_of_recharges`: Count of top-ups
- `interevent_time_recharges`: Time between consecutive recharges
- `percent_pareto_recharges`: Concentration of recharge amounts (80/20 rule)
- `average_balance_recharges`: Estimated average daily balance
```

### Compare Users Command: `commands/compare.md`

```markdown
---
description: Compare behavioral indicators between multiple Bandicoot users
argument-hint: <user_ids...> <records_path> [antennas_path] [--output=comparison.csv]
allowed-tools: Bash, Write
---

# Bandicoot: Compare Users

Compare behavioral profiles across multiple users.

## Arguments
- `$@`: Space-separated list of user IDs
- `--records-path`: Directory containing user records
- `--antennas-path` (optional): Path to antennas CSV
- `--output`: Output CSV filename

## Execution

```python
import bandicoot as bc

user_ids = ['$USER_IDS']  # Split from arguments
records_path = '$RECORDS_PATH'
antennas_path = '$ANTENNAS_PATH' if '$ANTENNAS_PATH' else None

results = []
for user_id in user_ids:
    try:
        user = bc.read_csv(user_id, records_path, antennas_path, describe=False, warnings=False)
        result = bc.utils.all(user, groupby='week')
        results.append(result)
        print(f"Loaded: {user_id}")
    except Exception as e:
        print(f"Error loading {user_id}: {e}")

if len(results) > 1:
    bc.to_csv(results, '$OUTPUT')
    print(f"Comparison exported to: $OUTPUT")

    # Summary comparison
    print("\n=== Key Metric Comparison ===")
    for r in results:
        name = r['name']
        active = r.get('active_days', {}).get('allweek', {}).get('allday', {}).get('callandtext', 'N/A')
        contacts = r.get('number_of_contacts', {}).get('allweek', {}).get('allday', {}).get('call', 'N/A')
        print(f"{name}: Active days={active}, Contacts={contacts}")
```
```

### Generate Sample Command: `commands/generate-sample.md`

```markdown
---
description: Generate synthetic Bandicoot user data for testing
argument-hint: [--records=500] [--seed=42] [--network]
allowed-tools: Bash
---

# Bandicoot: Generate Sample Data

Generate synthetic user data for testing and experimentation.

## Arguments
- `--records`: Number of records to generate (default: 500)
- `--seed`: Random seed for reproducibility (default: 42)
- `--network`: Include network data (default: false)

## Execution

```python
import bandicoot as bc

# Generate synthetic user
user = bc.tests.sample_user(
    number_records=$RECORDS,
    seed=$SEED,
    pct_in_network=0.8 if $NETWORK else 0
)

# Describe the generated user
user.describe()

# Optionally run quick analysis
results = bc.utils.all(user, groupby=None)
print(f"\n=== Sample Analysis ===")
print(f"Active days: {results['active_days']['allweek']['allday']['callandtext']}")
print(f"Contacts: {results['number_of_contacts']['allweek']['allday']['call']}")
```

## Notes

The sample user generator creates:
- Random call and text records
- 7 antenna locations around Boston, MA (42.35N, -71.09W)
- A connected social network (if --network specified)
- Automatically computed home location
```

---

## Agent Specifications

### Network Analyst Agent: `agents/network-analyst.md`

Agents (subagents) in Claude Code are defined as markdown files in the `agents/` directory. They use a similar frontmatter format to skills but are designed for task delegation with separate context windows.

```markdown
---
name: bandicoot-network-analyst
description: |
  Use this agent for multi-user network analysis tasks involving Bandicoot.
  Handles loading multiple correspondents, computing network metrics, and
  analyzing social graph properties.

  <example>
  Context: User wants to analyze a social network from phone records
  user: "Analyze the network structure from the records in network_data/"
  assistant: "[Invokes network analyst agent for comprehensive analysis]"
  <commentary>
  Multi-user network analysis requires specialized orchestration.
  </commentary>
  </example>

model: sonnet
color: green
allowed-tools: Bash, Read, Write, Glob
---

# Bandicoot Network Analysis Agent

You are a specialized agent for analyzing social networks from mobile phone
metadata using Bandicoot.

## Your Responsibilities

1. **Data Discovery**: Find all user CSV files in the specified directory
2. **Network Loading**: Load the ego user with `network=True` to include correspondents
3. **Network Metrics**: Compute clustering coefficients, assortativity, and matrices
4. **Visualization**: Generate network visualizations when requested
5. **Interpretation**: Explain network structure and what metrics mean

## Workflow

### Step 1: Discover Data Files

```bash
ls -la $RECORDS_PATH/*.csv | head -20
```

### Step 2: Load Primary User with Network

```python
import bandicoot as bc

# Load ego user with full network
user = bc.read_csv(
    '$EGO_USER_ID',
    '$RECORDS_PATH',
    '$ANTENNAS_PATH',
    network=True,
    describe=True
)

print(f"Network size: {len(user.network)}")
print(f"Out-of-network calls: {user.percent_outofnetwork_calls:.1%}")
print(f"Out-of-network texts: {user.percent_outofnetwork_texts:.1%}")
```

### Step 3: Compute Network Metrics

```python
# Clustering coefficients
cc_unweighted = bc.network.clustering_coefficient_unweighted(user)
cc_weighted = bc.network.clustering_coefficient_weighted(user)

print(f"Clustering (unweighted): {cc_unweighted}")
print(f"Clustering (weighted): {cc_weighted}")

# Interaction matrices
matrix = bc.network.matrix_directed_weighted(user, interaction='call')
labels = bc.network.matrix_index(user)

print(f"Network nodes: {labels}")
```

### Step 4: Analyze Assortativity

```python
# How similar are connected users?
indicator_similarity = bc.network.assortativity_indicators(user)
print("Indicator Assortativity:")
for key, value in indicator_similarity.items():
    print(f"  {key}: {value}")
```

### Step 5: Export Results

```python
# Full analysis with network
results = bc.utils.all(user, network=True, groupby='week')
bc.to_csv(results, 'network_analysis.csv')
bc.to_json(results, 'network_analysis.json')
```

## Interpretation Guide

### Clustering Coefficient
- **0.0**: Contacts don't know each other (star network)
- **1.0**: All contacts know each other (complete subgraph)
- **Typical**: 0.1-0.4 for real social networks

### Out-of-Network Percentage
- **High (>50%)**: Many contacts not in dataset, incomplete network view
- **Low (<20%)**: Good network coverage, analysis more reliable

### Assortativity
- **Positive**: Similar people connect (homophily)
- **Negative**: Opposite people connect (heterophily)
- **Near zero**: Random mixing
```

### Batch Processor Agent: `agents/batch-processor.md`

```markdown
---
name: bandicoot-batch-processor
description: |
  Use this agent for processing multiple Bandicoot users in batch.
  Handles directory scanning, parallel processing considerations,
  error handling, and result aggregation.

model: sonnet
color: orange
allowed-tools: Bash, Read, Write, Glob
---

# Bandicoot Batch Processing Agent

You are a specialized agent for processing multiple users with Bandicoot.

## Workflow

### Step 1: Discover User Files

```python
import glob
import os

records_path = '$RECORDS_PATH'
user_files = sorted(glob.glob(os.path.join(records_path, '*.csv')))
user_ids = [os.path.basename(f)[:-4] for f in user_files]
print(f"Found {len(user_ids)} user files")
```

### Step 2: Process Users

```python
import bandicoot as bc

results = []
errors = []

for user_id in user_ids:
    try:
        user = bc.read_csv(user_id, records_path, antennas_path,
                          describe=False, warnings=False)
        result = bc.utils.all(user, groupby='$GROUPBY')
        results.append(result)
        print(f"Processed: {user_id}")
    except Exception as e:
        errors.append({'user_id': user_id, 'error': str(e)})
        print(f"Error processing {user_id}: {e}")

print(f"\nProcessed: {len(results)}, Errors: {len(errors)}")
```

### Step 3: Export Aggregated Results

```python
bc.to_csv(results, 'batch_results.csv')
print(f"Results exported to batch_results.csv")
```

## Error Handling

- Continue processing on individual user failures
- Log errors with user ID and error message
- Report summary at end with success/failure counts
```

---

## Workflow Encoding Patterns

### Pattern 1: Single User Analysis

```
User Request: "Analyze the phone records in demo/data/"
     |
     v
[Load Command] -> bc.read_csv()
     |
     v
[Analyze Command] -> bc.utils.all()
     |
     v
[Export] -> bc.to_csv() / bc.to_json()
     |
     v
[Interpret] -> Skill explains results
```

### Pattern 2: Network Analysis

```
User Request: "Analyze the social network from these records"
     |
     v
[Network Agent Triggered]
     |
     v
[Discover Files] -> glob.glob()
     |
     v
[Load with Network] -> bc.read_csv(network=True)
     |
     v
[Network Metrics] -> bc.network.*
     |
     v
[Visualize] -> bc.visualization.run()
     |
     v
[Export & Interpret] -> Results + Explanation
```

### Pattern 3: Batch Processing

```
User Request: "Process all users in the data/ directory"
     |
     v
[Batch Agent Triggered]
     |
     v
[File Discovery] -> List all CSVs
     |
     v
[Sequential Processing] -> Loop through users
     |
     v
[Error Handling] -> Continue on failures
     |
     v
[Aggregate Export] -> Combined CSV
```

### Pattern 4: Custom Indicator Development

```
User Request: "Create an indicator for average response time"
     |
     v
[Indicator Developer Agent]
     |
     v
[Understand Pattern] -> @grouping decorator
     |
     v
[Write Function] -> Python code
     |
     v
[Test] -> Run on sample data
     |
     v
[Validate] -> Compare expected vs actual
```

---

## Phase 1: Foundation

**Duration:** 1-2 days
**Goal:** Establish plugin structure and verify basic functionality

### Tasks

1. **Create Plugin Manifest (`.claude-plugin/plugin.json`)**

The plugin manifest must be located in `.claude-plugin/plugin.json`. Custom paths supplement default directories rather than replacing them.

```json
{
  "name": "bandicoot",
  "version": "1.0.0",
  "description": "Mobile phone metadata analysis using Bandicoot",
  "commands": "./commands",
  "skills": "./skills",
  "agents": "./agents",
  "hooks": "./hooks/hooks.json"
}
```

2. **Create Core Skill File**
   - `skills/bandicoot-analysis/SKILL.md` (as specified above)
   - Include indicator reference and troubleshooting guides

3. **Create Environment Verification Script**

```python
# skills/bandicoot-analysis/scripts/check-environment.py
import sys
try:
    import bandicoot as bc
    print(f"Bandicoot {bc.__version__} ready")
    sys.exit(0)
except ImportError as e:
    print(f"Bandicoot not available: {e}")
    sys.exit(1)
```

4. **Create Basic Load Command**
   - `commands/load.md`
   - Test with demo data

### Validation Checkpoint

```bash
# Verify plugin structure
ls -la bandicoot-plugin/
ls -la bandicoot-plugin/.claude-plugin/
ls -la bandicoot-plugin/commands/
ls -la bandicoot-plugin/skills/

# Test basic load
/bandicoot:load ego demo/data/ demo/data/antennas.csv
```

Expected output: User description with 314 records, 7 contacts, 27 antennas.

**Important Note on Session State:** Each slash command execution is independent. User objects loaded in `/bandicoot:load` do not persist to subsequent commands like `/bandicoot:analyze`. Commands should be designed to be self-contained (handle their own data loading) or clearly document that they must be run as part of a single Python script execution.

---

## Phase 2: Core Analysis Commands

**Duration:** 2-3 days
**Goal:** Implement all essential slash commands

### Tasks

1. **Implement Analysis Commands**
   - `commands/analyze.md` - Full analysis
   - `commands/analyze-individual.md` - Individual indicators only
   - `commands/analyze-spatial.md` - Spatial indicators only
   - `commands/quick-stats.md` - Fast summary

2. **Implement Export Commands**
   - `commands/export.md` - Export to CSV/JSON

3. **Implement Utility Commands**
   - `commands/describe.md` - User description
   - `commands/generate-sample.md` - Synthetic data
   - `commands/validate.md` - Data validation

4. **Create Result Interpretation Skill**
   - `skills/result-interpretation/SKILL.md`
   - `skills/result-interpretation/indicator-meanings.md`

### Validation Checkpoint

Run full analysis on demo data and compare with known output:

```bash
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --output=test_output.csv
```

Compare `test_output.csv` with `my_first_analysis.csv` (known-good output).

Key metrics to verify:
- `active_days__allweek__allday__callandtext__mean`: 5.5
- `number_of_contacts__allweek__allday__call__mean`: 5.14286
- `call_duration__allweek__allday__call__mean__mean`: 3776.70935

---

## Phase 3: Advanced Workflows

**Duration:** 4-5 days (revised from 2-3 days based on complexity assessment)
**Goal:** Implement agents and complex workflows

### Tasks

1. **Implement Network Analyst Agent**
   - `agents/network-analyst.md`
   - Test with sample network data

2. **Implement Batch Processor Agent**
   - `agents/batch-processor.md`
   - Test with multiple user files

3. **Implement Visualization Command**
   - `commands/visualize.md`
   - Handle server lifecycle

4. **Create Data Preparation Skill**
   - `skills/data-preparation/SKILL.md`
   - CSV format guidance
   - Common data issues

### Validation Checkpoint

Test network analysis:

```bash
# Generate sample network user
/bandicoot:generate-sample --records=500 --network

# Run network analysis
# Verify clustering coefficients computed
# Verify matrices generated
```

---

## Phase 4: Network Analysis Suite

**Duration:** 2-3 days
**Goal:** Complete network analysis capabilities

### Tasks

1. **Enhance Network Agent**
   - Add matrix visualization
   - Add assortativity analysis
   - Add network sampling

2. **Implement Network-Specific Commands**
   - `commands/analyze-network.md`
   - `commands/network-matrix.md`

3. **Create Network Analysis Documentation**
   - Add to skill resources
   - Include interpretation guides

### Validation Checkpoint

Run full network analysis on test data:

```python
user = bc.read_csv('sample_user', 'test_data/', network=True)
results = bc.utils.all(user, network=True)
```

Verify all network indicators computed successfully.

---

## Phase 5: Polish and Optimization

**Duration:** 1-2 days
**Goal:** Finalize, test, and document

### Tasks

1. **Create Hooks**
   - Output validation hook
   - Environment check hook

2. **Create Comprehensive Tests**
   - Test all commands
   - Test all agents
   - Verify against known outputs

3. **Documentation**
   - README.md with usage examples
   - Troubleshooting guide
   - Quick reference card

4. **Optimization**
   - Review command efficiency
   - Simplify complex workflows

### Final Validation

Complete end-to-end test:

```bash
# 1. Verify environment
/bandicoot:validate

# 2. Load data
/bandicoot:load ego demo/data/ demo/data/antennas.csv

# 3. Run analysis
/bandicoot:analyze ego demo/data/ demo/data/antennas.csv

# 4. Verify outputs match expected
# Compare with my_first_analysis.csv

# 5. Test network analysis
/bandicoot:analyze-network sample_user test_data/ test_data/antennas.csv

# 6. Test visualization (manual)
/bandicoot:visualize ego demo/data/ demo/data/antennas.csv
```

---

## Validation Strategy

### Known-Good Outputs

We have validated outputs from testing:

**File:** `my_first_analysis.csv` (ego user)
- 314 records, 8 weeks
- Key values to verify:
  - `active_days__allweek__allday__callandtext__mean`: 5.5
  - `number_of_contacts__allweek__allday__call__mean`: 5.14286
  - `call_duration__allweek__allday__call__mean__mean`: 3776.70935
  - `radius_of_gyration__allweek__allday__mean`: 1.45038

**File:** `network_analysis.csv` (synthetic network user)
- 500 records, 10 weeks
- Network metrics computed
- 48 contacts in network

### Validation Script

```python
# resources/validate-output.py
import csv
import sys

def validate(actual_file, expected_file, tolerance=0.001):
    with open(actual_file) as f1, open(expected_file) as f2:
        actual = list(csv.DictReader(f1))[0]
        expected = list(csv.DictReader(f2))[0]

    errors = []
    for key in expected:
        if key in actual:
            try:
                exp_val = float(expected[key])
                act_val = float(actual[key])
                if abs(exp_val - act_val) > tolerance:
                    errors.append(f"{key}: expected {exp_val}, got {act_val}")
            except ValueError:
                if expected[key] != actual[key]:
                    errors.append(f"{key}: expected {expected[key]}, got {actual[key]}")

    if errors:
        print("Validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("Validation PASSED")
        return True

if __name__ == "__main__":
    validate(sys.argv[1], sys.argv[2])
```

---

## Testing Approach

### Unit Tests (Per Command)

```bash
# Test each command individually
/bandicoot:load ego demo/data/ demo/data/antennas.csv
# Expected: User loaded successfully with 314 records

/bandicoot:quick-stats ego demo/data/ demo/data/antennas.csv
# Expected: Summary statistics displayed

/bandicoot:analyze ego demo/data/ demo/data/antennas.csv --output=test.csv
# Expected: test.csv created with all indicators
```

### Integration Tests (Workflows)

```bash
# Test complete workflow
1. /bandicoot:generate-sample --records=100 --seed=42
2. /bandicoot:analyze sample_user . --groupby=none
3. Verify results are consistent
```

### Regression Tests

Compare outputs against known-good files after each change.

---

## Pros and Cons Analysis

### Pros

| Advantage | Description |
|-----------|-------------|
| **Zero Infrastructure** | No server to deploy or maintain |
| **Direct Python Access** | Full Bandicoot API available |
| **Simple Implementation** | Markdown files with natural language |
| **Fast Iteration** | Easy to modify and test |
| **Native Integration** | Uses Claude Code's built-in tools |
| **Portable** | Works anywhere conda is available |
| **Transparent** | Commands are readable Python code |
| **Extensible** | Easy to add new commands/skills |

### Cons

| Disadvantage | Description | Mitigation |
|--------------|-------------|------------|
| **No Schema Enforcement** | Parameters not type-checked | Validation in skill prompts |
| **Sequential Execution** | No true parallelism | Batch agent handles loops |
| **Environment Dependency** | Requires conda setup | Check script included |
| **Error Handling** | Python errors surface raw | Skill provides context |
| **No Caching** | Results not persisted | User can save outputs |
| **Manual Orchestration** | Complex workflows need agents | Pre-built agents provided |

---

## Comparison with MCP Approach

| Aspect | Skills Approach | MCP Approach |
|--------|-----------------|--------------|
| **Setup Complexity** | Low (markdown files) | Medium (Python server) |
| **Type Safety** | None (natural language) | Strong (schema validation) |
| **Tool Discovery** | Via skill prompts | Via MCP protocol |
| **Error Handling** | Manual/skill-based | Structured responses |
| **Debugging** | Read Python output | Server logs |
| **Maintenance** | Edit markdown | Edit Python code |
| **Portability** | Needs conda | Needs MCP client |
| **Performance** | Shell overhead | Direct calls |
| **Best For** | Quick integration | Production system |

### Recommendation

**Use Skills Approach when:**
- Rapid prototyping needed
- Team comfortable with markdown
- Workflows are well-defined
- Direct Python access valuable

**Use MCP Approach when:**
- Production deployment required
- Type safety important
- Multiple clients need access
- Structured error handling needed

---

## Risk Mitigation

### Risk 1: Conda Environment Issues

**Mitigation:**
- Environment check command/hook
- Clear setup documentation
- Fallback to pip install

### Risk 2: Large Dataset Performance

**Mitigation:**
- Batch processor agent
- Chunked processing patterns
- Progress reporting

### Risk 3: Data Format Errors

**Mitigation:**
- Data preparation skill
- Validation command
- Clear error messages in skill

### Risk 4: Result Interpretation

**Mitigation:**
- Interpretation skill
- Indicator reference documentation
- Benchmark values

### Implementation Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1: Foundation** | 1-2 days | Plugin manifest, core skill, environment verification |
| **Phase 2: Core Analysis** | 2-3 days | All analysis commands, export, utilities |
| **Phase 3: Advanced Workflows** | 4-5 days | Agents, visualization, data preparation skill |
| **Phase 4: Network Suite** | 2-3 days | Network analysis, matrix operations |
| **Phase 5: Polish** | 1-2 days | Hooks, testing, documentation |
| **Total** | **10-15 days** | Complete Bandicoot integration |

**Note:** These estimates include time for testing, validation against known outputs, and documentation. Original estimates (8-13 days) were revised upward based on complexity assessment of Phase 3 workflows.

---

## Appendix: Reference Commands

### Quick Reference Card

**Note:** This Quick Reference Card is also available as a skill resource at `skills/bandicoot-analysis/quick-reference.md` for easy Claude Code access.

```
LOADING DATA
/bandicoot:load <user_id> <records_path> [antennas_path] [--network]
/bandicoot:generate-sample [--records=500] [--seed=42] [--network]

ANALYSIS
/bandicoot:analyze <user_id> <records_path> [antennas_path] [--groupby=week]
/bandicoot:analyze-individual <user_id> <records_path>
/bandicoot:analyze-spatial <user_id> <records_path> <antennas_path>
/bandicoot:analyze-network <user_id> <records_path> <antennas_path>
/bandicoot:quick-stats <user_id> <records_path>

EXPORT & VISUALIZATION
/bandicoot:export <user_id> <records_path> --format=csv|json
/bandicoot:visualize <user_id> <records_path> [--port=4242]

UTILITIES
/bandicoot:describe <user_id> <records_path>
/bandicoot:validate <user_id> <records_path>
/bandicoot:batch <records_directory> --output=results.csv
```

### Python Command Reference

```python
import bandicoot as bc

# Loading
user = bc.read_csv('user_id', 'path/', 'antennas.csv', network=True)
user = bc.tests.sample_user(number_records=500, seed=42)

# Individual Indicators
bc.individual.active_days(user)
bc.individual.number_of_contacts(user, direction='out', more=5)
bc.individual.call_duration(user, direction='in')
bc.individual.percent_nocturnal(user)
bc.individual.entropy_of_contacts(user, normalize=True)
bc.individual.percent_pareto_interactions(user, percentage=0.8)

# Spatial Indicators
bc.spatial.number_of_antennas(user)
bc.spatial.radius_of_gyration(user)
bc.spatial.percent_at_home(user)
bc.spatial.churn_rate(user)

# Network Indicators
bc.network.clustering_coefficient_unweighted(user)
bc.network.clustering_coefficient_weighted(user)
bc.network.assortativity_indicators(user)
bc.network.matrix_directed_weighted(user)

# Batch & Export
results = bc.utils.all(user, groupby='week', summary='default')
bc.to_csv([results], 'output.csv')
bc.to_json(results, 'output.json')

# Visualization
bc.visualization.run(user, port=4242)
bc.visualization.export(user, 'viz_dir/')
```

---

**Document Version:** 1.2
**Last Updated:** January 2026
**Author:** Claude Code Architecture Team

---

*This plan provides a comprehensive roadmap for implementing Bandicoot integration via Claude Code skills. Follow the phases sequentially, validating at each checkpoint before proceeding.*

---

## Revision Notes (v1.2)

This section documents changes made in version 1.2 to address all outstanding review items.

### New Additions in v1.2

| Addition | Description | Outstanding Item Addressed |
|----------|-------------|----------------------------|
| **Recharge command** | `commands/analyze-recharge.md` with full specification | M1: Recharge Indicators Missing |
| **Compare command** | `commands/compare.md` for multi-user comparison | Priority 3: Comparison workflow |
| **Path validation script** | `scripts/validate-path.py` with Windows support | M2: Path Validation Missing |
| **Error handling patterns** | `error-patterns.md` with 4 pattern types | M3: Error Recovery Patterns Undefined |
| **Updated Phase 3 duration** | 4-5 days (from 2-3 days) | M4: Duration Estimates Low |
| **Timeline summary table** | Complete implementation timeline | M4: Duration Estimates Low |
| **Quick Reference note** | Added skill resource location note | L2: Quick Reference accessibility |
| **Standard output formatting** | Success/Error/Partial output patterns | Priority 2: Standardize output |

### Additional Enhancements

- Added `--split-week`, `--split-day`, `--summary`, `--date-range` parameter documentation references in relevant commands
- Enhanced directory structure to include `error-patterns.md` and `validate-path.py`
- Color field retention documented as optional/experimental (L1 addressed via documentation)

---

## Revision Notes (v1.1)

This section documents changes made after expert review and independent verification against Claude Code documentation and Bandicoot source code.

### Critical Fixes Applied

| Issue | Original | Corrected | Verification Source |
|-------|----------|-----------|---------------------|
| **Plugin manifest location** | `plugin.json` at root | `.claude-plugin/plugin.json` | Claude Code official docs, Context7 |
| **Frontmatter tools field** | `tools: ["Bash", "Read"]` | `allowed-tools: Bash, Read` | Claude Code frontmatter reference |
| **Conda activation (Windows)** | `conda activate && python` | `conda run -n bandicoot python` | Cross-platform compatibility best practice |

### High-Priority Fixes Applied

| Issue | Original | Corrected | Notes |
|-------|----------|-----------|-------|
| **Model field** | `model: inherit` | `model: sonnet` | Valid values: `sonnet`, `opus`, `haiku`. Review incorrectly stated this field was invalid - it IS valid per Claude Code docs |
| **Agents directory** | Incorrectly flagged as invalid | **RETAINED** - `agents/` IS valid | Review was incorrect; Claude Code supports `agents/` directory for subagent definitions |
| **hooks.json** | Incorrectly flagged as invalid | **RETAINED** - `hooks/hooks.json` IS valid | Review was incorrect; Claude Code supports hooks with wrapper format `{"hooks": {...}}` |

### Session State Clarification

Added explicit documentation that slash command executions are independent - User objects do not persist between separate command invocations. Commands should be self-contained or designed to work within a single Python execution context.

### Review Assessment

The original review (Bandicoot_Skills_Plan_Review.md) contained several inaccuracies that were corrected through independent verification:

1. **plugin.json**: Review was PARTIALLY CORRECT - location was wrong in plan, but format does exist
2. **tools field**: Review was PARTIALLY CORRECT - wrong syntax (`tools:` vs `allowed-tools:`), but the field itself is valid
3. **model field**: Review was INCORRECT - `model` is a valid field accepting `sonnet`, `opus`, `haiku`
4. **agents/ directory**: Review was INCORRECT - Claude Code DOES support `agents/` for subagents
5. **hooks.json**: Review was INCORRECT - Claude Code DOES support `hooks/hooks.json`
6. **Windows conda**: Review was CORRECT - `conda run` is more portable

### Bandicoot API Verification

Verified against `bandicoot/io.py` source code:
- `bc.to_csv()` accepts BOTH single objects AND lists (auto-wraps non-lists at line 71-72)
- `bc.to_csv()` DOES have a `warnings` parameter (defaults to `True`)
- `bc.to_json()` has the same signature pattern

### Sources Consulted

- Claude Code official documentation: https://code.claude.com/docs/en/skills
- Claude Code GitHub: https://github.com/anthropics/claude-code
- Context7 documentation library for Claude Code
- Bandicoot source: `bandicoot/io.py` (lines 46-97, 99-132)
