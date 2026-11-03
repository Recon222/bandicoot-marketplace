"""
Test script for validating refactored data-first indicators against real Bandicoot data.

This script tests:
1. Single-user indicators (location_at_specific_time, time_at_locations, etc.)
2. Multi-user indicators (group_locations_at_time, meeting_detection, synchronized_silence)
3. Render functions

DO NOT EDIT indicator code based on results - this is purely for documentation.
"""

import sys
import os
import json
from datetime import datetime

# Add the custom_indicators module to path
sys.path.insert(0, r'D:\Coding\Active Working Coding Projects\Bandicoot MCP\bandicoot_mcp\bandicoot-plugin')

import bandicoot as bc

# Import the custom indicators
from custom_indicators.location import (
    location_at_specific_time,
    time_at_locations,
    unusual_locations,
    location_timeline,
    frequent_locations_ranked
)
from custom_indicators.temporal import (
    activity_bursts,
    inter_event_times,
    activity_around_time,
    communication_gaps
)
from custom_indicators.colocation import (
    group_locations_at_time,
    meeting_detection,
    synchronized_silence,
    antenna_overlap
)
from custom_indicators.relationship import (
    relationship_strength,
    reciprocity_score
)
from custom_indicators.render import (
    render_evidence,
    render_evidence_compact
)

# Data paths
DATA_PATH = r'D:\Coding\Active Working Coding Projects\Bandicoot MCP\test-analysis\data'
ANTENNA_PATH = os.path.join(DATA_PATH, 'antennas.csv')

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def print_result(name, result, compact=True):
    print(f"\n--- {name} ---")
    if result is None:
        print("Result: None")
        return

    # Check for type field
    result_type = result.get('type') if isinstance(result, dict) else None
    print(f"Has 'type' field: {result_type is not None}")
    if result_type:
        print(f"Type value: {result_type}")

    # Check for subjective fields that should NOT be present
    if isinstance(result, dict):
        bad_fields = ['confidence', 'suspicion_score', 'likely', 'suspicious']
        found_bad = [f for f in bad_fields if f in str(result)]
        print(f"Contains subjective fields: {found_bad if found_bad else 'None (good)'}")

    # Print abbreviated JSON
    if compact:
        try:
            json_str = json.dumps(result, indent=2, default=str)
            if len(json_str) > 2000:
                print(f"Result (truncated - {len(json_str)} chars total):")
                print(json_str[:2000] + "\n...")
            else:
                print(f"Result:")
                print(json_str)
        except Exception as e:
            print(f"JSON serialization error: {e}")
            print(f"Raw result (first 1000 chars): {str(result)[:1000]}")

def load_user(user_id):
    """Load a user from the data directory."""
    return bc.read_csv(user_id, DATA_PATH + '/', ANTENNA_PATH, describe=False)

def main():
    print_section("DATASET OVERVIEW")

    # List available users
    user_files = [f.replace('.csv', '') for f in os.listdir(DATA_PATH)
                  if f.endswith('.csv') and not f.startswith('_') and f != 'antennas.csv']
    print(f"Available users: {len(user_files)}")
    print(f"Sample users: {user_files[:5]}")

    # Load primary test user
    print("\nLoading primary test user: 416-225-5506 (Marcus Chen)")
    user1 = load_user('416-225-5506')
    print(f"  Records: {len(user1.records)}")
    print(f"  Antennas loaded: {len(user1.antennas) if user1.antennas else 0}")

    # Get date range
    if user1.records:
        sorted_recs = sorted(user1.records, key=lambda r: r.datetime)
        print(f"  Date range: {sorted_recs[0].datetime} to {sorted_recs[-1].datetime}")
        # Sample record structure
        r = sorted_recs[0]
        print(f"  Sample record: datetime={r.datetime}, interaction={r.interaction}, direction={r.direction}")
        print(f"                 correspondent_id={r.correspondent_id}, antenna={r.position.antenna}")

    # Load second user for multi-user tests
    print("\nLoading second test user: 416-367-8573 (Daniel Ng)")
    user2 = load_user('416-367-8573')
    print(f"  Records: {len(user2.records)}")

    # Load third user for multi-user tests
    print("\nLoading third test user: 416-471-3287 (Lauren Martinez)")
    user3 = load_user('416-471-3287')
    print(f"  Records: {len(user3.records)}")

    # ========== PHASE 1: HIGH PRIORITY INDICATORS ==========
    print_section("PHASE 1: HIGH PRIORITY INDICATORS")

    # 1. location_at_specific_time
    print("\n>>> Testing location_at_specific_time")
    target_time = datetime(2012, 1, 15, 14, 30, 0)  # Mid-dataset time
    try:
        result = location_at_specific_time(user1, target_time, window_minutes=60)
        print_result("location_at_specific_time", result)
    except Exception as e:
        print(f"ERROR: {e}")

    # 2. group_locations_at_time (multi-user)
    print("\n>>> Testing group_locations_at_time")
    try:
        users = [user1, user2, user3]
        user_ids = ['416-225-5506', '416-367-8573', '416-471-3287']
        result = group_locations_at_time(users, user_ids, target_time, window_minutes=60)
        print_result("group_locations_at_time", result)
    except Exception as e:
        print(f"ERROR: {e}")

    # 3. meeting_detection (multi-user)
    print("\n>>> Testing meeting_detection")
    try:
        result = meeting_detection(user1, user2, colocation_window_minutes=60, gap_threshold_minutes=120)
        if result:
            print(f"Found {len(result)} potential co-location(s)")
            print_result("meeting_detection (first result)", result[0] if result else None)
        else:
            print("No co-locations found (may need larger window)")
            print("Result: []")
    except Exception as e:
        print(f"ERROR: {e}")

    # 4. synchronized_silence (multi-user)
    print("\n>>> Testing synchronized_silence")
    try:
        users = [user1, user2]
        user_ids = ['416-225-5506', '416-367-8573']
        result = synchronized_silence(users, user_ids, min_silence_minutes=120, min_overlap_minutes=60)
        if result:
            print(f"Found {len(result)} synchronized silence period(s)")
            print_result("synchronized_silence (first result)", result[0] if result else None)
        else:
            print("No synchronized silence found")
            print("Result: []")
    except Exception as e:
        print(f"ERROR: {e}")

    # ========== PHASE 2: MEDIUM PRIORITY INDICATORS ==========
    print_section("PHASE 2: MEDIUM PRIORITY INDICATORS")

    # 5. time_at_locations
    print("\n>>> Testing time_at_locations")
    try:
        result = time_at_locations(user1, minutes_per_hit=30)
        print_result("time_at_locations", result)
    except Exception as e:
        print(f"ERROR: {e}")

    # 6. unusual_locations
    print("\n>>> Testing unusual_locations")
    try:
        result = unusual_locations(user1, threshold_visits=2)
        print_result("unusual_locations", result)
    except Exception as e:
        print(f"ERROR: {e}")

    # 7. activity_bursts
    print("\n>>> Testing activity_bursts")
    try:
        result = activity_bursts(user1, window_minutes=30, threshold_multiplier=3)
        print_result("activity_bursts", result)
    except Exception as e:
        print(f"ERROR: {e}")

    # 8. inter_event_times
    print("\n>>> Testing inter_event_times")
    try:
        result = inter_event_times(user1)
        print_result("inter_event_times", result)
    except Exception as e:
        print(f"ERROR: {e}")

    # 9. activity_around_time
    print("\n>>> Testing activity_around_time")
    try:
        result = activity_around_time(user1, target_time, hours_before=24, hours_after=24)
        print_result("activity_around_time", result)
    except Exception as e:
        print(f"ERROR: {e}")

    # ========== PHASE 3: RELATIONSHIP INDICATOR ==========
    print_section("PHASE 3: RELATIONSHIP INDICATOR")

    # 10. relationship_strength
    print("\n>>> Testing relationship_strength")
    try:
        result = relationship_strength(user1)
        print_result("relationship_strength", result)
    except Exception as e:
        print(f"ERROR: {e}")

    # ========== PHASE 4: RENDERER TESTS ==========
    print_section("PHASE 4: RENDERER TESTS")

    # Test render_evidence on various result types
    test_cases = [
        ("location_at_specific_time", location_at_specific_time(user1, target_time, window_minutes=60)),
        ("time_at_locations", time_at_locations(user1)),
        ("unusual_locations", unusual_locations(user1)),
        ("activity_bursts", activity_bursts(user1)),
        ("inter_event_times", inter_event_times(user1)),
        ("activity_around_time", activity_around_time(user1, target_time)),
        ("relationship_strength", relationship_strength(user1)),
    ]

    for name, result in test_cases:
        print(f"\n--- Rendering: {name} ---")
        if result is None:
            print("  (No result to render)")
            continue
        try:
            # Full render
            lines = render_evidence(result)
            print("render_evidence output:")
            for line in lines[:10]:
                print(f"  {line}")
            if len(lines) > 10:
                print(f"  ... ({len(lines) - 10} more lines)")

            # Compact render
            compact = render_evidence_compact(result)
            print(f"render_evidence_compact: {compact}")
        except Exception as e:
            print(f"Render ERROR: {e}")

    # Test multi-user renders
    print("\n--- Rendering: group_locations_at_time ---")
    try:
        users = [user1, user2, user3]
        user_ids = ['Marcus Chen', 'Daniel Ng', 'Lauren Martinez']
        result = group_locations_at_time(users, user_ids, target_time, window_minutes=60)
        lines = render_evidence(result)
        print("render_evidence output:")
        for line in lines[:15]:
            print(f"  {line}")
        compact = render_evidence_compact(result)
        print(f"render_evidence_compact: {compact}")
    except Exception as e:
        print(f"Render ERROR: {e}")

    print_section("VALIDATION COMPLETE")
    print("Review the output above to verify:")
    print("1. All indicators have 'type' field")
    print("2. No subjective fields (confidence, suspicion_score)")
    print("3. Coordinates are normalized (lat/lon dict)")
    print("4. Events are serialized (ts, interaction, direction, etc.)")
    print("5. Renderers produce plain-English output")

if __name__ == '__main__':
    main()
