#!/usr/bin/env python
"""
Data validation script for Bandicoot plugin.
Validates CSV file format and data quality before analysis.
"""
from __future__ import print_function, division
import csv
import os
import sys
from datetime import datetime


def validate_records_csv(filepath, verbose=True):
    """
    Validate records CSV file format for Bandicoot compatibility.

    Parameters
    ----------
    filepath : str
        Path to the records CSV file
    verbose : bool
        Print detailed output

    Returns
    -------
    dict
        Validation results with 'valid', 'errors', 'warnings', 'stats' keys
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'stats': {
            'total_rows': 0,
            'valid_rows': 0,
            'calls': 0,
            'texts': 0,
            'incoming': 0,
            'outgoing': 0,
            'unique_contacts': set(),
            'unique_antennas': set(),
            'date_range': [None, None]
        }
    }

    required_columns = {'datetime', 'interaction', 'direction', 'correspondent_id'}
    optional_columns = {'call_duration', 'antenna_id', 'latitude', 'longitude'}

    if not os.path.exists(filepath):
        results['valid'] = False
        results['errors'].append(f"File not found: {filepath}")
        return results

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])

            # Check required columns
            missing = required_columns - headers
            if missing:
                results['valid'] = False
                results['errors'].append(f"Missing required columns: {missing}")
                return results

            # Note extra columns
            extra = headers - required_columns - optional_columns
            if extra:
                results['warnings'].append(f"Extra columns (will be ignored): {extra}")

            # Validate each row
            for row_num, row in enumerate(reader, start=2):
                results['stats']['total_rows'] += 1
                row_valid = True

                # Validate datetime
                dt_str = row.get('datetime', '')
                try:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

                    # Track date range
                    if results['stats']['date_range'][0] is None or dt < results['stats']['date_range'][0]:
                        results['stats']['date_range'][0] = dt
                    if results['stats']['date_range'][1] is None or dt > results['stats']['date_range'][1]:
                        results['stats']['date_range'][1] = dt
                except ValueError:
                    row_valid = False
                    if len(results['errors']) < 10:
                        results['errors'].append(
                            f"Row {row_num}: Invalid datetime format '{dt_str}' "
                            f"(expected YYYY-MM-DD HH:MM:SS)"
                        )

                # Validate interaction
                interaction = row.get('interaction', '')
                if interaction not in ('call', 'text', ''):
                    row_valid = False
                    if len(results['errors']) < 10:
                        results['errors'].append(
                            f"Row {row_num}: Invalid interaction '{interaction}' "
                            f"(expected 'call' or 'text')"
                        )
                elif interaction == 'call':
                    results['stats']['calls'] += 1
                elif interaction == 'text':
                    results['stats']['texts'] += 1

                # Validate direction
                direction = row.get('direction', '')
                if direction not in ('in', 'out'):
                    row_valid = False
                    if len(results['errors']) < 10:
                        results['errors'].append(
                            f"Row {row_num}: Invalid direction '{direction}' "
                            f"(expected 'in' or 'out')"
                        )
                elif direction == 'in':
                    results['stats']['incoming'] += 1
                elif direction == 'out':
                    results['stats']['outgoing'] += 1

                # Validate correspondent_id
                correspondent = row.get('correspondent_id', '')
                if not correspondent:
                    row_valid = False
                    if len(results['errors']) < 10:
                        results['errors'].append(
                            f"Row {row_num}: Missing correspondent_id"
                        )
                else:
                    results['stats']['unique_contacts'].add(correspondent)

                # Validate call_duration (optional)
                if interaction == 'call':
                    duration = row.get('call_duration', '')
                    if duration:
                        try:
                            dur_val = int(duration)
                            if dur_val < 0:
                                results['warnings'].append(
                                    f"Row {row_num}: Negative call_duration {dur_val}"
                                )
                        except ValueError:
                            if len(results['warnings']) < 10:
                                results['warnings'].append(
                                    f"Row {row_num}: Invalid call_duration '{duration}'"
                                )

                # Track antennas
                antenna = row.get('antenna_id', '')
                if antenna:
                    results['stats']['unique_antennas'].add(antenna)

                if row_valid:
                    results['stats']['valid_rows'] += 1

    except Exception as e:
        results['valid'] = False
        results['errors'].append(f"Error reading file: {e}")
        return results

    # Set final validity
    if results['errors']:
        results['valid'] = False

    # Convert sets to counts for JSON serialization
    results['stats']['unique_contacts'] = len(results['stats']['unique_contacts'])
    results['stats']['unique_antennas'] = len(results['stats']['unique_antennas'])

    # Format date range
    if results['stats']['date_range'][0]:
        results['stats']['date_range'] = [
            str(results['stats']['date_range'][0]),
            str(results['stats']['date_range'][1])
        ]

    # Truncate error messages if too many
    if len(results['errors']) >= 10:
        total_errors = results['stats']['total_rows'] - results['stats']['valid_rows']
        results['errors'].append(f"... and {total_errors - 10} more errors")

    if verbose:
        print_validation_results(results)

    return results


def validate_antennas_csv(filepath, verbose=True):
    """
    Validate antennas CSV file format.

    Parameters
    ----------
    filepath : str
        Path to the antennas CSV file
    verbose : bool
        Print detailed output

    Returns
    -------
    dict
        Validation results
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'stats': {
            'total_antennas': 0,
            'valid_antennas': 0
        }
    }

    required_columns = {'antenna_id', 'latitude', 'longitude'}

    if not os.path.exists(filepath):
        results['valid'] = False
        results['errors'].append(f"File not found: {filepath}")
        return results

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])

            missing = required_columns - headers
            if missing:
                results['valid'] = False
                results['errors'].append(f"Missing required columns: {missing}")
                return results

            for row_num, row in enumerate(reader, start=2):
                results['stats']['total_antennas'] += 1
                row_valid = True

                # Validate antenna_id
                antenna_id = row.get('antenna_id', '')
                if not antenna_id:
                    row_valid = False
                    results['errors'].append(f"Row {row_num}: Missing antenna_id")

                # Validate coordinates
                try:
                    lat = float(row.get('latitude', ''))
                    lon = float(row.get('longitude', ''))

                    if not (-90 <= lat <= 90):
                        results['warnings'].append(
                            f"Row {row_num}: Latitude {lat} out of range [-90, 90]"
                        )
                    if not (-180 <= lon <= 180):
                        results['warnings'].append(
                            f"Row {row_num}: Longitude {lon} out of range [-180, 180]"
                        )
                except ValueError:
                    row_valid = False
                    if len(results['errors']) < 10:
                        results['errors'].append(
                            f"Row {row_num}: Invalid coordinates"
                        )

                if row_valid:
                    results['stats']['valid_antennas'] += 1

    except Exception as e:
        results['valid'] = False
        results['errors'].append(f"Error reading file: {e}")

    if results['errors']:
        results['valid'] = False

    if verbose:
        print_validation_results(results, "Antennas")

    return results


def print_validation_results(results, file_type="Records"):
    """Print formatted validation results."""
    print(f"\n{'=' * 50}")
    print(f"{file_type} Validation Results")
    print('=' * 50)

    status = "PASSED" if results['valid'] else "FAILED"
    print(f"\nStatus: {status}")

    if results['stats']:
        print("\nStatistics:")
        for key, value in results['stats'].items():
            print(f"  {key}: {value}")

    if results['warnings']:
        print(f"\nWarnings ({len(results['warnings'])}):")
        for warning in results['warnings'][:5]:
            print(f"  - {warning}")
        if len(results['warnings']) > 5:
            print(f"  ... and {len(results['warnings']) - 5} more")

    if results['errors']:
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  - {error}")

    print()


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python validate-data.py <records_csv> [antennas_csv]")
        print("\nValidates CSV files for Bandicoot compatibility.")
        sys.exit(1)

    records_path = sys.argv[1]
    antennas_path = sys.argv[2] if len(sys.argv) > 2 else None

    print("Bandicoot Data Validator")
    print("=" * 50)

    records_result = validate_records_csv(records_path)

    if antennas_path:
        antennas_result = validate_antennas_csv(antennas_path)
        all_valid = records_result['valid'] and antennas_result['valid']
    else:
        all_valid = records_result['valid']

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
