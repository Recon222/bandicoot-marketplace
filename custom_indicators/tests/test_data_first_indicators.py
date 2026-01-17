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
