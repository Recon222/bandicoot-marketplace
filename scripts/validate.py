#!/usr/bin/env python
"""
Bandicoot Environment and Data Validator

Validates Bandicoot installation, dependencies, and CDR data files.

Usage:
    conda run -n bandicoot python validate.py [options]

Examples:
    # Check environment only
    python validate.py --env-only

    # Validate specific user data
    python validate.py --user sample_user_PRIMARY --data data/

    # Full validation with antennas file
    python validate.py --user ego --data demo/data/ --antennas demo/data/antennas.csv
"""

import argparse
import csv
import os
import sys
from datetime import datetime


def print_header(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print('=' * 60)


def print_subheader(title):
    """Print a subsection header."""
    print(f"\n--- {title} ---")


def ok(msg):
    """Print success message."""
    print(f"[OK] {msg}")


def fail(msg):
    """Print failure message."""
    print(f"[FAIL] {msg}")


def warn(msg):
    """Print warning message."""
    print(f"[WARN] {msg}")


def info(msg):
    """Print info message."""
    print(f"[INFO] {msg}")


def validate_environment():
    """Validate Bandicoot environment and dependencies."""
    print_header("Bandicoot Environment Validation")

    all_ok = True

    # Python environment
    print_subheader("Python Environment")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")

    # Bandicoot import
    print_subheader("Bandicoot Installation")
    try:
        import bandicoot as bc
        ok(f"Bandicoot {bc.__version__} imported successfully")
    except ImportError as e:
        fail(f"Cannot import bandicoot: {e}")
        print("\nTo install:")
        print("  pip install bandicoot")
        print("  OR")
        print("  conda install -c conda-forge bandicoot")
        return False

    # Submodules
    print_subheader("Bandicoot Modules")
    modules = ['core', 'individual', 'spatial', 'network', 'recharge', 'io', 'utils']
    for mod in modules:
        try:
            __import__(f'bandicoot.{mod}')
            ok(f"bandicoot.{mod}")
        except ImportError as e:
            fail(f"bandicoot.{mod}: {e}")
            all_ok = False

    # Optional dependencies
    print_subheader("Optional Dependencies")
    optional = [
        ('numpy', 'Extended statistics'),
        ('scipy', 'Advanced calculations'),
        ('networkx', 'Network analysis'),
    ]
    for mod, desc in optional:
        try:
            __import__(mod)
            ok(f"{mod} ({desc})")
        except ImportError:
            info(f"{mod} not installed ({desc}) - optional")

    return all_ok


def validate_csv_format(filepath):
    """Validate CSV file format and structure."""
    required = {'datetime', 'interaction', 'direction', 'correspondent_id'}
    optional = {'call_duration', 'antenna_id', 'latitude', 'longitude'}

    errors = []
    warnings = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])

            print(f"Columns found: {reader.fieldnames}")

            # Check required columns
            missing = required - headers
            if missing:
                fail(f"Missing required columns: {missing}")
                return False, errors
            else:
                ok("All required columns present")

            # Report optional columns
            present_optional = headers & optional
            if present_optional:
                ok(f"Optional columns present: {present_optional}")

            extra = headers - required - optional
            if extra:
                info(f"Extra columns (will be ignored): {extra}")

            # Validate sample rows
            print_subheader("Row Validation (first 100 rows)")
            row_count = 0

            for i, row in enumerate(reader):
                row_count += 1
                if i >= 100:
                    break

                # Check datetime format
                dt_str = row.get('datetime', '')
                try:
                    datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    if len(errors) < 5:
                        errors.append(f"Row {i+2}: Invalid datetime '{dt_str}'")

                # Check interaction type
                interaction = row.get('interaction', '')
                if interaction and interaction not in ('call', 'text'):
                    if len(errors) < 5:
                        errors.append(f"Row {i+2}: Invalid interaction '{interaction}' (expected 'call' or 'text')")

                # Check direction
                direction = row.get('direction', '')
                if direction not in ('in', 'out'):
                    if len(errors) < 5:
                        errors.append(f"Row {i+2}: Invalid direction '{direction}' (expected 'in' or 'out')")

            print(f"Rows checked: {min(row_count, 100)}")

            if errors:
                fail("Format errors found:")
                for err in errors:
                    print(f"  - {err}")
                if len(errors) >= 5:
                    print("  ... (showing first 5 errors)")

                print("\nExpected formats:")
                print("  datetime: YYYY-MM-DD HH:MM:SS (e.g., 2014-03-02 07:13:30)")
                print("  interaction: 'call' or 'text'")
                print("  direction: 'in' or 'out'")
                return False, errors
            else:
                ok("All sample rows validated successfully")
                return True, []

    except FileNotFoundError:
        fail(f"File not found: {filepath}")
        return False, [f"File not found: {filepath}"]
    except Exception as e:
        fail(f"Error reading file: {e}")
        return False, [str(e)]


def validate_antennas_file(filepath):
    """Validate antennas CSV file."""
    print_subheader("Antennas File Validation")
    print(f"Antennas file: {filepath}")

    if not os.path.exists(filepath):
        fail("Antennas file not found")
        return False

    ok("Antennas file exists")

    required = {'antenna_id', 'latitude', 'longitude'}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])

            missing = required - headers
            if missing:
                fail(f"Missing required columns: {missing}")
                print("Required columns: antenna_id, latitude, longitude")
                return False

            ok("Required columns present")

            # Validate coordinates
            ant_count = 0
            invalid_coords = 0

            for row in reader:
                ant_count += 1
                try:
                    lat = float(row['latitude'])
                    lon = float(row['longitude'])

                    # Basic coordinate range check
                    if not (-90 <= lat <= 90):
                        invalid_coords += 1
                    if not (-180 <= lon <= 180):
                        invalid_coords += 1
                except (ValueError, TypeError):
                    invalid_coords += 1

            print(f"Antennas found: {ant_count}")

            if invalid_coords > 0:
                warn(f"{invalid_coords} antenna(s) have invalid coordinates")
            else:
                ok("All coordinates valid")

            return True

    except Exception as e:
        fail(f"Error reading antennas file: {e}")
        return False


def validate_data(user_id, data_path, antennas_path=None):
    """Validate user data files and attempt Bandicoot load."""
    print_header("Bandicoot Data Validation")

    all_ok = True

    # Check records file
    print_subheader("Records File Check")
    records_file = os.path.join(data_path, f"{user_id}.csv")
    print(f"Looking for: {records_file}")

    if not os.path.exists(records_file):
        fail("Records file not found")

        # Help user find available files
        if os.path.exists(data_path):
            csvs = [f for f in os.listdir(data_path) if f.endswith('.csv')]
            if csvs:
                print(f"\nAvailable CSV files in {data_path}:")
                for f in csvs[:10]:
                    user_name = f[:-4]  # Remove .csv
                    print(f"  - {user_name}")
                if len(csvs) > 10:
                    print(f"  ... and {len(csvs) - 10} more")
        else:
            fail(f"Data directory not found: {data_path}")

        return False

    ok("Records file exists")

    # Validate CSV format
    print_subheader("CSV Format Validation")
    format_ok, errors = validate_csv_format(records_file)
    if not format_ok:
        all_ok = False

    # Validate antennas file if provided
    if antennas_path:
        ant_ok = validate_antennas_file(antennas_path)
        if not ant_ok:
            all_ok = False

    # Try actual Bandicoot load
    print_subheader("Bandicoot Load Test")
    try:
        import bandicoot as bc

        # Suppress bandicoot's own warnings during load for cleaner output
        user = bc.read_csv(
            user_id,
            data_path,
            antennas_path=antennas_path,
            describe=False
        )

        ok(f"Successfully loaded {len(user.records)} records")
        print(f"\n  User ID: {user_id}")
        print(f"  Records: {len(user.records)}")
        print(f"  Date range: {user.start_time} to {user.end_time}")
        print(f"  Has calls: {user.has_call}")
        print(f"  Has texts: {user.has_text}")
        print(f"  Has home: {user.has_home}")

        # Report ignored records
        if user.ignored_records:
            ignored_total = user.ignored_records.get('all', 0)
            if ignored_total > 0:
                warn(f"{ignored_total} records were ignored during load:")
                for key, count in user.ignored_records.items():
                    if key != 'all' and count > 0:
                        print(f"    - {key}: {count}")

    except ImportError:
        fail("Bandicoot not installed - cannot perform load test")
        all_ok = False
    except Exception as e:
        fail(f"Bandicoot load failed: {e}")
        all_ok = False

    return all_ok


def list_available_users(data_path):
    """List available user CSV files in the data directory."""
    print_subheader("Available Users")

    if not os.path.exists(data_path):
        fail(f"Data directory not found: {data_path}")
        return

    csvs = [f for f in os.listdir(data_path) if f.endswith('.csv')]

    if not csvs:
        info(f"No CSV files found in {data_path}")
        return

    print(f"Found {len(csvs)} CSV file(s) in {data_path}:\n")
    for f in sorted(csvs):
        user_name = f[:-4]  # Remove .csv
        filepath = os.path.join(data_path, f)
        size = os.path.getsize(filepath)
        size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
        print(f"  {user_name:<40} ({size_str})")


def main():
    parser = argparse.ArgumentParser(
        description='Validate Bandicoot environment and CDR data files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check environment only
  python validate.py --env-only

  # List available users in data directory
  python validate.py --list-users --data data/

  # Validate specific user
  python validate.py --user sample_user_PRIMARY --data data/

  # Full validation with antennas
  python validate.py --user ego --data demo/data/ --antennas demo/data/antennas.csv
        """
    )

    parser.add_argument(
        '--env-only',
        action='store_true',
        help='Only validate environment, skip data validation'
    )

    parser.add_argument(
        '--user',
        type=str,
        help='User ID to validate (filename without .csv extension)'
    )

    parser.add_argument(
        '--data',
        type=str,
        help='Path to directory containing CSV data files'
    )

    parser.add_argument(
        '--antennas',
        type=str,
        help='Path to antennas CSV file (optional)'
    )

    parser.add_argument(
        '--list-users',
        action='store_true',
        help='List available user CSV files in the data directory'
    )

    args = parser.parse_args()

    # Track overall success
    all_ok = True

    # Always validate environment first
    env_ok = validate_environment()
    if not env_ok:
        all_ok = False

    # If env-only, stop here
    if args.env_only:
        print_header("Validation Complete")
        if all_ok:
            print("\nEnvironment validation: PASSED")
        else:
            print("\nEnvironment validation: FAILED")
        return 0 if all_ok else 1

    # List users if requested
    if args.list_users and args.data:
        list_available_users(args.data)

    # Validate data if user and path provided
    if args.user and args.data:
        data_ok = validate_data(args.user, args.data, args.antennas)
        if not data_ok:
            all_ok = False
    elif args.user and not args.data:
        fail("--data path is required when --user is specified")
        all_ok = False
    elif not args.user and args.data and not args.list_users:
        info("No --user specified. Use --list-users to see available users.")

    # Final summary
    print_header("Validation Complete")

    if all_ok:
        print("\nAll validations PASSED")
        return 0
    else:
        print("\nSome validations FAILED - see above for details")
        return 1


if __name__ == '__main__':
    sys.exit(main())
