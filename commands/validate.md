---
description: Validate Bandicoot environment and data files
argument-hint: [--env-only] [--user USER_ID --data PATH] [--antennas PATH] [--list-users]
---

# Bandicoot: Validate

Validate your Bandicoot environment and CDR data files using the included validation script.

**Note**: This command uses a bundled validation script (`scripts/validate.py`)
from the plugin. This is an EXCEPTION to the "no wrapper scripts" guidance -
this script is part of the plugin distribution, not a wrapper around Bandicoot
functions. You are running it, not creating it.

For actual Bandicoot analysis after validation passes, use inline Python calls.

## Usage

Run the validation script from the plugin's scripts directory:

```bash
python {plugin_path}/scripts/validate.py [options]
```

**Note:** Replace `{plugin_path}` with the actual path to the bandicoot plugin, or if using a conda environment, run with:

```bash
conda run -n {conda_env} python {plugin_path}/scripts/validate.py [options]
```

Check the project's CLAUDE.md for the correct conda environment name.

## Options

| Option | Description |
|--------|-------------|
| `--env-only` | Only check environment, skip data validation |
| `--user USER_ID` | User ID to validate (filename without .csv) |
| `--data PATH` | Path to directory containing CSV data files |
| `--antennas PATH` | Path to antennas CSV file (optional) |
| `--list-users` | List available user CSV files in the data directory |

## Examples

### Check Environment Only

```bash
python scripts/validate.py --env-only
```

Validates:
- Python version
- Bandicoot installation and version
- All Bandicoot submodules (core, individual, spatial, network, recharge, io, utils)
- Optional dependencies (numpy, scipy, networkx)

### List Available Users

```bash
python scripts/validate.py --list-users --data data/
```

Shows all CSV files in the data directory with their sizes.

### Validate Specific User

```bash
python scripts/validate.py --user sample_user_PRIMARY --data data/
```

Validates:
- Records file exists
- CSV format (required columns, data types)
- Sample row validation (datetime format, interaction types, direction)
- Actual Bandicoot load test

### Full Validation with Antennas

```bash
python scripts/validate.py --user ego --data demo/data/ --antennas demo/data/antennas.csv
```

Additionally validates:
- Antennas file exists
- Required columns (antenna_id, latitude, longitude)
- Coordinate validity

## Output

The script uses clear status indicators:

- `[OK]` - Check passed
- `[FAIL]` - Check failed (see details)
- `[WARN]` - Warning (non-fatal issue)
- `[INFO]` - Informational message

## Exit Codes

- `0` - All validations passed
- `1` - One or more validations failed

## Common Issues

### "Bandicoot not installed"

Install bandicoot in your Python environment:

```bash
pip install bandicoot
```

Or with conda:

```bash
conda install -c conda-forge bandicoot
```

### "Records file not found"

- Check that `user_id` matches the filename (without .csv extension)
- Use `--list-users --data PATH` to see available files
- Verify the data path is correct

### "Invalid datetime format"

Bandicoot expects: `YYYY-MM-DD HH:MM:SS`

Example: `2014-03-02 07:13:30`

### "Invalid interaction/direction"

- `interaction` must be `call` or `text` (lowercase)
- `direction` must be `in` or `out` (lowercase)
