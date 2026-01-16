"""
Network Structure Analysis Indicators (Multi-User)
==================================================

Indicators for analyzing the collective network of subjects,
identifying central figures, and detecting communication patterns.

Investigative Value
-------------------
- Identify the hub/coordinator in a network
- Detect communication chains (information flow)
- Find subgroups and cliques
- Identify shared contacts across subjects
"""

from collections import Counter, defaultdict
from datetime import timedelta


def build_communication_matrix(users, user_ids):
    """
    Build a matrix of communication between all users.

    Parameters
    ----------
    users : list of bandicoot.core.User
    user_ids : list of str
        Identifiers (phone numbers) for each user in same order

    Returns
    -------
    dict
        {(from_id, to_id): count} for all communication pairs
    """
    matrix = defaultdict(int)

    for i, user in enumerate(users):
        user_id = user_ids[i]
        for r in user.records:
            if r.direction == 'out':
                matrix[(user_id, r.correspondent_id)] += 1
            else:
                matrix[(r.correspondent_id, user_id)] += 1

    return dict(matrix)


def degree_centrality(users, user_ids):
    """
    Calculate degree centrality (number of connections) for each user.

    Investigative Value
    -------------------
    Identify the most connected figure - potential leader, coordinator,
    or key witness.

    Parameters
    ----------
    users : list of bandicoot.core.User
    user_ids : list of str
        Identifiers for each user

    Returns
    -------
    dict
        user_id -> {'total_contacts': int, 'in_network_contacts': int,
                    'out_of_network_contacts': int}
    """
    user_id_set = set(user_ids)
    results = {}

    for i, user in enumerate(users):
        user_id = user_ids[i]
        contacts = set(r.correspondent_id for r in user.records)

        in_network = contacts & user_id_set
        out_network = contacts - user_id_set

        results[user_id] = {
            'total_contacts': len(contacts),
            'in_network_contacts': len(in_network),
            'out_of_network_contacts': len(out_network),
            'in_network_list': list(in_network),
            'out_of_network_list': list(out_network)
        }

    # Sort by total contacts descending
    return dict(sorted(results.items(),
                       key=lambda x: x[1]['total_contacts'],
                       reverse=True))


def communication_chains(users, user_ids, time_window_minutes=30):
    """
    Detect A -> B -> C communication patterns.

    Investigative Value
    -------------------
    Information flow and command structure - A contacts B, then B contacts C
    suggests passing information or coordinating.

    Parameters
    ----------
    users : list of bandicoot.core.User
    user_ids : list of str
    time_window_minutes : int
        Maximum time between A->B and B->C communications

    Returns
    -------
    list of dict
        Each chain: {'sequence': [A, B, C], 'times': [...], 'total_time': seconds}
    """
    window_seconds = time_window_minutes * 60

    # Build timeline of all outgoing communications
    all_comms = []
    for i, user in enumerate(users):
        user_id = user_ids[i]
        for r in user.records:
            if r.direction == 'out':
                all_comms.append({
                    'from': user_id,
                    'to': r.correspondent_id,
                    'time': r.datetime
                })

    # Sort by time
    all_comms.sort(key=lambda x: x['time'])

    # Find chains
    chains = []
    for i, comm_ab in enumerate(all_comms):
        # Look for B -> C within window
        for j in range(i + 1, len(all_comms)):
            comm_bc = all_comms[j]
            delta = (comm_bc['time'] - comm_ab['time']).total_seconds()

            if delta > window_seconds:
                break

            # Does B in AB match From in BC?
            if comm_ab['to'] == comm_bc['from']:
                # Found a chain A -> B -> C
                chains.append({
                    'sequence': [comm_ab['from'], comm_ab['to'], comm_bc['to']],
                    'times': [comm_ab['time'], comm_bc['time']],
                    'total_time_seconds': delta,
                    'a_to_b': comm_ab,
                    'b_to_c': comm_bc
                })

    return chains


def shared_contacts(users, user_ids, min_shared=2):
    """
    Find contacts that multiple subjects have in common.

    Investigative Value
    -------------------
    Common associates may be witnesses, coordinators, or co-conspirators.

    Parameters
    ----------
    users : list of bandicoot.core.User
    user_ids : list of str
    min_shared : int
        Minimum number of subjects sharing the contact to report

    Returns
    -------
    dict
        contact_id -> list of user_ids who communicate with them
    """
    # Build contact sets for each user
    contact_to_users = defaultdict(list)

    for i, user in enumerate(users):
        user_id = user_ids[i]
        contacts = set(r.correspondent_id for r in user.records)
        for contact in contacts:
            contact_to_users[contact].append(user_id)

    # Filter to shared contacts
    shared = {contact: user_list
              for contact, user_list in contact_to_users.items()
              if len(user_list) >= min_shared}

    # Sort by number of users sharing
    return dict(sorted(shared.items(),
                       key=lambda x: len(x[1]),
                       reverse=True))


def communication_volume_matrix(users, user_ids):
    """
    Build matrix of communication volume between all pairs.

    Investigative Value
    -------------------
    Understand relationship strengths across the entire network.

    Parameters
    ----------
    users : list of bandicoot.core.User
    user_ids : list of str

    Returns
    -------
    dict
        {(user_a, user_b): {'total': int, 'calls': int, 'texts': int, 'duration': int}}
    """
    matrix = defaultdict(lambda: {'total': 0, 'calls': 0, 'texts': 0, 'duration': 0})

    for i, user in enumerate(users):
        user_id = user_ids[i]
        for r in user.records:
            # Normalize direction so (A,B) and (B,A) are the same key
            pair = tuple(sorted([user_id, r.correspondent_id]))

            matrix[pair]['total'] += 1
            if r.interaction == 'call':
                matrix[pair]['calls'] += 1
                if r.call_duration:
                    matrix[pair]['duration'] += r.call_duration
            else:
                matrix[pair]['texts'] += 1

    # Convert to regular dict and sort by volume
    return dict(sorted(matrix.items(),
                       key=lambda x: x[1]['total'],
                       reverse=True))


def network_timeline(users, user_ids, time_bucket_hours=24):
    """
    Show how network communication evolves over time.

    Investigative Value
    -------------------
    See when communication patterns change - new connections forming,
    existing ones going quiet.

    Parameters
    ----------
    users : list of bandicoot.core.User
    user_ids : list of str
    time_bucket_hours : int
        Group communications into buckets of this size

    Returns
    -------
    list of dict
        Each bucket: {'start': datetime, 'end': datetime,
                      'active_pairs': list, 'total_comms': int}
    """
    # Collect all communications
    all_comms = []
    for i, user in enumerate(users):
        user_id = user_ids[i]
        for r in user.records:
            pair = tuple(sorted([user_id, r.correspondent_id]))
            all_comms.append({
                'time': r.datetime,
                'pair': pair
            })

    if not all_comms:
        return []

    all_comms.sort(key=lambda x: x['time'])

    # Bucket by time
    bucket_delta = timedelta(hours=time_bucket_hours)
    buckets = []
    current_start = all_comms[0]['time'].replace(hour=0, minute=0, second=0, microsecond=0)

    while current_start <= all_comms[-1]['time']:
        current_end = current_start + bucket_delta
        bucket_comms = [c for c in all_comms
                        if current_start <= c['time'] < current_end]

        if bucket_comms:
            active_pairs = list(set(c['pair'] for c in bucket_comms))
            buckets.append({
                'start': current_start,
                'end': current_end,
                'active_pairs': active_pairs,
                'unique_pair_count': len(active_pairs),
                'total_communications': len(bucket_comms)
            })

        current_start = current_end

    return buckets


def identify_bridges(users, user_ids):
    """
    Identify users who bridge otherwise separate groups.

    Investigative Value
    -------------------
    Bridges are key information brokers - they connect groups that
    wouldn't otherwise communicate.

    Parameters
    ----------
    users : list of bandicoot.core.User
    user_ids : list of str

    Returns
    -------
    list of dict
        Users who connect to contacts not shared by others
    """
    user_id_set = set(user_ids)

    # Build contact sets for each user (only in-network)
    user_contacts = {}
    for i, user in enumerate(users):
        user_id = user_ids[i]
        contacts = set(r.correspondent_id for r in user.records)
        # Only count in-network contacts for bridge analysis
        user_contacts[user_id] = contacts & user_id_set

    # Find exclusive connections (contacts only this user has)
    bridges = []
    for user_id, contacts in user_contacts.items():
        others_contacts = set()
        for other_id, other_contacts in user_contacts.items():
            if other_id != user_id:
                others_contacts |= other_contacts

        exclusive = contacts - others_contacts - {user_id}
        if exclusive:
            bridges.append({
                'user_id': user_id,
                'exclusive_contacts': list(exclusive),
                'exclusive_count': len(exclusive),
                'total_contacts': len(contacts)
            })

    # Sort by exclusive contact count
    bridges.sort(key=lambda x: x['exclusive_count'], reverse=True)
    return bridges
