"""
Additional targeted tests for data-first indicators.
Testing with a time that has actual activity to verify location_at_specific_time.
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, r'D:\Coding\Active Working Coding Projects\Bandicoot MCP\bandicoot_mcp\bandicoot-plugin')

import bandicoot as bc

from custom_indicators.location import location_at_specific_time
from custom_indicators.colocation import synchronized_silence, group_locations_at_time
from custom_indicators.render import render_evidence, render_evidence_compact

DATA_PATH = r'D:\Coding\Active Working Coding Projects\Bandicoot MCP\test-analysis\data'
ANTENNA_PATH = os.path.join(DATA_PATH, 'antennas.csv')

def load_user(user_id):
    return bc.read_csv(user_id, DATA_PATH + '/', ANTENNA_PATH, describe=False)

def main():
    print("=" * 60)
    print("ADDITIONAL TARGETED TESTS")
    print("=" * 60)

    # Load users
    user1 = load_user('416-225-5506')
    user2 = load_user('416-367-8573')
    user3 = load_user('416-471-3287')

    # Find a time with actual activity
    print("\n--- Finding active time for location_at_specific_time test ---")
    if user1.records:
        sorted_recs = sorted(user1.records, key=lambda r: r.datetime)
        # Use time of first record
        test_time = sorted_recs[0].datetime
        print(f"Using actual record time: {test_time}")

        result = location_at_specific_time(user1, test_time, window_minutes=60)
        print(f"Result type field: {result.get('type') if result else 'None'}")
        if result:
            print(f"Has location: {result.get('support', {}).get('has_location')}")
            print(f"Antenna: {result.get('location', {}).get('antenna_id')}")
            print(f"Coord: {result.get('location', {}).get('coord')}")
            print(f"Events in window: {result.get('support', {}).get('events_in_window')}")

            print("\n--- Render test for location_at_specific_time ---")
            lines = render_evidence(result)
            for line in lines:
                print(f"  {line}")
            print(f"Compact: {render_evidence_compact(result)}")

    # Test synchronized_silence with relaxed parameters
    print("\n--- Testing synchronized_silence with relaxed parameters ---")
    users = [user1, user2]
    user_ids = ['Marcus Chen', 'Daniel Ng']

    # Very relaxed: 2 hour minimum silence, 1 hour overlap
    result = synchronized_silence(users, user_ids, min_silence_minutes=180, min_overlap_minutes=60)
    print(f"With 180 min silence, 60 min overlap: {len(result)} results")

    if result:
        r = result[0]
        print(f"First result type: {r.get('type')}")
        print(f"Users: {r.get('users')}")
        print(f"Silence duration: {r.get('silence', {}).get('duration_minutes')} minutes")
        print(f"Has preceding_events: {'preceding_events' in r}")
        print(f"Has following_events: {'following_events' in r}")

        print("\n--- Render test for synchronized_silence ---")
        lines = render_evidence(r)
        for line in lines:
            print(f"  {line}")
        print(f"Compact: {render_evidence_compact(r)}")

    # Test group_locations_at_time with actual data time
    print("\n--- Testing group_locations_at_time with active time ---")
    test_time = datetime(2012, 1, 2, 0, 25, 0)  # Time of first record
    users = [user1, user2, user3]
    user_ids = ['Marcus Chen', 'Daniel Ng', 'Lauren Martinez']

    result = group_locations_at_time(users, user_ids, test_time, window_minutes=30)
    print(f"Result type: {result.get('type')}")

    for uid, data in result.get('users', {}).items():
        has_loc = data.get('support', {}).get('has_location')
        antenna = data.get('location', {}).get('antenna_id')
        print(f"  {uid}: has_location={has_loc}, antenna={antenna}")

    by_ant = result.get('colocation_summary', {}).get('by_antenna', {})
    if by_ant:
        print(f"Co-location by antenna: {by_ant}")
    else:
        print("No co-locations at this time")

    print("\n--- Render test for group_locations_at_time ---")
    lines = render_evidence(result)
    for line in lines:
        print(f"  {line}")
    print(f"Compact: {render_evidence_compact(result)}")

    print("\n" + "=" * 60)
    print("ADDITIONAL TESTS COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
