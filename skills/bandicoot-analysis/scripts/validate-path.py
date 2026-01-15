#!/usr/bin/env python
"""
Security utility for validating file paths before Bandicoot operations.
Prevents directory traversal attacks and ensures paths are within allowed directories.
"""
from __future__ import print_function
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
    if not path:
        raise ValueError("Path cannot be empty")

    # Convert to absolute path and normalize
    abs_path = os.path.abspath(os.path.expanduser(path))

    # Handle Windows paths (UNC paths, drive letters)
    if sys.platform == 'win32':
        abs_path = os.path.normpath(abs_path)

        # Check for UNC path attempts (\\server\share)
        if abs_path.startswith('\\\\'):
            # Only allow UNC if explicitly in allowed directories
            if allowed_base_dirs:
                allowed_unc = any(
                    abs_path.startswith(os.path.normpath(d))
                    for d in allowed_base_dirs
                    if d.startswith('\\\\')
                )
                if not allowed_unc:
                    raise ValueError(f"UNC paths not allowed: {path}")
            else:
                raise ValueError(f"UNC paths not allowed by default: {path}")

    # Default allowed directory is current working directory
    if allowed_base_dirs is None:
        allowed_base_dirs = [os.getcwd()]

    # Normalize all allowed directories
    allowed_base_dirs = [
        os.path.abspath(os.path.expanduser(d))
        for d in allowed_base_dirs
    ]

    if sys.platform == 'win32':
        allowed_base_dirs = [os.path.normpath(d) for d in allowed_base_dirs]

    # Check path is within allowed directories
    is_allowed = False
    for allowed_dir in allowed_base_dirs:
        # Use os.path.commonpath for reliable path comparison
        try:
            common = os.path.commonpath([abs_path, allowed_dir])
            if common == allowed_dir:
                is_allowed = True
                break
        except ValueError:
            # Different drives on Windows
            continue

    if not is_allowed:
        raise ValueError(
            f"Path '{path}' is outside allowed directories.\n"
            f"Allowed: {allowed_base_dirs}"
        )

    # Check for suspicious patterns in original path
    suspicious_patterns = ['..', '~root']
    for pattern in suspicious_patterns:
        if pattern in path:
            # Verify the pattern doesn't resolve to something outside allowed
            if pattern == '..' and os.path.normpath(path) != abs_path:
                # .. was resolved - check final path is still allowed
                pass  # Already checked above

    return abs_path


def validate_csv_path(path, allowed_base_dirs=None):
    """
    Validate path and ensure it's a CSV file or directory containing CSVs.

    Parameters
    ----------
    path : str
        Path to validate
    allowed_base_dirs : list of str, optional
        Allowed base directories

    Returns
    -------
    str
        Validated absolute path

    Raises
    ------
    ValueError
        If validation fails
    """
    validated = validate_path(path, allowed_base_dirs)

    if os.path.isfile(validated):
        if not validated.lower().endswith('.csv'):
            raise ValueError(f"File is not a CSV: {validated}")

    return validated


def validate_output_path(path, allowed_base_dirs=None, must_exist=False):
    """
    Validate an output path for writing.

    Parameters
    ----------
    path : str
        Output path to validate
    allowed_base_dirs : list of str, optional
        Allowed base directories
    must_exist : bool
        If True, parent directory must exist

    Returns
    -------
    str
        Validated absolute path
    """
    validated = validate_path(path, allowed_base_dirs)

    parent_dir = os.path.dirname(validated)
    if must_exist and not os.path.exists(parent_dir):
        raise ValueError(f"Parent directory does not exist: {parent_dir}")

    return validated


def check_path_safety(path):
    """
    Perform safety checks on a path without raising exceptions.

    Parameters
    ----------
    path : str
        Path to check

    Returns
    -------
    dict
        Results with 'safe', 'warnings', 'absolute_path' keys
    """
    results = {
        'safe': True,
        'warnings': [],
        'absolute_path': None
    }

    if not path:
        results['safe'] = False
        results['warnings'].append("Empty path")
        return results

    try:
        abs_path = os.path.abspath(os.path.expanduser(path))
        results['absolute_path'] = abs_path
    except Exception as e:
        results['safe'] = False
        results['warnings'].append(f"Cannot resolve path: {e}")
        return results

    # Check for suspicious patterns
    if '..' in path:
        results['warnings'].append("Contains parent directory reference (..)")

    if path.startswith('~') and not path.startswith('~/'):
        results['warnings'].append("Contains tilde expansion to other user")

    if sys.platform == 'win32':
        if path.startswith('\\\\'):
            results['warnings'].append("UNC network path")
        if ':' in path[2:]:
            results['warnings'].append("Contains colon in path (possible alternate data stream)")

    # Check if path exists
    if os.path.exists(abs_path):
        if os.path.islink(abs_path):
            results['warnings'].append("Path is a symbolic link")
            real_path = os.path.realpath(abs_path)
            if real_path != abs_path:
                results['warnings'].append(f"Symlink resolves to: {real_path}")

    return results


def main():
    """Command-line interface for path validation."""
    if len(sys.argv) < 2:
        print("Usage: python validate-path.py <path> [allowed_base_dir...]")
        print("\nValidates a path for safe use with Bandicoot.")
        print("\nExamples:")
        print("  python validate-path.py ./data/user.csv")
        print("  python validate-path.py /data/records /data /home/user")
        sys.exit(1)

    test_path = sys.argv[1]
    allowed_dirs = sys.argv[2:] if len(sys.argv) > 2 else None

    print(f"Validating path: {test_path}")
    print(f"Allowed directories: {allowed_dirs or ['(current directory)']}")
    print()

    # Run safety check first
    safety = check_path_safety(test_path)
    if safety['warnings']:
        print("Warnings:")
        for warning in safety['warnings']:
            print(f"  - {warning}")
        print()

    # Attempt validation
    try:
        validated = validate_path(test_path, allowed_dirs)
        print(f"VALID: {validated}")
        sys.exit(0)
    except ValueError as e:
        print(f"INVALID: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
