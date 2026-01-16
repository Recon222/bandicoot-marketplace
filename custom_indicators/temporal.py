"""
Temporal Pattern Analysis Indicators
====================================

Indicators for analyzing timing patterns, detecting anomalies,
and reconstructing timelines around key events.

Investigative Value
-------------------
- Establish routine behavior (deviations are significant)
- Detect coordination through activity bursts
- Identify gaps that may indicate incarceration, hospitalization, etc.
- Compare behavior before/after significant dates
"""

from bandicoot.helper.group import grouping
from bandicoot.helper.maths import summary_stats
from bandicoot.helper.tools import pairwise
from collections import Counter, defaultdict
from datetime import timedelta


@grouping
def hourly_activity_profile(records):
    """
    Create hour-by-hour activity profile.

    Investigative Value
    -------------------
    Establishes routine - deviations from pattern around key dates
    are significant for investigation.

    Returns
    -------
    dict
        hour (0-23) -> count of interactions
    """
    if len(records) == 0:
        return {h: 0 for h in range(24)}

    hours = Counter(r.datetime.hour for r in records)
    return {h: hours.get(h, 0) for h in range(24)}


@grouping
def communication_gaps(records, threshold_hours=24):
    """
    Detect unusual periods of silence.

    Investigative Value
    -------------------
    Gaps could indicate incarceration, hospitalization, travel,
    phone switching, or significant events.

    Parameters
    ----------
    threshold_hours : int
        Minimum gap duration to report (default 24 hours)

    Returns
    -------
    list of dict
        Each gap: {'start': datetime, 'end': datetime, 'duration_hours': float}
    """
    if len(records) < 2:
        return []

    sorted_records = sorted(records, key=lambda r: r.datetime)
    threshold_seconds = threshold_hours * 3600
    gaps = []

    for prev, curr in pairwise(sorted_records):
        delta = (curr.datetime - prev.datetime).total_seconds()
        if delta >= threshold_seconds:
            gaps.append({
                'start': prev.datetime,
                'end': curr.datetime,
                'duration_hours': delta / 3600
            })

    return gaps


@grouping
def activity_bursts(records, window_minutes=30, threshold_multiplier=3):
    """
    Identify periods of unusually high activity.

    Investigative Value
    -------------------
    Bursts around key times may indicate coordination, panic,
    or crisis response.

    Parameters
    ----------
    window_minutes : int
        Size of sliding window (default 30 minutes)
    threshold_multiplier : float
        Activity must exceed average by this factor (default 3x)

    Returns
    -------
    list of dict
        Each burst: {'start': datetime, 'end': datetime, 'count': int}
    """
    if len(records) < 2:
        return []

    sorted_records = sorted(records, key=lambda r: r.datetime)

    # Calculate average activity rate
    total_seconds = (sorted_records[-1].datetime - sorted_records[0].datetime).total_seconds()
    if total_seconds == 0:
        return []

    avg_rate = len(records) / (total_seconds / (window_minutes * 60))
    threshold = avg_rate * threshold_multiplier

    # Sliding window detection
    window_delta = timedelta(minutes=window_minutes)
    bursts = []
    i = 0

    while i < len(sorted_records):
        window_start = sorted_records[i].datetime
        window_end = window_start + window_delta

        # Count records in window
        window_records = [r for r in sorted_records[i:]
                         if r.datetime < window_end]
        count = len(window_records)

        if count >= threshold:
            bursts.append({
                'start': window_start,
                'end': window_end,
                'count': count,
                'contacts': list(set(r.correspondent_id for r in window_records))
            })
            # Skip to end of this burst
            i += count
        else:
            i += 1

    return bursts


@grouping
def contact_first_appearance(records):
    """
    Identify when each contact first appears in the record.

    Investigative Value
    -------------------
    New contacts shortly before an event may be significant.

    Returns
    -------
    dict
        correspondent_id -> first_contact_datetime
    """
    if len(records) == 0:
        return {}

    first_seen = {}
    for r in sorted(records, key=lambda r: r.datetime):
        if r.correspondent_id not in first_seen:
            first_seen[r.correspondent_id] = r.datetime

    return first_seen


@grouping
def contact_last_appearance(records):
    """
    Identify when each contact last appears in the record.

    Investigative Value
    -------------------
    Sudden cessation of contact may indicate fallout, threat, or victim.

    Returns
    -------
    dict
        correspondent_id -> last_contact_datetime
    """
    if len(records) == 0:
        return {}

    last_seen = {}
    for r in records:
        if r.correspondent_id not in last_seen or r.datetime > last_seen[r.correspondent_id]:
            last_seen[r.correspondent_id] = r.datetime

    return last_seen


@grouping
def daily_activity_counts(records):
    """
    Count of interactions per day.

    Investigative Value
    -------------------
    Identify unusually active or inactive days.

    Returns
    -------
    dict
        date -> count
    """
    if len(records) == 0:
        return {}

    return dict(Counter(r.datetime.date() for r in records))


@grouping
def inter_event_times(records):
    """
    Distribution of time between consecutive interactions.

    Investigative Value
    -------------------
    Unusual clustering or spacing of communications.

    Returns
    -------
    SummaryStats
        Statistics of inter-event times in seconds
    """
    if len(records) < 2:
        return summary_stats([])

    sorted_records = sorted(records, key=lambda r: r.datetime)
    deltas = [(b.datetime - a.datetime).total_seconds()
              for a, b in pairwise(sorted_records)]

    return summary_stats(deltas)


def activity_around_time(user, target_datetime, hours_before=24, hours_after=24):
    """
    Get activity summary around a specific time.

    NOT a @grouping indicator - specific point-in-time query.

    Investigative Value
    -------------------
    What was happening in the hours before/after a key event?

    Parameters
    ----------
    user : bandicoot.core.User
    target_datetime : datetime
    hours_before : int
    hours_after : int

    Returns
    -------
    dict
        'before': list of records, 'after': list of records,
        'contacts_before': Counter, 'contacts_after': Counter
    """
    before_start = target_datetime - timedelta(hours=hours_before)
    after_end = target_datetime + timedelta(hours=hours_after)

    before_records = [r for r in user.records
                      if before_start <= r.datetime < target_datetime]
    after_records = [r for r in user.records
                     if target_datetime <= r.datetime <= after_end]

    return {
        'before': before_records,
        'after': after_records,
        'contacts_before': Counter(r.correspondent_id for r in before_records),
        'contacts_after': Counter(r.correspondent_id for r in after_records),
        'count_before': len(before_records),
        'count_after': len(after_records)
    }


def first_contact_after_time(user, target_datetime):
    """
    Who did the subject contact immediately after a specific time?

    NOT a @grouping indicator - specific query.

    Investigative Value
    -------------------
    First person contacted after an event is often significant.

    Returns
    -------
    dict or None
        First record after target time with contact info
    """
    after_records = [r for r in user.records if r.datetime > target_datetime]

    if not after_records:
        return None

    first = min(after_records, key=lambda r: r.datetime)
    return {
        'correspondent_id': first.correspondent_id,
        'datetime': first.datetime,
        'interaction': first.interaction,
        'direction': first.direction,
        'delay_seconds': (first.datetime - target_datetime).total_seconds()
    }
