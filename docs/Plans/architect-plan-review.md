# Architectural Review: Bandicoot Mapbox GL JS Visualization Plan

**Review Date:** 2026-01-16
**Reviewer:** Software Architecture Review
**Document Under Review:** `docs/Plans/mapbox-visualization-plan.md`
**Verdict:** CONDITIONAL APPROVAL with Critical Gaps

---

## Executive Summary

The proposed Mapbox GL JS visualization plan is ambitious and technically sound in its core architecture. The event-driven design with pub/sub messaging, centralized state management, and clean component separation demonstrates solid software engineering principles. However, the plan contains **critical missing features** that would significantly limit its usefulness for CDR analysis, and there are **architectural misalignments** with the existing Bandicoot plugin patterns that must be addressed before implementation.

### Critical Issues

| Issue | Severity | Impact |
|-------|----------|--------|
| No user/contact filtering capabilities | **CRITICAL** | Cannot isolate communication patterns by correspondent |
| No date/time picker UI for precise filtering | **HIGH** | Users cannot select specific time windows with precision |
| Violates "inline execution, no wrapper scripts" pattern | **HIGH** | Creates external JS application instead of inline tooling |
| No integration with existing plugin command structure | **HIGH** | Standalone application, not a plugin extension |
| GeoJSON data transformation pipeline undefined | **MEDIUM** | Unclear how Bandicoot data becomes visualization-ready |

---

## Critical Missing Implementations

### 1. User/Contact Filtering Capabilities (CRITICAL)

**Current State:** The plan provides time-based filtering and event type filtering (call/text, in/out) but completely omits the ability to filter by:
- Specific correspondent IDs (contacts)
- User selection in multi-user scenarios
- Contact groupings or communication frequency tiers

**Why This Is Critical:**

CDR analysis fundamentally revolves around understanding communication patterns with specific individuals. The ability to isolate and visualize interactions with particular contacts is essential for:
- Identifying key relationships
- Understanding communication frequency with specific correspondents
- Analyzing spatial patterns when communicating with particular contacts
- Investigating behavioral changes in specific relationships over time

**Required Addition:**

```javascript
// FilterEngine.js - Missing contact filtering
#state = {
  // ... existing state
  contacts: {
    selected: [],           // Array of correspondent_ids to show
    excluded: [],           // Array of correspondent_ids to hide
    frequencyThreshold: 0,  // Minimum interactions to show
    mode: 'all'            // 'all' | 'selected' | 'excluded' | 'top-n'
  }
};

// Events to add
// 'filter:contact:select' - Select specific contacts
// 'filter:contact:exclude' - Exclude specific contacts
// 'filter:contact:top' - Show top N contacts by frequency
```

**UI Component Required:**

A contact selector panel showing:
- List of all correspondents with interaction counts
- Multi-select capability
- Search/filter within contact list
- "Top N contacts" quick filter
- Contact grouping/tagging (future enhancement)

### 2. Date/Time Picker UI (HIGH)

**Current State:** The plan includes `datetime-local` inputs in the Range Selector component, but this is insufficient for CDR analysis workflows.

```html
<!-- Current plan - insufficient -->
<input type="datetime-local" class="range-selector__input" id="range-start">
```

**Why This Is a Gap:**

- Native `datetime-local` has poor cross-browser consistency
- No visual calendar for date selection
- Difficult to quickly select common ranges (last 7 days, this month, specific week)
- No timezone awareness display
- Cannot easily select partial days (e.g., "all evenings in March")

**Required Enhancement:**

```javascript
// components/DateTimePicker.js
export class DateTimePicker {
  // Features needed:
  // - Visual calendar with range selection
  // - Time picker with hour/minute precision
  // - Timezone selector
  // - Preset ranges: Today, Yesterday, Last 7 days, This week, This month, Custom
  // - Time-of-day filters: Morning (6-12), Afternoon (12-18), Evening (18-24), Night (0-6)
  // - Relative range input: "Last N days/weeks/months"
}
```

**UI Events to Add:**

| Event | Payload | Purpose |
|-------|---------|---------|
| `date:range:select` | `{ start, end, timezone }` | Precise date/time selection |
| `date:preset:select` | `{ preset: 'last7days' }` | Quick range selection |
| `date:timeofday:filter` | `{ periods: ['evening', 'night'] }` | Filter by time of day |

---

## Architectural Concerns

### 3. Violation of "Inline Execution" Pattern (HIGH)

**Existing Pattern (from CLAUDE.md):**

```bash
# CORRECT - inline execution
conda run -n bandicoot python -c "
import bandicoot as bc
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')
print(bc.individual.number_of_contacts(user))
"

# INCORRECT - do not create script files for Bandicoot calls
```

**Plan Violation:**

The proposed visualization creates a complete standalone web application with:
- 50+ JavaScript files in a `bandicoot-visualizer/` directory
- Permanent HTML/CSS/JS assets that must be served
- A browser-based application requiring a web server

**Architectural Mismatch:**

The existing plugin architecture operates on the principle that each command execution is independent with no state persistence. The visualization plan contradicts this by creating:
1. A stateful browser application
2. Persistent asset files
3. A required web server for operation

**Proposed Mitigation:**

Three potential approaches to align with plugin architecture:

**Option A: Inline HTML Generation (Recommended)**
```bash
# Generate self-contained HTML with embedded JS/CSS and data
conda run -n bandicoot python -c "
import bandicoot as bc
user = bc.read_csv('ego', 'demo/data/', 'demo/data/antennas.csv')
# Generate GeoJSON
geojson = generate_location_geojson(user)
# Generate self-contained HTML with embedded data
html = generate_visualization_html(geojson, user.name)
with open('visualization.html', 'w') as f:
    f.write(html)
print('Open visualization.html in browser')
"
```

**Option B: MCP Tool Integration**
Use the Mapbox MCP tools directly for visualization:
```javascript
// Leverage existing MCP tools
mcp__mapbox__static_map_image_tool  // For static snapshots
mcp__mapbox-devkit__geojson_preview_tool  // For geojson.io preview
mcp__mapbox-devkit__style_builder_tool  // For custom styles
```

**Option C: Accept as External Tool**
Document that this visualization is intentionally a standalone tool that operates outside the inline execution pattern, with clear justification.

### 4. Missing Integration with Plugin Command Structure (HIGH)

**Current Plugin Commands:**

The plugin has 14 commands following a consistent pattern:
- `/bandicoot:load` - Load user data
- `/bandicoot:analyze` - Run analysis
- `/bandicoot:visualize` - Start D3.js dashboard (existing)
- `/bandicoot:export` - Export results

**Plan Gap:**

The Mapbox visualization plan exists in isolation with no defined:
- Slash command to invoke it (e.g., `/bandicoot:map-visualize`)
- Integration with existing `/bandicoot:visualize` command
- Command arguments and flags
- Allowed tools specification

**Required Addition:**

Create command file `commands/map-visualize.md`:
```yaml
---
description: Generate interactive Mapbox GL JS location visualization
argument-hint: <user_id> <records_path> <antennas_path> [--output=map.html] [--contacts=all|top10|id1,id2]
allowed-tools: Bash, Read, Write
---
```

### 5. GeoJSON Data Transformation Pipeline (MEDIUM)

**Current State:**

The plan assumes GeoJSON data with this structure:
```javascript
{
  "type": "Feature",
  "properties": {
    "antenna_id": "string",
    "datetime": "ISO8601 string",
    "timestamp": "number (unix ms)",
    "interaction_type": "call" | "text",
    "direction": "in" | "out",
    "duration": "number",
    "contact_hash": "string"
  }
}
```

**Gap:**

There is no defined transformation from Bandicoot's internal data structures to this GeoJSON format. The plan states:
> "Check for embedded data: if (window.BANDICOOT_DATA)"

But never specifies:
1. How `window.BANDICOOT_DATA` is populated
2. The Python code to generate the GeoJSON
3. How antenna coordinates are merged with record data
4. Privacy considerations for contact identifiers

**Required Specification:**

```python
def generate_visualization_geojson(user):
    """
    Transform Bandicoot user data to visualization GeoJSON.

    Args:
        user: Bandicoot User object with records and antennas

    Returns:
        dict: GeoJSON FeatureCollection
    """
    features = []
    for record in user.records:
        if record.position is None:
            continue  # Skip records without location

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [record.position.longitude, record.position.latitude]
            },
            "properties": {
                "antenna_id": record.antenna_id,
                "datetime": record.datetime.isoformat(),
                "timestamp": int(record.datetime.timestamp() * 1000),
                "interaction_type": record.interaction,
                "direction": record.direction,
                "duration": record.call_duration if record.interaction == 'call' else None,
                "contact_hash": hash_contact(record.correspondent_id)  # Privacy
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "user_id": user.name,
            "total_records": len(user.records),
            "date_range": {
                "start": user.start_time.isoformat(),
                "end": user.end_time.isoformat()
            }
        }
    }
```

---

## Design Quality Assessment

### Strengths

1. **Event-Driven Architecture**
   - The pub/sub EventBus pattern provides excellent decoupling
   - Clear event contracts with documented payloads
   - Error isolation within event handlers

2. **State Management**
   - Single source of truth pattern
   - Clean path-based state access
   - Subscription model for reactive updates

3. **Component Separation**
   - Clear boundaries between controllers and components
   - Well-defined responsibilities
   - Testable in isolation

4. **Visual Design System**
   - Comprehensive CSS custom properties
   - Dark/light theme support with smooth transitions
   - Glassmorphic design is modern and visually appealing

5. **Accessibility Consideration**
   - ARIA labels on interactive elements
   - Keyboard navigation planned
   - Focus management mentioned

### Weaknesses

1. **Over-Engineering for Plugin Context**
   - The sophistication level (12 days, 50+ files) exceeds what's typical for plugin commands
   - Creates maintenance burden disproportionate to other plugin components

2. **No Graceful Degradation**
   - What happens if Mapbox GL JS fails to load?
   - No fallback for browsers without WebGL support
   - No server-side rendering option for export

3. **Memory Management Concerns**
   - For users with 10,000+ records, holding all features in memory may cause issues
   - No virtualization or progressive loading strategy
   - Animation loop could cause memory leaks if not properly cleaned up

4. **Testing Strategy Absent**
   - No unit test specifications
   - No integration test plan
   - No performance benchmarks defined

---

## Scalability Analysis

### Data Volume Concerns

| Records | Memory (est.) | Performance Impact |
|---------|---------------|-------------------|
| 1,000 | ~2 MB | Smooth |
| 10,000 | ~20 MB | Acceptable |
| 50,000 | ~100 MB | Degraded |
| 100,000+ | 200+ MB | Likely problematic |

**Recommendations:**

1. **Implement Data Sampling**
   ```javascript
   // For large datasets, sample at zoom levels
   if (features.length > 10000 && zoom < 10) {
     return sampleFeatures(features, 5000);
   }
   ```

2. **Server-Side Pre-aggregation**
   ```python
   # Pre-aggregate data for large users
   def aggregate_by_antenna_hour(user):
       """Aggregate records by antenna and hour for large datasets."""
       pass
   ```

3. **Progressive Loading**
   - Load visible viewport first
   - Lazy load data as user pans/zooms
   - Use Mapbox vector tiles for very large datasets

---

## Security Considerations

### Data Privacy

1. **Contact Anonymization**
   - The plan uses `contact_hash` but doesn't specify the hashing algorithm
   - Recommendation: Use SHA-256 with a session salt to prevent rainbow table attacks

2. **Location Sensitivity**
   - Antenna locations reveal movement patterns
   - Consider offering location precision reduction option

3. **Mapbox API Key Exposure**
   - Plan stores token in `constants.js`
   - Recommendation: Use environment variable injection or server-side token proxy

### Browser Security

1. **XSS Prevention**
   - GeoJSON data from files should be sanitized
   - Use DOMPurify for any user-generated content in popups

2. **CSP Compatibility**
   - Document Content Security Policy requirements
   - CDN dependencies need explicit allowlisting

---

## Dependency Analysis

### External Dependencies

| Dependency | Purpose | Risk |
|------------|---------|------|
| Mapbox GL JS v3.3.0 | Map rendering | Low - stable, well-maintained |
| Google Fonts (Inter, JetBrains Mono, Space Grotesk) | Typography | Low - high availability |
| No npm packages | Zero build dependencies | **Positive** - aligns with plugin simplicity |

### Internal Dependencies

| Dependency | Integration Point | Risk |
|------------|-------------------|------|
| Bandicoot Python library | Data source | Low - well-defined API |
| Conda environment | Execution context | Medium - requires setup |
| Mapbox MCP server | Token management | Medium - optional but beneficial |

**Recommendation:** Leverage existing Mapbox MCP tools for token management:
```javascript
// Use MCP tool instead of hardcoded token
const token = await mcp__mapbox-devkit__list_tokens_tool({ default: true });
```

---

## Maintainability Assessment

### Code Organization: GOOD

The proposed file structure is clean and follows common patterns:
```
bandicoot-visualizer/
  js/
    core/       # Infrastructure
    controllers/ # Business logic
    components/ # UI elements
    data/       # Data handling
    utils/      # Helpers
```

### Documentation: ADEQUATE

- Inline JSDoc mentioned but not specified
- README planned
- Architecture diagrams included

### Testability: POOR

- No test structure defined
- No mocking strategy for Mapbox GL JS
- No CI/CD integration plan

**Required Addition:**

```
tests/
  unit/
    EventBus.test.js
    StateManager.test.js
    TimeController.test.js
  integration/
    map-load.test.js
    time-animation.test.js
  e2e/
    full-workflow.test.js
```

---

## Recommendations Summary

### Must Have (Before Implementation)

1. **Add user/contact filtering UI and logic**
   - Contact selector component
   - Filter events in EventBus
   - State management for selected contacts

2. **Add proper date/time picker**
   - Calendar-based selection
   - Time-of-day filtering
   - Preset ranges

3. **Define GeoJSON transformation pipeline**
   - Python function to generate GeoJSON from Bandicoot User
   - Privacy-preserving contact hashing
   - Metadata inclusion

4. **Create plugin command integration**
   - New command file `/bandicoot:map-visualize`
   - Argument specification
   - Allowed tools definition

### Should Have (Before Production)

5. **Address inline execution pattern**
   - Choose Option A (self-contained HTML) or Option C (accept as external)
   - Document architectural decision

6. **Add data volume handling**
   - Sampling strategy for large datasets
   - Progressive loading
   - Memory management

7. **Define testing strategy**
   - Unit test specifications
   - Integration test plan
   - Performance benchmarks

### Nice to Have (Future Enhancement)

8. **Mapbox MCP integration**
   - Token management via MCP tools
   - Style customization via MCP

9. **Server-side rendering option**
   - Static map export for reports
   - PDF generation capability

10. **Offline support**
    - Service worker for cached operation
    - Local tile caching

---

## Architectural Decision Records

### ADR-001: Standalone vs Integrated Visualization

**Status:** PENDING DECISION

**Context:** The plan creates a standalone web application, which conflicts with the plugin's inline execution pattern.

**Options:**
- A: Self-contained HTML with embedded code and data
- B: MCP tool composition for visualization
- C: Accept standalone application with documented justification

**Recommendation:** Option A for alignment with plugin philosophy, or Option C with clear documentation if the full interactive experience is deemed essential.

### ADR-002: Contact Filtering Scope

**Status:** PROPOSED

**Context:** Contact filtering was not included in the original plan but is critical for CDR analysis.

**Decision:** Add contact filtering with these capabilities:
- Individual contact selection
- Top-N contacts by frequency
- Contact exclusion
- Search within contacts

**Consequences:** Adds UI complexity but provides essential analytical capability.

---

## Conclusion

The Mapbox GL JS visualization plan demonstrates strong technical architecture and visual design thinking. However, it requires significant additions before it can serve as an effective CDR analysis tool:

1. **Contact filtering is non-negotiable** - CDR analysis without correspondent filtering is fundamentally limited
2. **Date/time selection needs enhancement** - The current approach is insufficient for analytical workflows
3. **Integration with existing plugin patterns must be addressed** - Either by conforming to inline execution or by explicitly documenting the deviation

With these additions and clarifications, the plan would provide a compelling visualization capability for the Bandicoot plugin ecosystem.

**Approval Status:** CONDITIONAL - Approved for implementation once critical gaps are addressed

---

*Review conducted following Clean Architecture principles and Domain-Driven Design patterns.*
