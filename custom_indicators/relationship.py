"""
Relationship Analysis Indicators
================================

Indicators for quantifying and ranking relationships between subjects.

Investigative Value
-------------------
- Identify closest associates (potential witnesses, accomplices)
- Detect one-sided relationships (pursuit, harassment, hierarchy)
- Understand communication dynamics between specific pairs
"""

from bandicoot.helper.group import grouping
from bandicoot.helper.maths import summary_stats
from collections import Counter, defaultdict


@grouping
def relationship_strength(records):
    """
    Rank contacts by communication intensity.

    Combines frequency, total call duration, and interaction recency into
    a composite score.

    Investigative Value
    -------------------
    Quickly identify who the subject communicates with most - these are
    potential witnesses, accomplices, or persons of interest.

    Returns
    -------
    dict
        correspondent_id -> strength_score, sorted by score descending
    """
    if len(records) == 0:
        return {}

    contact_stats = defaultdict(lambda: {'count': 0, 'duration': 0, 'last': None})

    for r in records:
        cid = r.correspondent_id
        contact_stats[cid]['count'] += 1
        if r.call_duration:
            contact_stats[cid]['duration'] += r.call_duration
        if contact_stats[cid]['last'] is None or r.datetime > contact_stats[cid]['last']:
            contact_stats[cid]['last'] = r.datetime

    # Normalize and compute composite score
    max_count = max(s['count'] for s in contact_stats.values())
    max_duration = max(s['duration'] for s in contact_stats.values()) or 1

    scores = {}
    for cid, stats in contact_stats.items():
        # Weight: 50% frequency, 30% duration, 20% recency not implemented yet
        freq_score = stats['count'] / max_count
        dur_score = stats['duration'] / max_duration
        scores[cid] = (0.6 * freq_score) + (0.4 * dur_score)

    # Sort by score descending
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))


@grouping
def reciprocity_score(records):
    """
    Measure balance of in/out communication per contact.

    For each contact: min(in, out) / max(in, out)
    - 1.0 = perfectly balanced relationship
    - 0.0 = completely one-sided

    Investigative Value
    -------------------
    One-sided relationships may indicate pursuit, harassment, or
    hierarchical relationship (e.g., receiving orders).

    Returns
    -------
    dict
        correspondent_id -> reciprocity score (0.0 to 1.0)
    """
    if len(records) == 0:
        return {}

    contact_dirs = defaultdict(lambda: {'in': 0, 'out': 0})

    for r in records:
        contact_dirs[r.correspondent_id][r.direction] += 1

    scores = {}
    for cid, dirs in contact_dirs.items():
        in_count = dirs['in']
        out_count = dirs['out']
        if in_count == 0 and out_count == 0:
            scores[cid] = None
        elif in_count == 0 or out_count == 0:
            scores[cid] = 0.0
        else:
            scores[cid] = min(in_count, out_count) / max(in_count, out_count)

    return scores


@grouping
def initiation_ratio(records):
    """
    Track who initiates contact in each relationship.

    Investigative Value
    -------------------
    The person who always initiates may be the pursuer, coordinator,
    or dependent party in the relationship.

    Returns
    -------
    dict
        correspondent_id -> ratio of subject-initiated interactions (0.0 to 1.0)
    """
    if len(records) == 0:
        return {}

    contact_counts = defaultdict(lambda: {'initiated': 0, 'total': 0})

    for r in records:
        contact_counts[r.correspondent_id]['total'] += 1
        if r.direction == 'out':
            contact_counts[r.correspondent_id]['initiated'] += 1

    return {
        cid: counts['initiated'] / counts['total'] if counts['total'] > 0 else None
        for cid, counts in contact_counts.items()
    }


@grouping(user_kwd=True)
def first_contact_of_day(records, user):
    """
    Identify who the subject contacts first each day.

    Investigative Value
    -------------------
    First contact of day often reveals closest personal relationships
    (partner, family) or urgent business contacts.

    Returns
    -------
    dict
        correspondent_id -> count of days they were first contact
    """
    if len(records) == 0:
        return {}

    # Group records by date
    by_date = defaultdict(list)
    for r in records:
        by_date[r.datetime.date()].append(r)

    first_contacts = []
    for date, day_records in by_date.items():
        # Sort by time, get first
        sorted_records = sorted(day_records, key=lambda r: r.datetime)
        if sorted_records:
            first_contacts.append(sorted_records[0].correspondent_id)

    return dict(Counter(first_contacts))


@grouping(user_kwd=True)
def last_contact_of_day(records, user):
    """
    Identify who the subject contacts last each day.

    Investigative Value
    -------------------
    Last contact of day often indicates close personal relationships
    or late-night coordination.

    Returns
    -------
    dict
        correspondent_id -> count of days they were last contact
    """
    if len(records) == 0:
        return {}

    # Group records by date
    by_date = defaultdict(list)
    for r in records:
        by_date[r.datetime.date()].append(r)

    last_contacts = []
    for date, day_records in by_date.items():
        # Sort by time, get last
        sorted_records = sorted(day_records, key=lambda r: r.datetime)
        if sorted_records:
            last_contacts.append(sorted_records[-1].correspondent_id)

    return dict(Counter(last_contacts))


@grouping
def contact_interaction_summary(records):
    """
    Detailed summary of interactions with each contact.

    Returns
    -------
    dict
        correspondent_id -> {
            'total': int,
            'calls_in': int, 'calls_out': int,
            'texts_in': int, 'texts_out': int,
            'total_call_duration': int,
            'first_contact': datetime,
            'last_contact': datetime
        }
    """
    if len(records) == 0:
        return {}

    summaries = defaultdict(lambda: {
        'total': 0,
        'calls_in': 0, 'calls_out': 0,
        'texts_in': 0, 'texts_out': 0,
        'total_call_duration': 0,
        'first_contact': None,
        'last_contact': None
    })

    for r in records:
        s = summaries[r.correspondent_id]
        s['total'] += 1

        key = f"{r.interaction}s_{r.direction}"
        s[key] += 1

        if r.call_duration:
            s['total_call_duration'] += r.call_duration

        if s['first_contact'] is None or r.datetime < s['first_contact']:
            s['first_contact'] = r.datetime
        if s['last_contact'] is None or r.datetime > s['last_contact']:
            s['last_contact'] = r.datetime

    return dict(summaries)
