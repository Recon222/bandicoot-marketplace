# Plan Review: Bandicoot Mapbox GL JS Visualization

**Reviewer**: Senior Code Reviewer
**Date**: 2026-01-16
**Plan Document**: `docs/Plans/mapbox-visualization-plan.md`
**Verdict**: **NEEDS REVISION** - Critical features missing, integration unclear

---

## Executive Summary

The plan describes an ambitious, visually impressive Mapbox GL JS visualization system for Bandicoot CDR data. While the technical specifications for the UI components are detailed and the glassmorphic design approach is well-thought-out, the plan has **critical gaps** that must be addressed before implementation.

### Critical Issues (Must Fix)

1. **No User/Contact Filtering Capabilities** - The plan lacks any mechanism to filter visualization by specific users or contacts
2. **No Date/Time Picker Component** - While the plan mentions `datetime-local` inputs in passing, there is no proper date/time picker specification
3. **Unclear Integration with Existing Plugin Architecture** - The plan does not explain how this becomes a Bandicoot command/skill
4. **Missing Data Transformation Pipeline** - How does Bandicoot CDR data become GeoJSON?
5. **No Mapbox Token Management Strategy** - Critical security gap

---

## Critical Missing Features

### 1. User/Contact Filtering - CRITICAL MISSING

**Status**: Completely absent from the plan

The plan provides time-based filtering (Phase 3) and event type filtering (call/text, direction in/out), but there is **zero mention** of:

- Filtering by specific `correspondent_id` (contact)
- Filtering by user when multiple users are loaded
- Multi-select contact filtering
- Contact search/autocomplete functionality
- "Show only communications with contact X" capability

**Why This Matters**: CDR analysis frequently requires isolating communications with specific contacts. A user might want to see "all locations where I communicated with contact_001" or "compare my activity patterns with two specific contacts." Without this, the visualization loses significant analytical value.

**Recommendation**: Add a **ContactFilter Component** specification:

```javascript
// Missing component that should be specified
class ContactFilter {
  // Multi-select dropdown with search
  // Checkbox list of all contacts in dataset
  // "Select All" / "Clear All" controls
  // Contact count display
  // Integration with FilterEngine
}
```

This should emit `filter:contacts` events and integrate with the existing FilterEngine.

### 2. Date/Time Picker - CRITICAL MISSING

**Status**: Mentioned only in passing (line 738-739), no specification

The plan shows:

```html
<input type="datetime-local" class="range-selector__input" id="range-start">
```

This is insufficient. A proper date/time picker specification should include:

- **Calendar popup component** with month/year navigation
- **Time picker** with hour/minute selectors
- **Quick preset buttons** (Today, Yesterday, Last 7 days, Last 30 days, Custom)
- **Timezone handling** - CDR data may span multiple timezones
- **Validation** - prevent selecting dates outside data range
- **Mobile-friendly design** - native `datetime-local` has poor mobile UX

**Why This Matters**: Users need precise temporal control. The time slider is excellent for scrubbing/playback, but for analytical queries like "show me activity on March 15, 2014 between 9 AM and 5 PM", a proper date/time picker is essential.

**Recommendation**: Add a full **DateTimePicker Component** specification in Phase 3, including:

- Calendar view
- Time input with AM/PM toggle
- Timezone selector (or at minimum, clear timezone display)
- Integration with existing QuickSelectors
- Accessibility compliance (keyboard navigation, ARIA)

---

## Major Integration Issues

### 3. Plugin Architecture Integration - UNCLEAR

**Status**: Not addressed

The plan describes a standalone web application (`bandicoot-visualizer/`) but does not explain:

- How does this integrate with the existing plugin structure (`commands/`, `skills/`, `agents/`)?
- Is this a new `/bandicoot:visualize-map` command?
- Does this replace or supplement the existing `/bandicoot:visualize` command (which uses D3.js)?
- Where do the visualization files live in the plugin directory structure?
- How is the visualization served? Local HTTP server? Exported HTML?

**Current `visualize.md` command** (line 1-147) uses Bandicoot's built-in `bc.visualization.run()` which is D3.js-based. The new Mapbox visualization appears to be entirely separate.

**Recommendation**: Add a new section titled "Plugin Integration" that specifies:

1. New command file: `commands/visualize-map.md`
2. Whether this is a supplement or replacement
3. How the HTML/JS/CSS assets are delivered to users
4. Server requirements (if any)

### 4. Data Transformation Pipeline - MISSING

**Status**: Not addressed

The plan shows expected GeoJSON format (lines 256-275, 2272-2309) but never explains how Bandicoot CDR data transforms into this format.

**Current Bandicoot Data Flow**:
```
CSV files -> bc.read_csv() -> User object -> Analysis results
```

**Required for Visualization**:
```
User object -> ??? -> GeoJSON FeatureCollection
```

The `???` is never specified. The plan assumes GeoJSON magically exists.

**Questions that must be answered**:

1. Does Bandicoot have a built-in GeoJSON export? (It does not appear to)
2. Is a new Python transformation script needed?
3. Where does this transformation run - in the browser or server-side?
4. What happens when records lack `antenna_id`? (many CDRs have null locations)
5. How are records without location data handled in the visualization?

**Recommendation**: Add a "Data Transformation" section covering:

```python
# Conceptual - needs specification
def bandicoot_to_geojson(user):
    """Transform Bandicoot User object to GeoJSON FeatureCollection."""
    features = []
    for record in user.records:
        if record.position:  # Has location data
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [record.position.longitude, record.position.latitude]
                },
                "properties": {
                    "antenna_id": record.antenna_id,
                    "datetime": str(record.datetime),
                    "timestamp": int(record.datetime.timestamp() * 1000),
                    "interaction_type": record.interaction,
                    "direction": record.direction,
                    "duration": getattr(record, 'call_duration', None),
                    "contact_hash": hash(record.correspondent_id)  # Anonymization
                }
            })
    return {"type": "FeatureCollection", "features": features}
```

### 5. Mapbox Token Management - SECURITY GAP

**Status**: Mentioned once, not addressed

The plan references `MAPBOX_TOKEN` (line 1810) but provides no strategy for:

- Where does the token come from?
- Is it embedded in JavaScript (security risk for public tokens)?
- How do users configure their own Mapbox account?
- What scopes/permissions are required?
- Rate limiting considerations

**Why This Matters**: Mapbox GL JS requires an access token. If the plugin embeds a shared token, it will be abused. If users must provide their own, the UX must be clear.

**Recommendation**: Add "Token Configuration" section specifying:

1. Users must provide their own Mapbox token
2. Token stored in environment variable or config file
3. Token injected at visualization generation time
4. Clear error message if token missing/invalid

---

## Important Issues (Should Fix)

### 6. Violation of Plugin Pattern: No Wrapper Scripts

**Status**: Plan creates a multi-file JavaScript application

The `CLAUDE.md` explicitly states:

> **NEVER create wrapper scripts around Bandicoot.** All Bandicoot operations must be executed inline.

The plan creates an extensive JavaScript application with 20+ files. While this is JavaScript (not Python wrappers), the spirit of the constraint is about keeping things simple and transparent.

**Questions**:

- Is a complex JS application appropriate for this plugin?
- Who maintains these files if Mapbox GL JS has breaking changes?
- How does this align with the "just works" philosophy?

**Recommendation**: Consider a simpler approach:

1. Generate a single self-contained HTML file with embedded CSS/JS
2. Use CDN links for Mapbox GL JS (already planned)
3. Inline all custom JavaScript rather than ES6 modules
4. Output: One HTML file that opens in browser

This matches the existing `bc.visualization.export()` pattern better.

### 7. No Error Handling Specification

**Status**: Minimal mention

The plan does not specify behavior for:

- Empty dataset (no records)
- Dataset with no location data (all `antenna_id` null)
- Invalid GeoJSON
- Mapbox API failures
- Network connectivity issues
- Large dataset performance warnings

**Recommendation**: Add "Error States" section covering user-facing error messages and fallback behaviors.

### 8. Missing Accessibility Details

**Status**: Mentioned in Phase 5 checklist but not specified

The plan lists accessibility as a Phase 5 deliverable but provides no specifications:

- Screen reader support for the map (how?)
- Keyboard navigation for time slider (how?)
- ARIA labels (what content?)
- Focus management (what order?)
- Color contrast (only mentions "WCAG 2.1 AA" checkbox)

**Recommendation**: Either:
1. Add detailed accessibility specifications, or
2. Acknowledge this is a visual-first tool with limited accessibility support

### 9. Mobile/Responsive Design

**Status**: One checkbox mention - "Mobile-responsive (tablets minimum)"

A full-viewport map application requires explicit responsive design:

- How do controls adapt on tablet vs desktop?
- Is touch gesture support different from mouse?
- What minimum viewport size is supported?
- Does the time slider collapse or reposition on narrow screens?

**Recommendation**: Add responsive breakpoint specifications.

---

## Minor Issues (Nice to Fix)

### 10. Unrealistic Timeline

12 days for a production-quality visualization system is aggressive. The scope includes:

- Custom pub/sub architecture
- State management system
- Complex time animation system
- Glassmorphic design system
- Accessibility compliance
- 60fps performance optimization
- Cross-browser testing

**Recommendation**: Either expand timeline to 20-25 days or reduce scope.

### 11. Over-Engineering Concerns

The plan includes:

- Custom EventBus implementation (why not use native CustomEvents?)
- Custom StateManager (why not use a lightweight library?)
- Event history tracking (is this needed?)
- Complex animation system (is 60fps animation actually needed for CDR data?)

**Recommendation**: Consider using simpler, battle-tested alternatives where possible.

### 12. No Offline/Export Capability

The current `visualize` command supports `--export` for static files. The new plan only describes a live JavaScript application.

**Recommendation**: Specify export capability to match existing command pattern.

---

## What the Plan Does Well

1. **Detailed Component Specifications** - HTML structures, CSS custom properties, and JavaScript implementations are thoroughly documented.

2. **Event Architecture** - The pub/sub event table (lines 66-78) clearly defines system communication.

3. **Visual Design System** - The glassmorphic design with dark/light themes is well-specified with color codes, spacing scales, and animation timings.

4. **Mapbox Integration** - The cluster layer configuration and filter expressions are technically sound.

5. **Time System Design** - The TimeController animation loop and TimeSlider component are well-thought-out.

6. **Sample Data** - GeoJSON sample format is clearly specified.

---

## Required Changes Summary

| Priority | Issue | Action Required |
|----------|-------|-----------------|
| **CRITICAL** | No user/contact filtering | Add ContactFilter component specification |
| **CRITICAL** | No date/time picker | Add DateTimePicker component specification |
| **CRITICAL** | No data transformation pipeline | Specify Bandicoot-to-GeoJSON conversion |
| **CRITICAL** | No plugin integration plan | Add plugin architecture section |
| **CRITICAL** | No token management | Add Mapbox token configuration section |
| Important | Complex multi-file structure | Consider single-file export approach |
| Important | No error handling | Add error states specification |
| Important | Vague accessibility | Add detailed a11y specifications |
| Minor | Unrealistic timeline | Adjust to 20-25 days |
| Minor | No export capability | Add --export option specification |

---

## Conclusion

The plan demonstrates strong front-end design skills and a clear vision for an impressive visualization. However, it is fundamentally incomplete as a Bandicoot plugin feature specification.

**The plan must be revised to include:**

1. User/contact filtering capabilities
2. Proper date/time picker component
3. Data transformation from Bandicoot to GeoJSON
4. Plugin integration strategy (command file, asset delivery)
5. Mapbox token management

Without these additions, the plan cannot proceed to implementation.

---

**Reviewer Sign-off**: Plan requires revision before approval.

**Next Step**: Author should revise the plan to address critical issues, then request re-review.
