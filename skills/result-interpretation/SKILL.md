---
name: result-interpretation
description: |
  Use this skill when explaining or interpreting Bandicoot analysis results,
  understanding what behavioral indicators mean, or comparing values against
  typical benchmarks.

  <example>
  Context: User asks what an indicator means
  user: "What does radius of gyration mean?"
  assistant: "[Uses skill to explain the mobility indicator and typical values]"
  <commentary>
  User wants indicator explanation - provide meaning and context.
  </commentary>
  </example>

  <example>
  Context: User has analysis results and wants interpretation
  user: "My user has a clustering coefficient of 0.3, is that high?"
  assistant: "[Uses skill to interpret value against typical ranges]"
  <commentary>
  User needs help understanding if value is normal.
  </commentary>
  </example>

  <example>
  Context: User comparing two analyses
  user: "User A has 20 contacts but User B has 50. What does this mean?"
  assistant: "[Uses skill to interpret difference in social network size]"
  <commentary>
  Comparative interpretation of behavioral indicators.
  </commentary>
  </example>

allowed-tools: Read
---

# Bandicoot Result Interpretation Skill

You are an expert in interpreting mobile phone behavioral analysis results from
Bandicoot. Help users understand what indicators mean, what values are typical,
and what insights can be drawn from the results.

## Interpretation Framework

When interpreting Bandicoot results, consider:

1. **Context**: What type of user/population is being analyzed?
2. **Data Quality**: Are there enough records? Missing data?
3. **Comparison**: What are typical values for this indicator?
4. **Meaning**: What behavior does this indicate?
5. **Limitations**: What can't we conclude from this indicator?

## Indicator Interpretation Guide

### Individual Indicators

#### active_days

**What it measures**: Number of days with at least one call or text.

**Typical values**:
- Low (1-3 days/week): Occasional phone user
- Medium (4-5 days/week): Regular user
- High (6-7 days/week): Daily phone user

**Interpretation notes**:
- Affected by observation period length
- Low values may indicate data gaps rather than behavior
- Compare to total days in observation period

---

#### number_of_contacts

**What it measures**: Count of unique people communicated with.

**Typical values**:
- Small network (< 10): Close-knit social circle
- Medium network (10-50): Typical social network
- Large network (50+): Broad social connections

**Interpretation notes**:
- Social network research suggests most people actively maintain 5-15 close contacts
- Large networks may include professional contacts
- Direction filter (in/out) reveals social reach vs receptiveness

---

#### call_duration

**What it measures**: Length of phone calls in seconds.

**Typical values**:
- Short calls (< 60s): Quick check-ins, voicemails
- Medium calls (60-300s): Standard conversations
- Long calls (> 300s): Extended conversations

**Interpretation notes**:
- High std indicates variable call patterns
- Very short mean may indicate many missed/voicemail calls
- Cultural factors affect call duration norms

---

#### percent_nocturnal

**What it measures**: Fraction of activity during night (7pm-7am).

**Typical values**:
- Low (< 25%): Daytime communicator, typical work schedule
- Medium (25-50%): Mixed schedule
- High (> 50%): Night-owl, shift worker, or different timezone contacts

**Interpretation notes**:
- Night definition is configurable (default 7pm-7am)
- Cultural and occupational factors matter
- High values don't necessarily indicate problematic behavior

---

#### entropy_of_contacts

**What it measures**: How evenly interactions are distributed across contacts.

**Typical values**:
- Low entropy (< 1.0): Concentrated on few contacts
- Medium entropy (1.0-2.5): Moderate distribution
- High entropy (> 2.5): Evenly spread across many contacts

**Normalized (0-1)**:
- 0: All interactions with one person
- 0.5: Moderately distributed
- 1.0: Perfectly even distribution

**Interpretation notes**:
- Lower entropy often indicates close relationships
- Higher entropy may indicate professional use
- Normalize for comparison across users with different contact counts

---

#### percent_pareto_interactions

**What it measures**: Fraction of contacts accounting for 80% of interactions.

**Typical values**:
- Pareto-like (15-25%): Classic 80/20 distribution
- More concentrated (< 15%): Very few close contacts
- More distributed (> 40%): Broader, more even relationships

**Interpretation notes**:
- Most social networks show Pareto-like distributions
- Very low values suggest dependency on few contacts
- Professional networks tend toward more distribution

---

### Spatial Indicators

#### radius_of_gyration

**What it measures**: Typical travel distance from center of activity (km).

**Typical values**:
- Local (< 5 km): Neighborhood-level mobility
- Urban (5-20 km): City-level mobility
- Regional (20-50 km): Commuter-level mobility
- Long-distance (> 50 km): Frequent traveler

**Interpretation notes**:
- Strongly affected by lifestyle (student vs professional vs retired)
- Urban vs rural settings show different patterns
- Does not capture travel frequency, only range

---

#### percent_at_home

**What it measures**: Fraction of phone activity at detected home location.

**Typical values**:
- Low (< 30%): Away from home frequently
- Medium (30-50%): Balanced home/away
- High (> 50%): Home-based lifestyle

**Interpretation notes**:
- Home is detected from nighttime patterns
- Work-from-home trends increase this value
- None value means home couldn't be detected

---

#### churn_rate

**What it measures**: Week-to-week change in location patterns (0-1).

**Typical values**:
- Low (< 0.2): Very consistent routine
- Medium (0.2-0.5): Normal weekly variation
- High (> 0.5): Highly variable locations

**Interpretation notes**:
- Low values suggest stable routine
- High values may indicate travel or irregular schedule
- Seasonal patterns may affect this

---

### Network Indicators

#### clustering_coefficient

**What it measures**: How interconnected the user's contacts are.

**Typical values**:
- Low (< 0.1): Star network - contacts don't know each other
- Medium (0.1-0.4): Typical social network clustering
- High (> 0.4): Dense network - contacts are interconnected

**Interpretation notes**:
- Real social networks typically show 0.1-0.4
- Family networks tend toward higher clustering
- Professional networks may be lower

---

## Benchmark Reference Values

### Demo Data (ego user) Expected Values

These values serve as reference for the Bandicoot demo dataset:

| Indicator | Expected Value |
|-----------|----------------|
| active_days (mean) | ~5.5 |
| number_of_contacts call (mean) | ~5.14 |
| call_duration mean (mean) | ~3776 seconds |
| radius_of_gyration (mean) | ~1.45 km |
| percent_at_home | ~0.4-0.6 |

### General Population Benchmarks

Based on mobile phone research literature:

| Indicator | Low | Typical | High |
|-----------|-----|---------|------|
| Contacts | <10 | 10-50 | >100 |
| Active days/week | <3 | 4-6 | 7 |
| Radius of gyration | <5km | 5-20km | >50km |
| Percent nocturnal | <20% | 20-40% | >50% |
| Clustering coefficient | <0.1 | 0.1-0.4 | >0.5 |

## Interpretation Caveats

### Data Quality Considerations

1. **Sample size**: More records = more reliable indicators
2. **Missing data**: Check `percent_records_missing_location`
3. **Time period**: Longer observation more representative
4. **Population**: Compare within similar populations

### What Indicators Cannot Tell You

- **Causation**: Indicators show patterns, not causes
- **Content**: No information about conversation topics
- **Intent**: Can't determine why someone behaved a way
- **Prediction**: Past behavior may not predict future

### Ethical Considerations

When interpreting behavioral data:
- Avoid over-interpretation of individual values
- Consider cultural and demographic context
- Be careful with pathologizing normal variation
- Remember privacy implications of detailed analysis

## Example Interpretations

### Low Activity User

```
active_days: 2
number_of_contacts: 4
percent_nocturnal: 15%
```

Interpretation: This user has low phone activity - only active 2 days per week
with a small network of 4 contacts. The low nocturnal percentage suggests
daytime-only communication. This pattern could indicate:
- Older user with limited phone use
- Secondary phone device
- Privacy-conscious user
- Data collection issues

### High Mobility User

```
radius_of_gyration: 45 km
percent_at_home: 18%
churn_rate: 0.65
```

Interpretation: This user shows high mobility - traveling an average of 45km
from their center of activity, spending little time at home (18%), with highly
variable weekly patterns (churn 0.65). This pattern suggests:
- Frequent traveler or commuter
- Field work or sales role
- Multiple residences
- Unstable housing situation

### Concentrated Social Network

```
number_of_contacts: 8
entropy_of_contacts: 0.85 (normalized: 0.41)
percent_pareto_interactions: 0.12
```

Interpretation: Small network (8 contacts) with concentrated communication -
only 12% of contacts account for 80% of interactions. Low normalized entropy
(0.41) confirms uneven distribution. This suggests:
- Close relationships with few people
- Possibly family-oriented communication
- Less diverse social network
