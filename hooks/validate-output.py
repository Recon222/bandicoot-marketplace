#!/usr/bin/env python
"""
Post-command hook to validate Bandicoot output files.
Runs after analyze commands to verify output integrity.
"""
import os
import sys
import csv
import json


def validate_csv(filepath):
    """Validate a CSV output file."""
    issues = []

    if not os.path.exists(filepath):
        return [f"File not found: {filepath}"]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Check header exists
            if not reader.fieldnames:
                issues.append("CSV has no header row")
                return issues

            # Check for expected columns
            expected_cols = {'key', 'value'}  # Bandicoot format
            if not expected_cols.issubset(set(reader.fieldnames)):
                # Check for flattened format
                if 'user_id' not in reader.fieldnames and len(reader.fieldnames) < 2:
                    issues.append("CSV missing expected columns")

            # Count rows
            row_count = sum(1 for _ in reader)

            if row_count == 0:
                issues.append("CSV has no data rows")

    except csv.Error as e:
        issues.append(f"CSV parsing error: {e}")
    except Exception as e:
        issues.append(f"Error reading CSV: {e}")

    return issues


def validate_json(filepath):
    """Validate a JSON output file."""
    issues = []

    if not os.path.exists(filepath):
        return [f"File not found: {filepath}"]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check it's a non-empty dict or list
        if isinstance(data, dict):
            if not data:
                issues.append("JSON object is empty")
        elif isinstance(data, list):
            if not data:
                issues.append("JSON array is empty")
        else:
            issues.append(f"Unexpected JSON type: {type(data)}")

    except json.JSONDecodeError as e:
        issues.append(f"Invalid JSON: {e}")
    except Exception as e:
        issues.append(f"Error reading JSON: {e}")

    return issues


def find_recent_outputs(directory='.', max_age_seconds=60):
    """Find recently created output files."""
    import time

    now = time.time()
    outputs = []

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if not os.path.isfile(filepath):
            continue

        # Check if file was recently created
        mtime = os.path.getmtime(filepath)
        if now - mtime > max_age_seconds:
            continue

        # Check file type
        if filename.endswith('.csv') or filename.endswith('.json'):
            outputs.append(filepath)

    return outputs


def main():
    """Main validation routine."""
    print("Validating Bandicoot output files...")

    # Find recent outputs
    outputs = find_recent_outputs()

    if not outputs:
        print("No recent output files found to validate.")
        return 0

    all_issues = []

    for filepath in outputs:
        if filepath.endswith('.csv'):
            issues = validate_csv(filepath)
        elif filepath.endswith('.json'):
            issues = validate_json(filepath)
        else:
            continue

        if issues:
            all_issues.extend([(filepath, issue) for issue in issues])
            print(f"WARN: {filepath}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"OK: {filepath}")

    if all_issues:
        print(f"\n{len(all_issues)} validation issue(s) found")
        return 1

    print("\nAll output files validated successfully")
    return 0


if __name__ == '__main__':
    sys.exit(main())
