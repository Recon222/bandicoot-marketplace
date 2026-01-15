#!/usr/bin/env python
"""
Pre-command hook to validate input data before loading.
Provides early warning about data format issues.
"""
import os
import sys
import csv
from datetime import datetime


def check_csv_format(filepath, max_rows=100):
    """
    Quick validation of CSV format for Bandicoot compatibility.

    Returns (is_valid, warnings, errors)
    """
    warnings = []
    errors = []

    if not os.path.exists(filepath):
        return False, [], [f"File not found: {filepath}"]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Check required columns
            required = {'datetime', 'interaction', 'direction', 'correspondent_id'}
            if reader.fieldnames is None:
                return False, [], ["CSV has no header row"]

            missing = required - set(reader.fieldnames)
            if missing:
                errors.append(f"Missing required columns: {missing}")

            # Check optional columns
            optional = {'call_duration', 'antenna_id', 'latitude', 'longitude'}
            present_optional = optional & set(reader.fieldnames)

            if not present_optional:
                warnings.append("No optional columns (call_duration, antenna_id, etc.)")

            # Sample rows for validation
            datetime_errors = 0
            interaction_errors = 0
            direction_errors = 0

            for i, row in enumerate(reader):
                if i >= max_rows:
                    break

                # Check datetime format
                dt = row.get('datetime', '')
                try:
                    datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    datetime_errors += 1

                # Check interaction
                interaction = row.get('interaction', '')
                if interaction and interaction not in ('call', 'text', ''):
                    interaction_errors += 1

                # Check direction
                direction = row.get('direction', '')
                if direction not in ('in', 'out'):
                    direction_errors += 1

            # Report errors
            if datetime_errors > 0:
                errors.append(
                    f"{datetime_errors}/{min(i+1, max_rows)} rows have invalid datetime format "
                    "(expected YYYY-MM-DD HH:MM:SS)"
                )

            if interaction_errors > 0:
                errors.append(
                    f"{interaction_errors}/{min(i+1, max_rows)} rows have invalid interaction "
                    "(expected 'call' or 'text')"
                )

            if direction_errors > 0:
                errors.append(
                    f"{direction_errors}/{min(i+1, max_rows)} rows have invalid direction "
                    "(expected 'in' or 'out')"
                )

    except csv.Error as e:
        errors.append(f"CSV parsing error: {e}")
    except UnicodeDecodeError as e:
        errors.append(f"Encoding error (try UTF-8): {e}")
    except Exception as e:
        errors.append(f"Error reading file: {e}")

    is_valid = len(errors) == 0
    return is_valid, warnings, errors


def main():
    """Main validation routine."""
    # Get file path from command line or environment
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = os.environ.get('BANDICOOT_INPUT_FILE', '')

    if not filepath:
        print("No input file specified for validation")
        return 0  # Don't fail if no file specified

    print(f"Pre-validating input data: {filepath}")

    is_valid, warnings, errors = check_csv_format(filepath)

    # Print results
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")
        print("\nData validation failed. Fix the errors above before proceeding.")
        return 1

    print("\nData format validation passed!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
