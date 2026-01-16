# Bandicoot Error Handling Patterns

This document defines standard error handling patterns for all commands and skills.

**Note on code examples**: The patterns below demonstrate error handling
approaches and diagnostic techniques. Use them inline to diagnose issues -
do not create wrapper scripts that add error handling around Bandicoot calls.

## Error Types and Recovery

### 1. File Not Found Errors

**Pattern**: Check file existence before loading, provide clear guidance.

```python
import os
import bandicoot as bc

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

**Recovery actions**:
- Verify file path spelling and case
- Check that directory exists
- Ensure user_id matches CSV filename (without extension)
- List available files in directory to find correct name

---

### 2. Invalid CSV Format Errors

**Pattern**: Validate CSV structure before full processing.

```python
import csv
from datetime import datetime

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

            # Validate direction
            if row['direction'] not in ('in', 'out'):
                raise ValueError(
                    f"Invalid direction in row {i+1}: '{row['direction']}'\n"
                    f"Expected: 'in' or 'out'"
                )

    return True
```

**Recovery actions**:
- Fix column names to match expected format
- Convert datetime to YYYY-MM-DD HH:MM:SS
- Ensure interaction values are lowercase 'call' or 'text'
- Ensure direction values are lowercase 'in' or 'out'

---

### 3. Bandicoot Runtime Exceptions

**Pattern**: Catch and translate library exceptions into user-friendly messages.

```python
def run_indicator_safely(indicator_func, user, **kwargs):
    """Run a Bandicoot indicator with proper error handling."""
    try:
        return {
            'status': 'success',
            'result': indicator_func(user, **kwargs)
        }

    except ZeroDivisionError:
        return {
            'status': 'error',
            'error_type': 'InsufficientData',
            'message': f'Not enough data to compute {indicator_func.__name__}',
            'suggestion': 'Ensure user has sufficient records for this indicator'
        }

    except KeyError as e:
        return {
            'status': 'error',
            'error_type': 'MissingData',
            'message': f'Required data missing: {e}',
            'suggestion': 'Check that user data includes required fields'
        }

    except AttributeError as e:
        return {
            'status': 'error',
            'error_type': 'InvalidState',
            'message': f'User object in invalid state: {e}',
            'suggestion': 'Reload user data and try again'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error_type': type(e).__name__,
            'message': str(e),
            'suggestion': 'Review the error message and check input data'
        }
```

---

### 4. Network Analysis Errors

**Pattern**: Handle missing network data gracefully.

```python
def safe_network_analysis(user):
    """Run network analysis with proper checks."""
    if not user.has_network:
        return {
            'status': 'error',
            'error_type': 'NetworkNotLoaded',
            'message': 'User was loaded without network data',
            'suggestion': 'Reload with bc.read_csv(..., network=True)'
        }

    if len(user.network) == 0:
        return {
            'status': 'warning',
            'message': 'Network is empty - no correspondent files found',
            'suggestion': 'Ensure correspondent CSV files exist in the same directory'
        }

    results = {'status': 'success', 'indicators': {}}

    # Try each network indicator
    try:
        results['indicators']['clustering_unweighted'] = \
            bc.network.clustering_coefficient_unweighted(user)
    except Exception as e:
        results['indicators']['clustering_unweighted'] = {'error': str(e)}

    try:
        results['indicators']['clustering_weighted'] = \
            bc.network.clustering_coefficient_weighted(user)
    except Exception as e:
        results['indicators']['clustering_weighted'] = {'error': str(e)}

    try:
        results['indicators']['assortativity_indicators'] = \
            bc.network.assortativity_indicators(user)
    except Exception as e:
        results['indicators']['assortativity_indicators'] = {'error': str(e)}

    return results
```

---

## Standard Output Formatting

All commands should return results in consistent formats:

### Success Output

```python
{
    'status': 'success',
    'user_id': 'ego',
    'indicator': 'call_duration',
    'parameters': {
        'groupby': 'week',
        'summary': 'default'
    },
    'result': {
        'allweek': {
            'allday': {
                'call': {
                    'mean': {'mean': 125.5, 'std': 45.2},
                    'std': {'mean': 80.1, 'std': 30.5}
                }
            }
        }
    }
}
```

### Error Output

```python
{
    'status': 'error',
    'user_id': 'ego',
    'error_type': 'FileNotFoundError',
    'message': 'Records file not found: data/ego.csv',
    'suggestion': 'Check that the file exists and path is correct',
    'context': {
        'records_path': 'data/',
        'expected_file': 'data/ego.csv'
    }
}
```

### Warning Output

```python
{
    'status': 'warning',
    'user_id': 'ego',
    'warning_type': 'DataQuality',
    'message': '15% of records are missing location data',
    'suggestion': 'Check antenna file path and antenna_id matching',
    'result': {...}  # Analysis still completed
}
```

### Partial Success Output (Batch Processing)

```python
{
    'status': 'partial',
    'summary': {
        'total': 10,
        'successful': 8,
        'failed': 2
    },
    'results': [
        {'user_id': 'user1', 'status': 'success', 'result': {...}},
        {'user_id': 'user2', 'status': 'success', 'result': {...}},
        # ... more results
    ],
    'errors': [
        {
            'user_id': 'user5',
            'error_type': 'FileNotFoundError',
            'message': 'Records file not found'
        },
        {
            'user_id': 'user9',
            'error_type': 'ValueError',
            'message': 'Invalid CSV format'
        }
    ]
}
```

---

## Error Recovery Workflow

When encountering errors, follow this decision tree:

```
Error Occurred
    |
    v
Is it a FileNotFoundError?
    |
    +--> YES: Check file paths, list directory contents, suggest corrections
    |
    +--> NO: Is it a ValueError (data format)?
              |
              +--> YES: Run validation script, identify specific issues
              |
              +--> NO: Is it a runtime error during analysis?
                        |
                        +--> YES: Check data quality, try with different parameters
                        |
                        +--> NO: Report error with full context, suggest manual review
```

---

## Logging Best Practices

```python
import logging

# Configure logging for Bandicoot operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('bandicoot')

def logged_analysis(user_id, records_path, **kwargs):
    """Run analysis with comprehensive logging."""
    logger.info(f"Starting analysis for user: {user_id}")
    logger.info(f"Records path: {records_path}")

    try:
        user = bc.read_csv(user_id, records_path, **kwargs)
        logger.info(f"Loaded {len(user.records)} records")
        logger.info(f"Date range: {user.start_time} to {user.end_time}")

        if user.ignored_records and user.ignored_records.get('all', 0) > 0:
            logger.warning(f"Ignored records: {user.ignored_records}")

        results = bc.utils.all(user)
        logger.info("Analysis completed successfully")
        return results

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise

    except ValueError as e:
        logger.error(f"Data validation error: {e}")
        raise

    except Exception as e:
        logger.exception(f"Unexpected error during analysis")
        raise
```

---

## User-Facing Error Messages

When reporting errors to users, follow these guidelines:

1. **Be specific**: State exactly what went wrong
2. **Provide context**: Include relevant file paths, values, etc.
3. **Suggest solutions**: Give actionable steps to fix the issue
4. **Avoid jargon**: Use clear, non-technical language where possible

**Good example**:
```
Error: Cannot load user data

The records file was not found at: demo/data/user123.csv

To fix this:
1. Check that 'user123.csv' exists in the 'demo/data/' directory
2. Verify the file name matches exactly (including case)
3. Ensure the path is correct relative to your current location

Current directory: /home/user/project
Files in demo/data/: ego.csv, sample.csv
```

**Bad example**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'demo/data/user123.csv'
```
