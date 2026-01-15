# Bandicoot Benchmark Values

Reference values for interpreting Bandicoot indicators. These benchmarks are
derived from mobile phone research literature and typical datasets.

## Demo Data Reference (ego user)

The Bandicoot demo dataset provides a baseline for testing. These are expected
values when analyzing the `ego` user from `demo/data/`:

### Data Characteristics

| Metric | Value |
|--------|-------|
| Total records | 314 |
| Date range | ~8 weeks |
| Unique contacts | 7 |
| Unique antennas | 27 |

### Expected Indicator Values (groupby='week')

| Indicator | Expected Value |
|-----------|----------------|
| active_days__allweek__allday__callandtext__mean | ~5.5 |
| number_of_contacts__allweek__allday__call__mean | ~5.14 |
| call_duration__allweek__allday__call__mean__mean | ~3776 seconds |
| radius_of_gyration__allweek__allday__mean | ~1.45 km |
| percent_nocturnal__allweek__allday__callandtext__mean | ~0.25-0.35 |

---

## General Population Benchmarks

Based on academic research on mobile phone usage patterns.

### Activity Indicators

| Indicator | Low | Typical | High | Reference |
|-----------|-----|---------|------|-----------|
| Active days per week | <3 | 4-6 | 7 | Most users active 5-6 days |
| Records per day | <5 | 5-20 | >30 | Varies by population |
| Unique contacts | <10 | 10-50 | >100 | Dunbar's number research |

### Communication Indicators

| Indicator | Low | Typical | High | Interpretation |
|-----------|-----|---------|------|----------------|
| Call duration (mean) | <30s | 60-180s | >300s | Voicemails vs conversations |
| Percent initiated | <30% | 40-60% | >70% | Reactive vs proactive |
| Response rate text | <50% | 60-80% | >90% | Engagement level |
| Response delay (mean) | <60s | 1-10 min | >30 min | Availability |

### Social Network Indicators

| Indicator | Low | Typical | High | Interpretation |
|-----------|-----|---------|------|----------------|
| Entropy of contacts | <1.0 | 1.5-2.5 | >3.0 | Concentrated vs distributed |
| Entropy (normalized) | <0.3 | 0.4-0.7 | >0.8 | Relative distribution |
| Pareto interactions | <15% | 15-30% | >40% | Classic 80/20 = ~20% |
| Interactions per contact | <5 | 10-50 | >100 | Relationship depth |

### Temporal Indicators

| Indicator | Low | Typical | High | Interpretation |
|-----------|-----|---------|------|----------------|
| Percent nocturnal | <15% | 20-40% | >50% | Day vs night person |
| Interevent time (mean) | <1hr | 2-8 hrs | >24 hrs | Frequent vs sparse user |

---

## Spatial Benchmarks

### Mobility Patterns

| Population Type | Radius of Gyration | Percent at Home | Typical Pattern |
|-----------------|-------------------|-----------------|-----------------|
| Student | 2-10 km | 40-60% | Local, regular |
| Urban professional | 5-20 km | 30-50% | Commute pattern |
| Suburban commuter | 15-40 km | 25-40% | Longer commute |
| Remote worker | 2-5 km | 60-80% | Home-based |
| Frequent traveler | 50-200 km | <25% | High mobility |
| Retired | 1-5 km | 50-70% | Local, stable |

### Location Diversity

| Indicator | Low | Typical | High |
|-----------|-----|---------|------|
| Number of antennas | <5 | 10-30 | >50 |
| Entropy of antennas | <1.0 | 1.5-3.0 | >3.5 |
| Frequent antennas (80%) | 1-2 | 2-4 | >5 |
| Churn rate | <0.2 | 0.2-0.5 | >0.6 |

---

## Network Analysis Benchmarks

### Clustering Coefficients

| Network Type | Unweighted CC | Interpretation |
|--------------|---------------|----------------|
| Star network | 0 | Contacts don't know each other |
| Family/close friends | 0.3-0.6 | Interconnected small group |
| Professional | 0.05-0.2 | Sparser connections |
| Typical social | 0.1-0.4 | Real social networks |
| Complete graph | 1.0 | Everyone knows everyone |

### Assortativity

| Value Range | Interpretation |
|-------------|----------------|
| Strong positive (>0.3) | Homophily - similar people connect |
| Weak positive (0.1-0.3) | Mild preference for similar |
| Near zero (-0.1 to 0.1) | Random mixing |
| Negative (<-0.1) | Heterophily - different people connect |

---

## Research-Based Benchmarks

### From Academic Literature

**Gonzalez et al. (2008)** - Nature paper on human mobility:
- Average radius of gyration: ~6 km (but highly variable)
- Most people visit <10 locations regularly
- Strong regularity in daily patterns

**Dunbar (1992)** - Social brain hypothesis:
- Active contacts: 5-15 "inner circle"
- Extended network: 100-200 people
- Typical maintenance capacity: ~150 contacts

**Song et al. (2010)** - Predictability of human mobility:
- Location entropy typically 2-4 bits
- 93% of human movements predictable
- Most time spent in top 2-3 locations

### Seasonal Variations

| Season | Expected Changes |
|--------|------------------|
| Summer | Higher radius of gyration, lower percent at home |
| Winter | Lower mobility, more home time |
| Holidays | Irregular patterns, higher churn |
| Weekends | Different location patterns |

---

## Data Quality Thresholds

### Minimum Data Requirements

| Analysis Type | Minimum Records | Minimum Period |
|--------------|-----------------|----------------|
| Basic individual | 50 | 1 week |
| Reliable individual | 200 | 4 weeks |
| Spatial analysis | 100 with location | 2 weeks |
| Network analysis | Correspondent data | - |
| Temporal patterns | 100 | 4 weeks |

### Quality Warnings

| Metric | Concern Threshold | Issue |
|--------|-------------------|-------|
| Records missing location | >50% | Spatial indicators unreliable |
| Ignored records | >10% | Data format issues |
| Active days | <50% of period | Incomplete data |
| Contacts | <3 | Insufficient social data |

---

## Comparison Guidelines

### Within-Population Comparison

When comparing users:
1. Ensure same observation period
2. Use same groupby settings
3. Account for data quality differences
4. Consider population demographics

### Cross-Population Comparison

Be cautious when comparing across:
- Different countries (cultural norms)
- Different age groups (usage patterns)
- Different time periods (technology changes)
- Different socioeconomic groups

### Longitudinal Comparison

When comparing same user over time:
- Account for seasonal effects
- Consider life changes (job, move, etc.)
- Check for data collection changes
- Use same analysis parameters
