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

from collections import Counter, defaultdict


def relationship_strength(user):
    """
    Rank contacts by communication intensity.

    Combines normalized frequency and total call duration into a composite
    score. Does NOT include recency weighting.

    Score formula: (0.6 * normalized_count) + (0.4 * normalized_duration)
    - normalized_count: contact's interaction count / max count across all contacts
    - normalized_duration: contact's total call duration / max duration across all contacts

    Investigative Value
    -------------------
    Quickly identify who the subject communicates with most - these are
    potential witnesses, accomplices, or persons of interest.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        Data-first evidence with:
        - type: "relationship_strength"
        - user_id: user identifier
        - contacts: dict of correspondent_id -> {
            score: composite score,
            count: raw interaction count,
            duration_sec: total call duration,
            last_contact_ts: ISO timestamp of most recent contact,
            score_components: {count_norm, duration_norm}
          }
        - methodology: weights used for scoring
    """
    records = user.records
    if len(records) == 0:
        return {
            "type": "relationship_strength",
            "user_id": getattr(user, 'name', None),
            "contacts": {},
            "methodology": {
                "count_weight": 0.6,
                "duration_weight": 0.4,
                "recency_weight": 0.0,
                "note": "Recency not implemented"
            }
        }

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

    contacts = {}
    for cid, stats in contact_stats.items():
        count_norm = stats['count'] / max_count
        duration_norm = stats['duration'] / max_duration
        score = (0.6 * count_norm) + (0.4 * duration_norm)

        contacts[cid] = {
            "score": round(score, 4),
            "count": stats['count'],
            "duration_sec": stats['duration'],
            "last_contact_ts": stats['last'].isoformat() if stats['last'] else None,
            "score_components": {
                "count_norm": round(count_norm, 4),
                "duration_norm": round(duration_norm, 4)
            }
        }

    # Sort by score descending
    sorted_contacts = dict(sorted(contacts.items(), key=lambda x: x[1]['score'], reverse=True))

    return {
        "type": "relationship_strength",
        "user_id": getattr(user, 'name', None),
        "contacts": sorted_contacts,
        "methodology": {
            "count_weight": 0.6,
            "duration_weight": 0.4,
            "recency_weight": 0.0,
            "note": "Recency not implemented"
        }
    }


def reciprocity_score(user):
    """
    Measure balance of in/out communication per contact.

    For each contact: min(in, out) / max(in, out)
    - 1.0 = perfectly balanced relationship
    - 0.0 = completely one-sided

    Investigative Value
    -------------------
    One-sided relationships may indicate pursuit, harassment, or
    hierarchical relationship (e.g., receiving orders).

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> reciprocity score (0.0 to 1.0)
    """
    records = user.records
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


def initiation_ratio(user):
    """
    Track who initiates contact in each relationship.

    Investigative Value
    -------------------
    The person who always initiates may be the pursuer, coordinator,
    or dependent party in the relationship.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> ratio of subject-initiated interactions (0.0 to 1.0)
    """
    records = user.records
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


def first_contact_of_day(user):
    """
    Identify who the subject contacts first each day.

    Investigative Value
    -------------------
    First contact of day often reveals closest personal relationships
    (partner, family) or urgent business contacts.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> count of days they were first contact
    """
    records = user.records
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


def last_contact_of_day(user):
    """
    Identify who the subject contacts last each day.

    Investigative Value
    -------------------
    Last contact of day often indicates close personal relationships
    or late-night coordination.

    Parameters
    ----------
    user : bandicoot.core.User

    Returns
    -------
    dict
        correspondent_id -> count of days they were last contact
    """
    records = user.records
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


def contact_interaction_summary(user):
    """
    Detailed summary of interactions with each contact.

    Parameters
    ----------
    user : bandicoot.core.User

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
    records = user.records
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
