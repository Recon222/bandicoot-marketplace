#!/usr/bin/env python
"""
Environment verification script for Bandicoot plugin.
Checks that Bandicoot is properly installed and functional.
"""
from __future__ import print_function
import sys


def check_bandicoot():
    """Verify Bandicoot installation and basic functionality."""
    print("=" * 50)
    print("Bandicoot Environment Check")
    print("=" * 50)

    # Check Python version
    print(f"\nPython version: {sys.version}")

    # Check Bandicoot import
    try:
        import bandicoot as bc
        print(f"Bandicoot version: {bc.__version__}")
    except ImportError as e:
        print(f"ERROR: Cannot import bandicoot: {e}")
        print("\nTo install bandicoot:")
        print("  pip install bandicoot")
        print("  OR")
        print("  conda install -c conda-forge bandicoot")
        return False

    # Check core modules
    modules = [
        ('bandicoot.core', 'Core data structures'),
        ('bandicoot.individual', 'Individual indicators'),
        ('bandicoot.spatial', 'Spatial indicators'),
        ('bandicoot.network', 'Network indicators'),
        ('bandicoot.recharge', 'Recharge indicators'),
        ('bandicoot.io', 'Input/Output functions'),
        ('bandicoot.utils', 'Utility functions'),
    ]

    print("\nModule availability:")
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"  [OK] {module_name}: {description}")
        except ImportError as e:
            print(f"  [FAIL] {module_name}: {e}")
            all_ok = False

    # Check optional dependencies
    print("\nOptional dependencies:")
    optional = [
        ('numpy', 'Required for tests'),
        ('scipy', 'Required for tests'),
        ('networkx', 'Required for tests'),
    ]

    for module_name, description in optional:
        try:
            __import__(module_name)
            print(f"  [OK] {module_name}: {description}")
        except ImportError:
            print(f"  [--] {module_name}: Not installed ({description})")

    # Test basic functionality
    print("\nFunctional tests:")
    try:
        user = bc.User()
        user.name = "test_user"
        print("  [OK] User object creation")
    except Exception as e:
        print(f"  [FAIL] User object creation: {e}")
        all_ok = False

    try:
        from bandicoot.core import Record, Position
        from datetime import datetime
        record = Record(
            interaction='call',
            direction='out',
            correspondent_id='contact1',
            datetime=datetime.now(),
            call_duration=60,
            position=Position(antenna='tower1')
        )
        print("  [OK] Record object creation")
    except Exception as e:
        print(f"  [FAIL] Record object creation: {e}")
        all_ok = False

    # Summary
    print("\n" + "=" * 50)
    if all_ok:
        print("STATUS: Environment ready for Bandicoot analysis")
        return True
    else:
        print("STATUS: Some issues detected - see above")
        return False


if __name__ == "__main__":
    success = check_bandicoot()
    sys.exit(0 if success else 1)
