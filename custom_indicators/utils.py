"""
Shared Utilities for Investigation Indicators
==============================================

Common functions used across indicator modules including:
- ID mapping (phone numbers to names)
- Time window queries
- Record filtering
- Result formatting
"""

import csv
from datetime import datetime, timedelta


def load_id_mapping(mapping_path):
    """
    Load phone number to name mapping from CSV.

    Parameters
    ----------
    mapping_path : str
        Path to _ID_MAPPING.csv file

    Returns
    -------
    dict
        phone_number -> name mapping
    """
    mapping = {}
    with open(mapping_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row['phone_number']] = row['name']
    return mapping


def resolve_contact(phone_number, mapping):
    """
    Resolve a single phone number to name.

    Parameters
    ----------
    phone_number : str
    mapping : dict

    Returns
    -------
    str
        Name if found, otherwise original phone number
    """
    return mapping.get(phone_number, phone_number)


def resolve_contacts(results, mapping):
    """
    Replace phone numbers with names in results.

    Parameters
    ----------
    results : dict or list
        Results containing phone numbers as keys or values
    mapping : dict
        phone_number -> name mapping

    Returns
    -------
    dict or list
        Results with phone numbers replaced by names
    """
    if isinstance(results, dict):
        return {mapping.get(k, k): v for k, v in results.items()}
    elif isinstance(results, list):
        return [mapping.get(item, item) if isinstance(item, str) else item
                for item in results]
    return results


def records_in_window(user, start_datetime, end_datetime):
    """
    Get all records within a specific time window.

    Parameters
    ----------
    user : bandicoot.core.User
        User object with records
    start_datetime : datetime
        Start of time window
    end_datetime : datetime
        End of time window

    Returns
    -------
    list of Record
        Records within the time window
    """
    return [r for r in user.records
            if start_datetime <= r.datetime <= end_datetime]


def records_around_time(user, target_datetime, window_minutes=30):
    """
    Get records within a window around a specific time.

    Parameters
    ----------
    user : bandicoot.core.User
    target_datetime : datetime
    window_minutes : int
        Minutes before and after target time

    Returns
    -------
    list of Record
    """
    delta = timedelta(minutes=window_minutes)
    return records_in_window(user, target_datetime - delta, target_datetime + delta)


def contacts_in_window(user, start_datetime, end_datetime):
    """
    Get all contacts communicated with in a time window.

    Parameters
    ----------
    user : bandicoot.core.User
    start_datetime : datetime
    end_datetime : datetime

    Returns
    -------
    dict
        correspondent_id -> count of interactions
    """
    from collections import Counter
    records = records_in_window(user, start_datetime, end_datetime)
    return dict(Counter(r.correspondent_id for r in records))


def location_at_time(user, target_datetime, window_minutes=30):
    """
    Determine location at a specific time.

    Parameters
    ----------
    user : bandicoot.core.User
    target_datetime : datetime
    window_minutes : int
        Search window around target time

    Returns
    -------
    dict or None
        Location info: antenna_id, coordinates, record_datetime
    """
    records = records_around_time(user, target_datetime, window_minutes)

    if not records:
        return None

    # Find closest record to target time
    closest = min(records, key=lambda r: abs((r.datetime - target_datetime).total_seconds()))

    if closest.position.antenna is None:
        return None

    # Get coordinates if available
    coords = None
    if user.antennas and closest.position.antenna in user.antennas:
        coords = user.antennas[closest.position.antenna]

    return {
        'antenna_id': closest.position.antenna,
        'coordinates': coords,
        'record_datetime': closest.datetime,
        'delta_seconds': abs((closest.datetime - target_datetime).total_seconds())
    }


def filter_by_contact(records, correspondent_id):
    """
    Filter records to only those with a specific contact.

    Parameters
    ----------
    records : list of Record
    correspondent_id : str

    Returns
    -------
    list of Record
    """
    return [r for r in records if r.correspondent_id == correspondent_id]


def filter_by_direction(records, direction):
    """
    Filter records by direction (in/out).

    Parameters
    ----------
    records : list of Record
    direction : str
        'in' or 'out'

    Returns
    -------
    list of Record
    """
    return [r for r in records if r.direction == direction]


def filter_by_interaction(records, interaction):
    """
    Filter records by interaction type (call/text).

    Parameters
    ----------
    records : list of Record
    interaction : str
        'call' or 'text'

    Returns
    -------
    list of Record
    """
    return [r for r in records if r.interaction == interaction]


def parse_datetime(datetime_str, fmt='%Y-%m-%d %H:%M:%S'):
    """
    Parse datetime string to datetime object.

    Parameters
    ----------
    datetime_str : str
    fmt : str
        datetime format string

    Returns
    -------
    datetime
    """
    return datetime.strptime(datetime_str, fmt)


def format_duration(seconds):
    """
    Format seconds as human-readable duration.

    Parameters
    ----------
    seconds : float

    Returns
    -------
    str
        e.g., "2h 30m 15s" or "45m 30s" or "30s"
    """
    if seconds is None:
        return "N/A"

    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)
