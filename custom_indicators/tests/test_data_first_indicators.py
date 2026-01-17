"""
Tests for data-first indicator return structures.

Validates:
1. No subjective fields (confidence, suspicion_score)
2. Required fields present
3. Coordinates normalized to {"lat": float, "lon": float}
4. Records serialized to Event format
"""

import pytest
from datetime import datetime, timedelta
from collections import namedtuple
from unittest.mock import MagicMock


# ==============================================================================
# Mock Objects for Testing
# ==============================================================================

class MockPosition:
    """Mock Bandicoot Position object."""
    def __init__(self, antenna=None):
        self.antenna = antenna


class MockRecord:
    """Mock Bandicoot Record object."""
    def __init__(self, dt, interaction='call', direction='out',
                 correspondent_id='contact1', call_duration=60, antenna=None):
        self.datetime = dt
        self.interaction = interaction
        self.direction = direction
        self.correspondent_id = correspondent_id
        self.call_duration = call_duration
        self.position = MockPosition(antenna)


class MockUser:
    """Mock Bandicoot User object."""
    def __init__(self, name='test_user', records=None, antennas=None):
        self.name = name
        self.records = records or []
        self.antennas = antennas or {}


# ==============================================================================
# Validation Helpers
# ==============================================================================

FORBIDDEN_FIELDS = ['confidence', 'suspicion_score', 'suspicion', 'likely', 'probably']


def assert_no_subjective_fields(result, path=""):
    """Recursively check that no subjective fields exist."""
    if isinstance(result, dict):
        for key, value in result.items():
            current_path = f"{path}.{key}" if path else key
            assert key not in FORBIDDEN_FIELDS, f"Forbidden field found at {current_path}"
            assert_no_subjective_fields(value, current_path)
    elif isinstance(result, list):
        for i, item in enumerate(result):
            assert_no_subjective_fields(item, f"{path}[{i}]")


def assert_has_required_fields(result, required_fields):
    """Check that all required fields are present."""
    for field in required_fields:
        parts = field.split('.')
        current = result
        for part in parts:
            assert part in current, f"Missing required field: {field}"
            current = current[part]


def assert_valid_coord(coord):
    """Check coordinate is properly normalized."""
    if coord is not None:
        assert isinstance(coord, dict), f"Coord should be dict, got {type(coord)}"
        assert 'lat' in coord, "Coord missing 'lat'"
        assert 'lon' in coord, "Coord missing 'lon'"


def assert_valid_event(event):
    """Check event is properly serialized."""
    assert isinstance(event, dict), f"Event should be dict, got {type(event)}"
    expected_fields = ['ts', 'interaction', 'direction', 'correspondent_id',
                       'duration_sec', 'antenna_id']
    for field in expected_fields:
        assert field in event, f"Event missing field: {field}"


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def sample_user():
    """Create a sample user with records and antenna data."""
    base_time = datetime(2024, 1, 15, 14, 0, 0)
    records = [
        MockRecord(base_time - timedelta(minutes=10), antenna='tower1'),
        MockRecord(base_time - timedelta(minutes=5), antenna='tower1'),
        MockRecord(base_time + timedelta(minutes=3), antenna='tower2'),
        MockRecord(base_time + timedelta(minutes=15), antenna='tower2'),
    ]
    antennas = {
        'tower1': (43.65, -79.38),
        'tower2': (43.66, -79.39)
    }
    return MockUser(name='test_subject', records=records, antennas=antennas)


@pytest.fixture
def two_users_same_antenna():
    """Create two users who were at the same antenna."""
    base_time = datetime(2024, 1, 15, 14, 0, 0)

    user_a_records = [
        MockRecord(base_time - timedelta(hours=2), antenna='tower1'),
        MockRecord(base_time - timedelta(minutes=5), antenna='tower_shared'),
        MockRecord(base_time + timedelta(hours=2), antenna='tower1'),
    ]
    user_b_records = [
        MockRecord(base_time - timedelta(hours=2), antenna='tower2'),
        MockRecord(base_time + timedelta(minutes=3), antenna='tower_shared'),
        MockRecord(base_time + timedelta(hours=2), antenna='tower2'),
    ]

    antennas = {
        'tower1': (43.65, -79.38),
        'tower2': (43.66, -79.39),
        'tower_shared': (43.67, -79.40)
    }

    user_a = MockUser(name='user_a', records=user_a_records, antennas=antennas)
    user_b = MockUser(name='user_b', records=user_b_records, antennas=antennas)

    return user_a, user_b


@pytest.fixture
def users_with_silence():
    """Create users with synchronized silence periods."""
    # Both users have a silence period from hour 2 to hour 4
    records_a = [
        MockRecord(datetime(2024, 1, 15, 10, 0, 0), antenna='tower1'),
        # 2 hour gap
        MockRecord(datetime(2024, 1, 15, 12, 0, 0), antenna='tower1'),
    ]
    records_b = [
        MockRecord(datetime(2024, 1, 15, 10, 30, 0), antenna='tower2'),
        # 2 hour gap
        MockRecord(datetime(2024, 1, 15, 12, 30, 0), antenna='tower2'),
    ]

    antennas = {
        'tower1': (43.65, -79.38),
        'tower2': (43.66, -79.39)
    }

    user_a = MockUser(name='user_a', records=records_a, antennas=antennas)
    user_b = MockUser(name='user_b', records=records_b, antennas=antennas)

    return [user_a, user_b], ['user_a', 'user_b']


# ==============================================================================
# Phase 1 Tests: High Priority Refactors
# ==============================================================================

class TestLocationAtSpecificTime:
    """Tests for location_at_specific_time indicator."""

    def test_no_confidence_field(self, sample_user):
        """Verify location_at_specific_time returns no confidence field."""
        from custom_indicators.location import location_at_specific_time

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = location_at_specific_time(sample_user, target, window_minutes=30)

        assert result is not None
        assert_no_subjective_fields(result)

    def test_has_type_field(self, sample_user):
        """Verify type field is present for renderer dispatch."""
        from custom_indicators.location import location_at_specific_time

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = location_at_specific_time(sample_user, target)

        assert result['type'] == 'location_at_time'

    def test_has_support_fields(self, sample_user):
        """Verify support section with raw observables."""
        from custom_indicators.location import location_at_specific_time

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = location_at_specific_time(sample_user, target)

        assert 'support' in result
        assert 'closest_event_delta_sec' in result['support']
        assert 'events_in_window' in result['support']
        assert 'has_location' in result['support']

    def test_coordinates_normalized(self, sample_user):
        """Verify coordinates use {"lat": float, "lon": float} format."""
        from custom_indicators.location import location_at_specific_time

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = location_at_specific_time(sample_user, target)

        assert 'location' in result
        coord = result['location']['coord']
        assert_valid_coord(coord)

    def test_events_serialized(self, sample_user):
        """Verify events are serialized to Event format."""
        from custom_indicators.location import location_at_specific_time

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = location_at_specific_time(sample_user, target)

        assert 'events_in_window' in result
        for event in result['events_in_window']:
            assert_valid_event(event)

    def test_returns_none_when_no_records(self):
        """Verify returns None when no records in window."""
        from custom_indicators.location import location_at_specific_time

        user = MockUser(name='empty', records=[], antennas={})
        target = datetime(2024, 1, 15, 14, 0, 0)
        result = location_at_specific_time(user, target)

        assert result is None


class TestGroupLocationsAtTime:
    """Tests for group_locations_at_time indicator."""

    def test_no_confidence_field(self, two_users_same_antenna):
        """Verify group_locations_at_time returns no confidence field."""
        from custom_indicators.colocation import group_locations_at_time

        user_a, user_b = two_users_same_antenna
        target = datetime(2024, 1, 15, 14, 0, 0)

        result = group_locations_at_time(
            [user_a, user_b], ['user_a', 'user_b'], target
        )

        assert_no_subjective_fields(result)

    def test_no_activity_at_time_phrase(self, two_users_same_antenna):
        """Verify no activity_at_time phrase (replaced with structured event)."""
        from custom_indicators.colocation import group_locations_at_time

        user_a, user_b = two_users_same_antenna
        target = datetime(2024, 1, 15, 14, 0, 0)

        result = group_locations_at_time(
            [user_a, user_b], ['user_a', 'user_b'], target
        )

        for uid, data in result['users'].items():
            assert 'activity_at_time' not in data

    def test_has_type_field(self, two_users_same_antenna):
        """Verify type field is present."""
        from custom_indicators.colocation import group_locations_at_time

        user_a, user_b = two_users_same_antenna
        target = datetime(2024, 1, 15, 14, 0, 0)

        result = group_locations_at_time(
            [user_a, user_b], ['user_a', 'user_b'], target
        )

        assert result['type'] == 'group_locations_at_time'

    def test_has_colocation_summary(self, two_users_same_antenna):
        """Verify colocation_summary groups users by antenna."""
        from custom_indicators.colocation import group_locations_at_time

        user_a, user_b = two_users_same_antenna
        target = datetime(2024, 1, 15, 14, 0, 0)

        result = group_locations_at_time(
            [user_a, user_b], ['user_a', 'user_b'], target
        )

        assert 'colocation_summary' in result
        assert 'by_antenna' in result['colocation_summary']

        # Both users should be at tower_shared
        by_antenna = result['colocation_summary']['by_antenna']
        assert 'tower_shared' in by_antenna
        assert len(by_antenna['tower_shared']) == 2


class TestMeetingDetection:
    """Tests for meeting_detection (now colocation_with_context)."""

    def test_no_confidence_field(self, two_users_same_antenna):
        """Verify meeting_detection returns no confidence field."""
        from custom_indicators.colocation import meeting_detection

        user_a, user_b = two_users_same_antenna
        result = meeting_detection(user_a, user_b)

        assert_no_subjective_fields(result)

    def test_has_type_field(self, two_users_same_antenna):
        """Verify type field is present."""
        from custom_indicators.colocation import meeting_detection

        user_a, user_b = two_users_same_antenna
        result = meeting_detection(user_a, user_b)

        if result:  # May be empty if no overlaps
            assert result[0]['type'] == 'colocation_with_context'

    def test_has_activity_context(self, two_users_same_antenna):
        """Verify activity_context for both users."""
        from custom_indicators.colocation import meeting_detection

        user_a, user_b = two_users_same_antenna
        result = meeting_detection(user_a, user_b)

        if result:
            assert 'activity_context' in result[0]
            assert 'user_a' in result[0]['activity_context']
            assert 'user_b' in result[0]['activity_context']
            assert 'records_around_count' in result[0]['activity_context']['user_a']

    def test_has_parameters(self, two_users_same_antenna):
        """Verify parameters are exposed."""
        from custom_indicators.colocation import meeting_detection

        user_a, user_b = two_users_same_antenna
        result = meeting_detection(user_a, user_b,
                                   colocation_window_minutes=45,
                                   gap_threshold_minutes=90)

        if result:
            assert 'parameters' in result[0]
            assert result[0]['parameters']['colocation_window_minutes'] == 45
            assert result[0]['parameters']['gap_threshold_minutes'] == 90


class TestSynchronizedSilence:
    """Tests for synchronized_silence indicator."""

    def test_no_suspicion_score(self, users_with_silence):
        """Verify synchronized_silence returns no suspicion_score."""
        from custom_indicators.colocation import synchronized_silence

        users, user_ids = users_with_silence
        result = synchronized_silence(users, user_ids, min_silence_minutes=60)

        assert_no_subjective_fields(result)

    def test_has_type_field(self, users_with_silence):
        """Verify type field is present."""
        from custom_indicators.colocation import synchronized_silence

        users, user_ids = users_with_silence
        result = synchronized_silence(users, user_ids, min_silence_minutes=60)

        if result:
            assert result[0]['type'] == 'synchronized_silence'

    def test_has_silence_object(self, users_with_silence):
        """Verify silence object with ISO timestamps."""
        from custom_indicators.colocation import synchronized_silence

        users, user_ids = users_with_silence
        result = synchronized_silence(users, user_ids, min_silence_minutes=60)

        if result:
            assert 'silence' in result[0]
            assert 'start_ts' in result[0]['silence']
            assert 'end_ts' in result[0]['silence']
            assert 'duration_minutes' in result[0]['silence']
            # Check ISO format
            assert 'T' in result[0]['silence']['start_ts']

    def test_has_support_observables(self, users_with_silence):
        """Verify support contains raw observables."""
        from custom_indicators.colocation import synchronized_silence

        users, user_ids = users_with_silence
        result = synchronized_silence(users, user_ids, min_silence_minutes=60)

        if result:
            assert 'support' in result[0]
            support = result[0]['support']
            assert 'participant_count' in support
            assert 'total_users' in support
            assert 'participant_ratio' in support
            assert 'start_hour' in support
            assert 'is_daytime' in support

    def test_has_parameters(self, users_with_silence):
        """Verify parameters are exposed."""
        from custom_indicators.colocation import synchronized_silence

        users, user_ids = users_with_silence
        result = synchronized_silence(users, user_ids,
                                      min_silence_minutes=45,
                                      min_overlap_minutes=20)

        if result:
            assert 'parameters' in result[0]
            assert result[0]['parameters']['min_silence_minutes'] == 45
            assert result[0]['parameters']['min_overlap_minutes'] == 20

    def test_sorted_chronologically(self, users_with_silence):
        """Verify results sorted by start time, not suspicion."""
        from custom_indicators.colocation import synchronized_silence

        users, user_ids = users_with_silence
        result = synchronized_silence(users, user_ids, min_silence_minutes=30)

        if len(result) > 1:
            for i in range(1, len(result)):
                assert result[i]['silence']['start_ts'] >= result[i-1]['silence']['start_ts']

    def test_events_serialized(self, users_with_silence):
        """Verify preceding/following events are serialized."""
        from custom_indicators.colocation import synchronized_silence

        users, user_ids = users_with_silence
        result = synchronized_silence(users, user_ids, min_silence_minutes=60)

        if result:
            assert 'preceding_events' in result[0]
            assert 'following_events' in result[0]

            for uid in result[0]['users']:
                if uid in result[0]['preceding_events']:
                    event = result[0]['preceding_events'][uid]
                    assert_valid_event(event)


# ==============================================================================
# Test Utils
# ==============================================================================

class TestSerializeRecord:
    """Tests for serialize_record utility."""

    def test_serialize_record(self):
        """Test record serialization."""
        from custom_indicators.utils import serialize_record

        dt = datetime(2024, 1, 15, 14, 0, 0)
        record = MockRecord(dt, interaction='call', direction='out',
                           correspondent_id='contact1', call_duration=120,
                           antenna='tower1')

        result = serialize_record(record)

        assert result['ts'] == '2024-01-15T14:00:00'
        assert result['interaction'] == 'call'
        assert result['direction'] == 'out'
        assert result['correspondent_id'] == 'contact1'
        assert result['duration_sec'] == 120
        assert result['antenna_id'] == 'tower1'


class TestNormalizeCoordinates:
    """Tests for normalize_coordinates utility."""

    def test_normalize_tuple(self):
        """Test normalizing tuple coordinates."""
        from custom_indicators.utils import normalize_coordinates

        antennas = {'tower1': (43.65, -79.38)}
        result = normalize_coordinates('tower1', antennas)

        assert result == {'lat': 43.65, 'lon': -79.38}

    def test_normalize_list(self):
        """Test normalizing list coordinates."""
        from custom_indicators.utils import normalize_coordinates

        antennas = {'tower1': [43.65, -79.38]}
        result = normalize_coordinates('tower1', antennas)

        assert result == {'lat': 43.65, 'lon': -79.38}

    def test_normalize_dict_lat_lon(self):
        """Test normalizing dict with lat/lon keys."""
        from custom_indicators.utils import normalize_coordinates

        antennas = {'tower1': {'lat': 43.65, 'lon': -79.38}}
        result = normalize_coordinates('tower1', antennas)

        assert result == {'lat': 43.65, 'lon': -79.38}

    def test_normalize_dict_latitude_longitude(self):
        """Test normalizing dict with latitude/longitude keys."""
        from custom_indicators.utils import normalize_coordinates

        antennas = {'tower1': {'latitude': 43.65, 'longitude': -79.38}}
        result = normalize_coordinates('tower1', antennas)

        assert result == {'lat': 43.65, 'lon': -79.38}

    def test_missing_antenna(self):
        """Test handling missing antenna."""
        from custom_indicators.utils import normalize_coordinates

        antennas = {'tower1': (43.65, -79.38)}
        result = normalize_coordinates('tower_unknown', antennas)

        assert result is None

    def test_none_antennas_dict(self):
        """Test handling None antennas dict."""
        from custom_indicators.utils import normalize_coordinates

        result = normalize_coordinates('tower1', None)

        assert result is None


# ==============================================================================
# Phase 2 Tests: Medium Priority Refactors
# ==============================================================================

class TestTimeAtLocations:
    """Tests for time_at_locations indicator."""

    def test_has_type_field(self, sample_user):
        """Verify type field is present."""
        from custom_indicators.location import time_at_locations

        result = time_at_locations(sample_user)

        assert result['type'] == 'time_at_locations'

    def test_exposes_hit_count(self, sample_user):
        """Verify raw hit_count is exposed."""
        from custom_indicators.location import time_at_locations

        result = time_at_locations(sample_user)

        assert 'locations' in result
        for antenna_id, data in result['locations'].items():
            assert 'hit_count' in data
            assert isinstance(data['hit_count'], int)

    def test_exposes_assumption(self, sample_user):
        """Verify assumption_minutes_per_hit is exposed."""
        from custom_indicators.location import time_at_locations

        result = time_at_locations(sample_user, minutes_per_hit=15)

        for antenna_id, data in result['locations'].items():
            assert data['assumption_minutes_per_hit'] == 15

    def test_has_totals(self, sample_user):
        """Verify totals summary is present."""
        from custom_indicators.location import time_at_locations

        result = time_at_locations(sample_user)

        assert 'totals' in result
        assert 'total_records_with_location' in result['totals']
        assert 'unique_antennas' in result['totals']


class TestUnusualLocations:
    """Tests for unusual_locations indicator (now location_visit_histogram)."""

    def test_has_type_field(self, sample_user):
        """Verify type field is present."""
        from custom_indicators.location import unusual_locations

        result = unusual_locations(sample_user)

        assert result['type'] == 'location_visit_histogram'

    def test_returns_all_locations(self, sample_user):
        """Verify all_locations contains full histogram."""
        from custom_indicators.location import unusual_locations

        result = unusual_locations(sample_user)

        assert 'all_locations' in result
        # Should have entries for all antennas in sample_user
        assert len(result['all_locations']) > 0

    def test_exposes_parameters(self, sample_user):
        """Verify parameters are exposed."""
        from custom_indicators.location import unusual_locations

        result = unusual_locations(sample_user, threshold_visits=5)

        assert 'parameters' in result
        assert result['parameters']['threshold_visits'] == 5

    def test_has_filtered_list(self, sample_user):
        """Verify filtered_below_threshold list is present."""
        from custom_indicators.location import unusual_locations

        result = unusual_locations(sample_user)

        assert 'filtered_below_threshold' in result
        assert isinstance(result['filtered_below_threshold'], list)

    def test_timestamps_are_iso(self, sample_user):
        """Verify timestamps are ISO formatted."""
        from custom_indicators.location import unusual_locations

        result = unusual_locations(sample_user)

        for antenna_id, data in result['all_locations'].items():
            for ts in data['timestamps']:
                assert 'T' in ts  # ISO format includes T


class TestActivityBursts:
    """Tests for activity_bursts indicator."""

    def test_has_type_field(self, sample_user):
        """Verify type field is present."""
        from custom_indicators.temporal import activity_bursts

        result = activity_bursts(sample_user)

        assert result['type'] == 'activity_bursts'

    def test_exposes_computed_parameters(self, sample_user):
        """Verify computed avg_rate and threshold are exposed."""
        from custom_indicators.temporal import activity_bursts

        result = activity_bursts(sample_user)

        assert 'parameters' in result
        assert 'computed_avg_rate' in result['parameters']
        assert 'computed_threshold' in result['parameters']
        assert 'window_minutes' in result['parameters']
        assert 'threshold_multiplier' in result['parameters']

    def test_has_data_span(self, sample_user):
        """Verify data_span shows analysis range."""
        from custom_indicators.temporal import activity_bursts

        result = activity_bursts(sample_user)

        assert 'data_span' in result
        assert 'first_record' in result['data_span']
        assert 'last_record' in result['data_span']
        assert 'total_records' in result['data_span']

    def test_bursts_have_events(self):
        """Verify bursts include serialized events."""
        from custom_indicators.temporal import activity_bursts

        # Create user with many records in short period (guaranteed burst)
        base_time = datetime(2024, 1, 15, 14, 0, 0)
        records = [
            MockRecord(base_time + timedelta(minutes=i), antenna='tower1')
            for i in range(20)  # 20 records in 20 minutes
        ]
        user = MockUser(name='burst_user', records=records)

        result = activity_bursts(user, window_minutes=30, threshold_multiplier=1)

        if result['bursts']:
            burst = result['bursts'][0]
            assert 'events' in burst
            assert len(burst['events']) > 0
            assert_valid_event(burst['events'][0])


class TestInterEventTimes:
    """Tests for inter_event_times indicator."""

    def test_has_type_field(self, sample_user):
        """Verify type field is present."""
        from custom_indicators.temporal import inter_event_times

        result = inter_event_times(sample_user)

        assert result['type'] == 'inter_event_times'

    def test_returns_raw_deltas(self, sample_user):
        """Verify raw deltas_seconds list is returned."""
        from custom_indicators.temporal import inter_event_times

        result = inter_event_times(sample_user)

        assert 'deltas_seconds' in result
        assert isinstance(result['deltas_seconds'], list)

    def test_has_summary_stats(self, sample_user):
        """Verify summary statistics are present."""
        from custom_indicators.temporal import inter_event_times

        result = inter_event_times(sample_user)

        assert 'summary' in result
        assert 'mean' in result['summary']
        assert 'std' in result['summary']
        assert 'min' in result['summary']
        assert 'max' in result['summary']
        assert 'median' in result['summary']
        assert 'count' in result['summary']

    def test_handles_empty_records(self):
        """Verify handles user with < 2 records."""
        from custom_indicators.temporal import inter_event_times

        user = MockUser(name='empty', records=[])
        result = inter_event_times(user)

        assert result['deltas_seconds'] == []
        assert result['summary']['count'] == 0


class TestActivityAroundTime:
    """Tests for activity_around_time indicator."""

    def test_has_type_field(self, sample_user):
        """Verify type field is present."""
        from custom_indicators.temporal import activity_around_time

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = activity_around_time(sample_user, target)

        assert result['type'] == 'activity_around_time'

    def test_events_serialized(self, sample_user):
        """Verify events are serialized, not raw Record objects."""
        from custom_indicators.temporal import activity_around_time

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = activity_around_time(sample_user, target)

        # Check before events
        for event in result['before']['events']:
            assert_valid_event(event)

        # Check after events
        for event in result['after']['events']:
            assert_valid_event(event)

    def test_has_window_spec(self, sample_user):
        """Verify window specification is present."""
        from custom_indicators.temporal import activity_around_time

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = activity_around_time(sample_user, target,
                                       hours_before=12, hours_after=6)

        assert 'window' in result
        assert result['window']['before_hours'] == 12
        assert result['window']['after_hours'] == 6
        assert 'center_ts' in result['window']

    def test_has_unique_contacts_count(self, sample_user):
        """Verify unique_contacts count is present."""
        from custom_indicators.temporal import activity_around_time

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = activity_around_time(sample_user, target)

        assert 'unique_contacts' in result['before']
        assert 'unique_contacts' in result['after']

    def test_no_raw_record_objects(self, sample_user):
        """Verify no raw Record objects in output."""
        from custom_indicators.temporal import activity_around_time

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = activity_around_time(sample_user, target)

        # Old API returned raw records in 'before' and 'after' lists
        # New API should only have 'events' which are serialized
        assert 'events' in result['before']
        assert 'events' in result['after']

        # Verify no raw Record objects exist anywhere
        def check_no_records(obj, path=""):
            if hasattr(obj, 'datetime') and hasattr(obj, 'interaction'):
                raise AssertionError(f"Raw Record object found at {path}")
            if isinstance(obj, dict):
                for k, v in obj.items():
                    check_no_records(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_no_records(item, f"{path}[{i}]")

        check_no_records(result)


# ==============================================================================
# Phase 3 Tests: Documentation and Consistency
# ==============================================================================

class TestRelationshipStrength:
    """Tests for relationship_strength indicator."""

    def test_has_type_field(self, sample_user):
        """Verify type field is present."""
        from custom_indicators.relationship import relationship_strength

        result = relationship_strength(sample_user)

        assert result['type'] == 'relationship_strength'

    def test_exposes_raw_components(self, sample_user):
        """Verify raw count and duration are exposed."""
        from custom_indicators.relationship import relationship_strength

        result = relationship_strength(sample_user)

        for cid, data in result['contacts'].items():
            assert 'count' in data
            assert 'duration_sec' in data
            assert 'score_components' in data
            assert 'count_norm' in data['score_components']
            assert 'duration_norm' in data['score_components']

    def test_exposes_methodology(self, sample_user):
        """Verify methodology/weights are exposed."""
        from custom_indicators.relationship import relationship_strength

        result = relationship_strength(sample_user)

        assert 'methodology' in result
        assert 'count_weight' in result['methodology']
        assert 'duration_weight' in result['methodology']
        assert result['methodology']['count_weight'] == 0.6
        assert result['methodology']['duration_weight'] == 0.4

    def test_has_last_contact_ts(self, sample_user):
        """Verify last_contact_ts is ISO formatted."""
        from custom_indicators.relationship import relationship_strength

        result = relationship_strength(sample_user)

        for cid, data in result['contacts'].items():
            assert 'last_contact_ts' in data
            if data['last_contact_ts']:
                assert 'T' in data['last_contact_ts']  # ISO format

    def test_no_recency_claim_in_docstring(self):
        """Verify docstring doesn't claim recency is implemented."""
        from custom_indicators.relationship import relationship_strength

        docstring = relationship_strength.__doc__
        assert 'Does NOT include recency' in docstring or 'not implemented' in docstring.lower()


# ==============================================================================
# Phase 4 Tests: Renderer Layer
# ==============================================================================

class TestRenderEvidence:
    """Tests for render_evidence function."""

    def test_render_location_at_time(self, sample_user):
        """Test rendering location_at_time evidence."""
        from custom_indicators.location import location_at_specific_time
        from custom_indicators.render import render_evidence, render_evidence_compact

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = location_at_specific_time(sample_user, target)

        lines = render_evidence(result)
        assert len(lines) > 0
        assert all(isinstance(line, str) for line in lines)

        # Check no forbidden words
        forbidden = ['confidence', 'suspicious', 'likely', 'probably']
        for line in lines:
            for word in forbidden:
                assert word.lower() not in line.lower(), f"Found '{word}' in: {line}"

        # Test compact version
        compact = render_evidence_compact(result)
        assert isinstance(compact, str)

    def test_render_group_locations_at_time(self, two_users_same_antenna):
        """Test rendering group_locations_at_time evidence."""
        from custom_indicators.colocation import group_locations_at_time
        from custom_indicators.render import render_evidence

        user_a, user_b = two_users_same_antenna
        target = datetime(2024, 1, 15, 14, 0, 0)

        result = group_locations_at_time([user_a, user_b], ['user_a', 'user_b'], target)

        lines = render_evidence(result)
        assert len(lines) > 0

    def test_render_colocation_with_context(self, two_users_same_antenna):
        """Test rendering colocation_with_context evidence."""
        from custom_indicators.colocation import meeting_detection
        from custom_indicators.render import render_evidence

        user_a, user_b = two_users_same_antenna
        results = meeting_detection(user_a, user_b)

        if results:
            lines = render_evidence(results[0])
            assert len(lines) > 0

    def test_render_synchronized_silence(self, users_with_silence):
        """Test rendering synchronized_silence evidence."""
        from custom_indicators.colocation import synchronized_silence
        from custom_indicators.render import render_evidence

        users, user_ids = users_with_silence
        results = synchronized_silence(users, user_ids, min_silence_minutes=60)

        if results:
            lines = render_evidence(results[0])
            assert len(lines) > 0

            # Verify no subjective words
            forbidden = ['suspicious', 'suspicion', 'likely']
            for line in lines:
                for word in forbidden:
                    assert word.lower() not in line.lower()

    def test_render_activity_around_time(self, sample_user):
        """Test rendering activity_around_time evidence."""
        from custom_indicators.temporal import activity_around_time
        from custom_indicators.render import render_evidence

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = activity_around_time(sample_user, target)

        lines = render_evidence(result)
        assert len(lines) > 0

    def test_render_relationship_strength(self, sample_user):
        """Test rendering relationship_strength evidence."""
        from custom_indicators.relationship import relationship_strength
        from custom_indicators.render import render_evidence

        result = relationship_strength(sample_user)

        lines = render_evidence(result)
        assert len(lines) > 0

    def test_render_activity_bursts(self, sample_user):
        """Test rendering activity_bursts evidence."""
        from custom_indicators.temporal import activity_bursts
        from custom_indicators.render import render_evidence

        result = activity_bursts(sample_user)

        lines = render_evidence(result)
        assert len(lines) > 0

    def test_render_inter_event_times(self, sample_user):
        """Test rendering inter_event_times evidence."""
        from custom_indicators.temporal import inter_event_times
        from custom_indicators.render import render_evidence

        result = inter_event_times(sample_user)

        lines = render_evidence(result)
        assert len(lines) > 0

    def test_render_time_at_locations(self, sample_user):
        """Test rendering time_at_locations evidence."""
        from custom_indicators.location import time_at_locations
        from custom_indicators.render import render_evidence

        result = time_at_locations(sample_user)

        lines = render_evidence(result)
        assert len(lines) > 0

    def test_render_location_visit_histogram(self, sample_user):
        """Test rendering location_visit_histogram evidence."""
        from custom_indicators.location import unusual_locations
        from custom_indicators.render import render_evidence

        result = unusual_locations(sample_user)

        lines = render_evidence(result)
        assert len(lines) > 0

    def test_unknown_type_handled(self):
        """Test that unknown evidence types are handled gracefully."""
        from custom_indicators.render import render_evidence

        result = {"type": "unknown_type_xyz", "data": "test"}
        lines = render_evidence(result)

        assert len(lines) == 1
        assert "Unknown evidence type" in lines[0]


class TestRenderEvidenceCompact:
    """Tests for render_evidence_compact function."""

    def test_compact_returns_string(self, sample_user):
        """Test that compact renderer returns a string."""
        from custom_indicators.location import location_at_specific_time
        from custom_indicators.render import render_evidence_compact

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = location_at_specific_time(sample_user, target)

        compact = render_evidence_compact(result)
        assert isinstance(compact, str)
        assert len(compact) > 0

    def test_compact_single_line(self, sample_user):
        """Test that compact renderer returns a single line."""
        from custom_indicators.location import location_at_specific_time
        from custom_indicators.render import render_evidence_compact

        target = datetime(2024, 1, 15, 14, 0, 0)
        result = location_at_specific_time(sample_user, target)

        compact = render_evidence_compact(result)
        assert '\n' not in compact
