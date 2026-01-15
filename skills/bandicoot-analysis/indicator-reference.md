# Bandicoot Indicator Reference

Complete reference for all Bandicoot behavioral indicators, their meanings, and
typical value ranges.

## Individual Indicators

Communication behavior metrics computed from call and text records.

### active_days

**Description**: The number of days during which the user was active. A user is
considered active if they send/receive a text, make/receive a call, or have a
mobility point.

**Type**: Scalar (count)
**Range**: 0 to N (days in period)
**Module**: `bc.individual.active_days(user)`

**Interpretation**:
- Higher values indicate more consistent phone usage
- Low values may indicate data gaps or intermittent usage
- Compare to total days in observation period

---

### number_of_contacts

**Description**: The number of unique contacts the user interacted with.

**Type**: Scalar (count)
**Range**: 0 to N (number of unique correspondent_ids)
**Module**: `bc.individual.number_of_contacts(user)`
**Parameters**:
- `direction`: `'in'`, `'out'`, or `None` (all)
- `more`: Count only contacts with more than N interactions

**Interpretation**:
- Higher values indicate larger social network
- Can be filtered by direction to see social reach vs receptiveness
- `more=5` filters to "meaningful" relationships

---

### call_duration

**Description**: Distribution of call durations in seconds.

**Type**: Summary statistics (mean, std, min, max, etc.)
**Range**: 0 to N seconds
**Module**: `bc.individual.call_duration(user)`
**Parameters**:
- `direction`: `'in'`, `'out'`, or `None` (all)

**Interpretation**:
- Mean indicates typical conversation length
- High std indicates variable call patterns
- Short calls may indicate voicemail checks
- Long calls indicate deep conversations

**Typical values**:
- Short: 10-60 seconds
- Medium: 60-300 seconds (1-5 minutes)
- Long: 300+ seconds

---

### interevent_time

**Description**: Time in seconds between consecutive interactions.

**Type**: Summary statistics
**Range**: 0 to N seconds
**Module**: `bc.individual.interevent_time(user)`

**Interpretation**:
- Low mean = frequent communication
- High std = irregular communication patterns
- Very long interevent times may indicate data gaps

**Typical values**:
- Active user: mean < 3600 (1 hour)
- Moderate: mean 3600-86400 (1 hour to 1 day)
- Sparse: mean > 86400 (more than 1 day)

---

### percent_nocturnal

**Description**: Percentage of interactions occurring during nighttime hours.
Default night is 7pm-7am.

**Type**: Scalar (percentage 0-1)
**Range**: 0.0 to 1.0
**Module**: `bc.individual.percent_nocturnal(user)`

**Interpretation**:
- Higher values indicate nighttime communication preference
- 0.5 = equal day/night (considering 12-hour night)
- Cultural and occupational patterns affect this

**Configurable via**:
- `user.night_start` (default: datetime.time(19))
- `user.night_end` (default: datetime.time(7))

---

### percent_initiated_interactions

**Description**: Percentage of calls initiated by the user (outgoing calls).

**Type**: Scalar (percentage 0-1)
**Range**: 0.0 to 1.0
**Module**: `bc.individual.percent_initiated_interactions(user)`
**Note**: Applies to calls only, not texts

**Interpretation**:
- 0.5 = balanced (equal incoming/outgoing)
- > 0.5 = more proactive communicator
- < 0.5 = more reactive communicator

---

### percent_initiated_conversations

**Description**: Percentage of conversations initiated by the user. Each call and
text conversation counts as one interaction.

**Type**: Scalar (percentage 0-1)
**Range**: 0.0 to 1.0
**Module**: `bc.individual.percent_initiated_conversations(user)`

**Note**: A conversation is a series of texts within 1 hour without a call
interruption.

**Interpretation**: Similar to percent_initiated_interactions but includes text
conversations.

---

### response_rate_text

**Description**: The fraction of incoming text conversations where the user
responded with at least one outgoing text.

**Type**: Scalar (percentage 0-1)
**Range**: 0.0 to 1.0 (or None if no incoming conversations)
**Module**: `bc.individual.response_rate_text(user)`

**Interpretation**:
- 1.0 = responds to all incoming text conversations
- 0.0 = never responds
- None = no incoming text conversations

---

### response_delay_text

**Description**: Time in seconds between receiving a text and sending a response
within a conversation.

**Type**: Summary statistics
**Range**: 0 to 3600 seconds (max 1 hour, since conversations are bounded)
**Module**: `bc.individual.response_delay_text(user)`

**Interpretation**:
- Low mean = quick responder
- High std = inconsistent response times

**Typical values**:
- Quick: < 60 seconds
- Normal: 60-300 seconds
- Slow: 300-3600 seconds

---

### entropy_of_contacts

**Description**: Shannon entropy of contact distribution. Measures how evenly
interactions are distributed across contacts.

**Type**: Scalar
**Range**: 0 to log(N) where N = number of contacts
**Module**: `bc.individual.entropy_of_contacts(user)`
**Parameters**:
- `normalize`: If True, returns value between 0 and 1

**Interpretation**:
- 0 = all interactions with one contact
- Maximum = perfectly even distribution
- Normalized: 0 = concentrated, 1 = perfectly distributed

---

### balance_of_contacts

**Description**: For each contact, the ratio of outgoing to total interactions.
Returns distribution across all contacts.

**Type**: Summary statistics
**Range**: 0.0 to 1.0 per contact
**Module**: `bc.individual.balance_of_contacts(user)`
**Parameters**:
- `weighted`: If True, weight by number of interactions

**Interpretation**:
- Mean near 0.5 = balanced relationships
- Mean > 0.5 = user initiates more
- Mean < 0.5 = contacts initiate more

---

### interactions_per_contact

**Description**: Distribution of number of interactions with each contact.

**Type**: Summary statistics
**Range**: 1 to N
**Module**: `bc.individual.interactions_per_contact(user)`
**Parameters**:
- `direction`: `'in'`, `'out'`, or `None`

**Interpretation**:
- High mean = deep relationships
- High std = mix of close and distant contacts

---

### percent_pareto_interactions

**Description**: Percentage of contacts that account for 80% of all interactions.
Measures concentration of social activity.

**Type**: Scalar (percentage 0-1)
**Range**: 0.0 to 1.0
**Module**: `bc.individual.percent_pareto_interactions(user)`
**Parameters**:
- `percentage`: Target percentage (default 0.8)

**Interpretation**:
- Low value (e.g., 0.2) = concentrated on few contacts (80% from 20% of contacts)
- High value (e.g., 0.8) = distributed across many contacts
- Classic Pareto: ~0.2 means 20% of contacts drive 80% of interactions

---

### percent_pareto_durations

**Description**: Percentage of contacts that account for 80% of total call time.

**Type**: Scalar (percentage 0-1)
**Range**: 0.0 to 1.0 (or None if no calls)
**Module**: `bc.individual.percent_pareto_durations(user)`
**Parameters**:
- `percentage`: Target percentage (default 0.8)

**Interpretation**: Similar to percent_pareto_interactions but weighted by call
duration rather than count.

---

### number_of_interactions

**Description**: Total count of interactions (calls and/or texts).

**Type**: Scalar (count)
**Range**: 0 to N
**Module**: `bc.individual.number_of_interactions(user)`
**Parameters**:
- `direction`: `'in'`, `'out'`, or `None`

**Interpretation**: Raw measure of communication volume.

---

## Spatial Indicators

Mobility metrics computed from antenna/location data.

### number_of_antennas

**Description**: Count of unique antenna locations visited.

**Type**: Scalar (count)
**Range**: 0 to N
**Module**: `bc.spatial.number_of_antennas(user)`

**Interpretation**:
- Higher = more mobile user
- Low = stationary lifestyle

---

### entropy_of_antennas

**Description**: Shannon entropy of location distribution. Measures diversity of
places visited.

**Type**: Scalar
**Range**: 0 to log(N)
**Module**: `bc.spatial.entropy_of_antennas(user)`
**Parameters**:
- `normalize`: If True, returns 0-1 range

**Interpretation**:
- 0 = always at same location
- High = visits many places evenly
- Normalized 1 = perfectly even distribution

---

### percent_at_home

**Description**: Percentage of interactions occurring at the detected home
location.

**Type**: Scalar (percentage 0-1)
**Range**: 0.0 to 1.0 (or None if no home detected)
**Module**: `bc.spatial.percent_at_home(user)`

**Interpretation**:
- High (> 0.5) = home-based lifestyle
- Low = away from home often
- None = insufficient data to detect home

**Home detection**: Most frequent nighttime location (7pm-7am)

---

### radius_of_gyration

**Description**: The equivalent distance of mass from center of gravity for all
visited locations. Measures typical mobility range in kilometers.

**Type**: Scalar (kilometers)
**Range**: 0 to N km
**Module**: `bc.spatial.radius_of_gyration(user)`

**Interpretation**:
- 0 = no mobility
- 1-5 km = local mobility (within city)
- 5-50 km = regional mobility
- 50+ km = long-distance traveler

**Typical values**:
- Urban professional: 2-10 km
- Suburban commuter: 10-30 km
- Frequent traveler: 50+ km

---

### frequent_antennas

**Description**: Number of locations that account for a given percentage of time
spent.

**Type**: Scalar (count)
**Range**: 1 to number_of_antennas
**Module**: `bc.spatial.frequent_antennas(user)`
**Parameters**:
- `percentage`: Target percentage (default 0.8)

**Interpretation**:
- Low = concentrated in few places (home + work)
- High = distributed across many places
- Typical: 2-3 for 80% (home, work, 1-2 regular places)

---

### churn_rate

**Description**: Week-to-week change in location distribution. Computed as cosine
distance between consecutive weeks' location frequencies.

**Type**: Summary statistics (distribution of weekly churn)
**Range**: 0.0 to 1.0
**Module**: `bc.spatial.churn_rate(user)`

**Interpretation**:
- 0 = identical location pattern each week
- 1 = completely different locations each week
- Mean ~0.3-0.5 = typical variation

---

## Network Indicators

Social network metrics requiring `network=True` when loading.

### clustering_coefficient_unweighted

**Description**: Measures how many of the user's contacts also know each other.
Fraction of closed triplets in the unweighted, undirected ego network.

**Type**: Scalar
**Range**: 0.0 to 1.0
**Module**: `bc.network.clustering_coefficient_unweighted(user)`

**Interpretation**:
- 0 = star network (contacts don't know each other)
- 1 = complete subgraph (all contacts know each other)
- Typical real networks: 0.1-0.4

---

### clustering_coefficient_weighted

**Description**: Same as unweighted but triplets are weighted by interaction
volume.

**Type**: Scalar
**Range**: 0.0 to 1.0
**Module**: `bc.network.clustering_coefficient_weighted(user)`
**Parameters**:
- `interaction`: `'call'`, `'text'`, or None (combined)

**Interpretation**: Emphasizes strongly connected triplets over weakly connected
ones.

---

### assortativity_indicators

**Description**: Measures similarity between user and contacts across all
behavioral indicators. Returns variance of indicator differences.

**Type**: Dictionary of indicator: variance pairs
**Range**: 0 to infinity (lower = more similar)
**Module**: `bc.network.assortativity_indicators(user)`

**Interpretation**:
- Low variance = homophily (similar people connect)
- High variance = heterophily (different people connect)

---

### assortativity_attributes

**Description**: Measures homophily for nominal attributes. Returns percentage of
contacts sharing each attribute value.

**Type**: Dictionary of attribute: percentage pairs
**Range**: 0.0 to 1.0 per attribute
**Module**: `bc.network.assortativity_attributes(user)`

**Interpretation**:
- 1.0 = all contacts share the attribute value
- 0.0 = no contacts share the attribute value

---

## Recharge Indicators

Financial top-up metrics (requires recharges data).

### amount_recharges

**Description**: Distribution of recharge amounts.

**Type**: Summary statistics
**Range**: 0 to N (currency units)
**Module**: `bc.recharge.amount_recharges(user)`

---

### number_of_recharges

**Description**: Total count of recharges in period.

**Type**: Scalar (count)
**Range**: 0 to N
**Module**: `bc.recharge.number_of_recharges(user)`

---

### interevent_time_recharges

**Description**: Time in seconds between consecutive recharges.

**Type**: Summary statistics
**Range**: 0 to N seconds
**Module**: `bc.recharge.interevent_time_recharges(user)`

**Interpretation**:
- Low mean = frequent top-ups (possibly lower amounts)
- High mean = infrequent top-ups (possibly higher amounts)

---

### percent_pareto_recharges

**Description**: Percentage of recharges that account for 80% of total amount.

**Type**: Scalar (percentage 0-1)
**Range**: 0.0 to 1.0
**Module**: `bc.recharge.percent_pareto_recharges(user)`
**Parameters**:
- `percentage`: Target percentage (default 0.8)

---

### average_balance_recharges

**Description**: Estimated average daily balance assuming linear usage between
recharges and empty balance before each recharge.

**Type**: Scalar (currency units)
**Range**: 0 to N
**Module**: `bc.recharge.average_balance_recharges(user)`

**Note**: This function is NOT decorated with `@recharges_grouping` so does not
support groupby parameter.

---

## Reporting Variables

Metadata included in `bc.utils.all()` results under the `reporting` key:

| Variable | Description |
|----------|-------------|
| `version` | Bandicoot version |
| `groupby` | Aggregation method used |
| `split_week` | Whether weekday/weekend split applied |
| `split_day` | Whether day/night split applied |
| `start_time` | First record timestamp |
| `end_time` | Last record timestamp |
| `night_start` | Night period start time |
| `night_end` | Night period end time |
| `weekend` | Days considered weekend |
| `number_of_records` | Total records loaded |
| `number_of_antennas` | Unique antenna count |
| `number_of_recharges` | Total recharges |
| `bins` | Number of time bins (weeks/months) |
| `bins_with_data` | Bins containing records |
| `bins_without_data` | Empty bins |
| `has_call` | Whether call records present |
| `has_text` | Whether text records present |
| `has_home` | Whether home detected |
| `has_recharges` | Whether recharges loaded |
| `has_attributes` | Whether attributes loaded |
| `has_network` | Whether network loaded |
| `percent_records_missing_location` | Records without location |
| `antennas_missing_locations` | Antennas without coordinates |
| `percent_outofnetwork_calls` | Calls to/from non-network contacts |
| `percent_outofnetwork_texts` | Texts to/from non-network contacts |
| `percent_outofnetwork_contacts` | Contacts not in network |
| `percent_outofnetwork_call_durations` | Call time with non-network |
| `ignored_records` | Dict of records filtered during load |
