# Dashboard Visualization Plan for Investigation Indicators

> High-level architecture and options for displaying Bandicoot investigation indicator results in single-file HTML/ES6/CSS dashboard templates

---

## Executive Summary

This plan outlines approaches for creating self-contained HTML dashboards that display results from the 47 custom investigation indicators. The dashboards are designed for law enforcement investigators reviewing production order cell phone records, with a focus on:

- **Single-file distribution** - Each dashboard is a complete, portable HTML file
- **Full-page metrics** - Each indicator gets maximum visual real estate
- **Investigative workflows** - Grouped by investigative purpose, not technical category
- **Offline capability** - Works without internet connection in secure environments

---

## Part 1: Dashboard Architecture Options

### 1.1 Single-File Template Structure

All dashboards follow this basic structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Title</title>
    <style>
        /* All CSS embedded here */
    </style>
</head>
<body>
    <nav><!-- Navigation --></nav>
    <main><!-- Content panels --></main>

    <script>
        // JSON data injection point
        const INDICATOR_DATA = /* INJECT_DATA_HERE */;

        // ES6 application code
    </script>
</body>
</html>
```

**Data Injection Pattern Options:**

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Template Literal** | Python replaces `/* INJECT_DATA_HERE */` with JSON | Simple, reliable | Large JSON visible in source |
| **Base64 Encoded** | Data encoded in a data attribute | Hides raw data | Decode overhead, debugging harder |
| **Script Tag Injection** | `<script id="data" type="application/json">` | Clean separation | Extra parsing step |

**Recommendation:** Use **Template Literal** injection for simplicity. Investigators need to see/verify data, not hide it.

### 1.2 Navigation Architecture Options

#### Option A: Tabbed Interface (Recommended for <10 metrics)

```
[Tab 1] [Tab 2] [Tab 3] [Tab 4] [Tab 5]
+------------------------------------------+
|                                          |
|        Full-page content area            |
|        for selected metric               |
|                                          |
+------------------------------------------+
```

**Pros:**
- Familiar UI pattern
- All options visible at once
- Fast switching

**Cons:**
- Limited to ~8-10 tabs before wrapping
- Mobile unfriendly with many tabs

#### Option B: Sidebar Navigation (Recommended for 10+ metrics)

```
+--------+----------------------------------+
| Nav    |                                  |
| -----  |                                  |
| Item 1 |    Full-page content area        |
| Item 2 |    for selected metric           |
| Item 3 |                                  |
| Item 4 |                                  |
| ...    |                                  |
+--------+----------------------------------+
```

**Pros:**
- Scales to many items
- Can include grouping/hierarchy
- Collapsible for more content space

**Cons:**
- Takes horizontal space
- Requires scroll for long lists

#### Option C: Dropdown Selector (Minimal chrome)

```
+------------------------------------------+
| Select Metric: [Dropdown v]              |
+------------------------------------------+
|                                          |
|        Maximum content area              |
|        for selected metric               |
|                                          |
+------------------------------------------+
```

**Pros:**
- Maximum content area
- Scales infinitely
- Print-friendly (can hide)

**Cons:**
- Only one item visible at a time
- Extra click to switch

#### Option D: Hybrid - Grouped Tabs with Dropdown

```
[Relationships] [Temporal] [Location] [Network]
     |
     v
+------------------------------------------+
| Sub-metric: [Dropdown v]                 |
+------------------------------------------+
|                                          |
|        Full-page content area            |
|                                          |
+------------------------------------------+
```

**Pros:**
- Category overview at top
- Detailed selection within category
- Best of both worlds

**Cons:**
- More complex to implement
- Two-level mental model

**Recommendation:** Use **Option D (Hybrid)** for dashboards with many indicators, **Option A (Tabs)** for focused dashboards with fewer metrics.

---

## Part 2: Logical Dashboard Groupings

### 2.1 Proposed Dashboard Structure

Rather than grouping by technical category (relationship, temporal, location, etc.), dashboards are organized by **investigative workflow** - what questions investigators ask at each stage.

#### Dashboard 1: Subject Profile Dashboard (Single User)
**File:** `subject-profile-dashboard.html`

**Purpose:** Comprehensive profile of a single subject - the first thing investigators want when examining a person of interest.

| Metric | Return Type | Visualization |
|--------|-------------|---------------|
| `relationship_strength` | `dict[str, float]` | Ranked contact list with strength bars |
| `contact_interaction_summary` | `dict[str, dict]` | Expandable contact cards |
| `reciprocity_score` | `dict[str, float]` | Balance indicators per contact |
| `initiation_ratio` | `dict[str, float]` | Who-initiates chart |
| `first_contact_of_day` | `dict[str, int]` | Morning contact frequency |
| `last_contact_of_day` | `dict[str, int]` | Evening contact frequency |
| `hourly_activity_profile` | `dict[int, int]` | 24-hour activity chart |
| `daily_activity_counts` | `dict[date, int]` | Calendar heatmap |
| `inter_event_times` | `SummaryStats` | Distribution histogram |

**Navigation:** Tabs for "Contacts", "Activity Pattern", "Communication Style"

---

#### Dashboard 2: Timeline & Events Dashboard (Single User)
**File:** `timeline-events-dashboard.html`

**Purpose:** Chronological view of significant events - gaps, bursts, and anomalies.

| Metric | Return Type | Visualization |
|--------|-------------|---------------|
| `communication_gaps` | `list[dict]` | Timeline with gap markers |
| `activity_bursts` | `list[dict]` | Timeline with burst highlights |
| `contact_first_appearance` | `dict[str, datetime]` | New contacts timeline |
| `contact_last_appearance` | `dict[str, datetime]` | Lost contacts timeline |
| `activity_around_time` | `dict` | Before/after comparison (requires target time) |
| `first_contact_after_time` | `dict` | Critical moment analysis |

**Navigation:** Single scrollable timeline with jump-to markers

---

#### Dashboard 3: Location Intelligence Dashboard (Single User)
**File:** `location-intelligence-dashboard.html`

**Purpose:** Where was the subject? Movement patterns and significant locations.

| Metric | Return Type | Visualization |
|--------|-------------|---------------|
| `location_timeline` | `list[dict]` | Chronological location list (map-ready) |
| `frequent_locations_ranked` | `list[dict]` | Top locations with percentages |
| `unusual_locations` | `list[dict]` | Rare visit highlights |
| `location_transitions` | `list[dict]` | Movement diagram |
| `time_at_locations` | `dict[str, float]` | Time distribution pie/bar |
| `location_at_specific_time` | `dict` | Point-in-time query result |
| `locations_in_time_range` | `list[dict]` | Time-filtered location list |

**Navigation:** Tabs for "Frequent Locations", "Movement", "Time Query", "Anomalies"

**Note:** If coordinates are available, these could feed a map visualization (external tool or embedded lightweight map).

---

#### Dashboard 4: Alibi & Incident Dashboard (Single User, Time-Focused)
**File:** `alibi-incident-dashboard.html`

**Purpose:** "Where was the subject at the time of the crime?" Focused analysis around a specific datetime.

| Metric | Return Type | Visualization |
|--------|-------------|---------------|
| `location_at_specific_time` | `dict` | Location with confidence indicator |
| `activity_around_time` | `dict` | Before/after activity comparison |
| `first_contact_after_time` | `dict` | First contact details |
| `locations_in_time_range` | `list[dict]` | All locations in window |

**Navigation:** Single-page focused view with target time prominently displayed

---

#### Dashboard 5: Co-Location Analysis Dashboard (Two Users)
**File:** `colocation-analysis-dashboard.html`

**Purpose:** Were two subjects together? Prove or disprove co-presence.

| Metric | Return Type | Visualization |
|--------|-------------|---------------|
| `antenna_overlap` | `list[dict]` | Co-location events table with timeline |
| `travel_pattern_match` | `list[dict]` | Matching route visualization |
| `meeting_detection` | `list[dict]` | Probable meetings with confidence |

**Navigation:** Tabs for "Overlaps", "Travel Matches", "Meetings"

---

#### Dashboard 6: Group Coordination Dashboard (Multi-User)
**File:** `group-coordination-dashboard.html`

**Purpose:** Analyze coordination across 3+ subjects - meetings, silences, locations.

| Metric | Return Type | Visualization |
|--------|-------------|---------------|
| `multi_user_colocation` | `list[dict]` | Group meeting events |
| `synchronized_silence` | `list[dict]` | Suspicious silence periods (ranked by score) |
| `group_locations_at_time` | `dict[str, dict]` | "Where was everyone" matrix |
| `proximity_to_location` | `list[dict]` | Crime scene proximity (per user) |

**Navigation:** Tabs for "Group Meetings", "Synchronized Silence", "Location Matrix"

---

#### Dashboard 7: Network Structure Dashboard (Multi-User)
**File:** `network-structure-dashboard.html`

**Purpose:** Who is the hub? How does information flow? Network-level analysis.

| Metric | Return Type | Visualization |
|--------|-------------|---------------|
| `build_communication_matrix` | `dict[tuple, int]` | Matrix heatmap |
| `degree_centrality` | `dict[str, dict]` | Centrality rankings |
| `communication_chains` | `list[dict]` | A->B->C flow diagrams |
| `shared_contacts` | `dict[str, list]` | Venn-style shared contact display |
| `communication_volume_matrix` | `dict[tuple, dict]` | Detailed pair statistics |
| `network_timeline` | `list[dict]` | Network evolution over time |
| `identify_bridges` | `list[dict]` | Bridge users highlighted |

**Navigation:** Tabs for "Centrality", "Chains", "Shared Contacts", "Evolution"

---

### 2.2 Dashboard Summary

| Dashboard | Users | Indicators | Primary Use Case |
|-----------|-------|------------|------------------|
| Subject Profile | 1 | 9 | Initial subject assessment |
| Timeline & Events | 1 | 6 | Anomaly detection |
| Location Intelligence | 1 | 7 | Movement analysis |
| Alibi & Incident | 1 | 4 | Time-of-crime focus |
| Co-Location Analysis | 2 | 3 | Two-person connection |
| Group Coordination | 3+ | 4 | Multi-person coordination |
| Network Structure | 3+ | 7 | Network-level analysis |

**Total:** 7 dashboards covering all 47 indicators (some indicators appear in multiple dashboards where contextually appropriate).

---

## Part 3: Per-Metric Full-Page Layouts

### 3.1 Visualization Types by Return Type

#### Type A: Ranked Dictionary (`dict[str, float]`)
**Examples:** `relationship_strength`, `reciprocity_score`, `initiation_ratio`

**Layout Option 1: Horizontal Bar Chart with Table**
```
+------------------------------------------+
|  Metric Name: Relationship Strength      |
+------------------------------------------+
| [============================] Contact A  0.95 |
| [=====================]       Contact B  0.72 |
| [=============]               Contact C  0.45 |
| [======]                      Contact D  0.23 |
+------------------------------------------+
| Click any bar for contact details        |
+------------------------------------------+
```

**Layout Option 2: Sortable Data Table**
```
+------------------------------------------+
| Rank | Contact      | Score | Visual     |
|------|--------------|-------|------------|
| 1    | Contact A    | 0.95  | [========] |
| 2    | Contact B    | 0.72  | [======]   |
| 3    | Contact C    | 0.45  | [====]     |
+------------------------------------------+
```

**Recommendation:** Use Bar Chart for visual impact on full page, with sortable table below for detail.

---

#### Type B: Count Dictionary (`dict[str, int]`)
**Examples:** `first_contact_of_day`, `last_contact_of_day`, `hourly_activity_profile`

**For hourly profile (24 values):**
```
+------------------------------------------+
|  24-Hour Activity Profile                |
+------------------------------------------+
|     |                                    |
| 50  |          *****                     |
| 40  |        ********   **               |
| 30  |       **********  ***              |
| 20  |      ************ *****            |
| 10  |     ******************             |
|  0  +------------------------------------+
|     0  3  6  9  12 15 18 21              |
+------------------------------------------+
```

**For contact counts (variable values):**
Use horizontal bar chart similar to Type A.

---

#### Type C: Timeline List (`list[dict]` with datetime)
**Examples:** `communication_gaps`, `activity_bursts`, `location_timeline`

**Layout Option 1: Vertical Timeline**
```
+------------------------------------------+
|  Communication Gaps (>24 hours)          |
+------------------------------------------+
|                                          |
|  2024-06-14 23:45  [START]               |
|       |                                  |
|       | 56.75 hours (2.5 days)           |
|       |                                  |
|  2024-06-17 08:30  [END]                 |
|                                          |
|  -------- gap --------                   |
|                                          |
|  2024-06-20 18:00  [START]               |
|       |                                  |
|       | 44.25 hours                      |
|       |                                  |
|  2024-06-22 14:15  [END]                 |
|                                          |
+------------------------------------------+
```

**Layout Option 2: Horizontal Timeline with Markers**
```
+------------------------------------------+
|  Jun 14    Jun 15    Jun 16    Jun 17    |
|  ---|------[=========GAP=========]|----  |
|             56.75h                        |
+------------------------------------------+
```

**Recommendation:** Use horizontal timeline for overview, vertical detail list for specifics.

---

#### Type D: Nested Detail Dictionary (`dict[str, dict]`)
**Examples:** `contact_interaction_summary`, `degree_centrality`

**Layout: Expandable Card Grid**
```
+------------------------------------------+
|  Contact Interaction Summary             |
+------------------------------------------+
| +----------------+ +----------------+    |
| | Contact A      | | Contact B      |    |
| | Total: 347     | | Total: 156     |    |
| | [v] Expand     | | [v] Expand     |    |
| +----------------+ +----------------+    |
|                                          |
| +----------------+ +----------------+    |
| | Contact C      | | Contact D      |    |
| | Total: 89      | | Total: 45      |    |
| | [v] Expand     | | [v] Expand     |    |
| +----------------+ +----------------+    |
+------------------------------------------+

Expanded Card:
+------------------------------------------+
| Contact A                         [^]    |
|------------------------------------------|
| Total Interactions: 347                  |
|------------------------------------------|
| Calls In:  45    | Calls Out: 62         |
| Texts In: 120    | Texts Out: 120        |
|------------------------------------------|
| Total Call Duration: 5h 7m 30s           |
|------------------------------------------|
| First Contact: Jan 15, 2024 08:30        |
| Last Contact:  Jun 20, 2024 23:15        |
+------------------------------------------+
```

---

#### Type E: Statistics Object (`SummaryStats`)
**Examples:** `inter_event_times`

**Layout: Stats Summary Card**
```
+------------------------------------------+
|  Inter-Event Time Distribution           |
+------------------------------------------+
| +----------+ +----------+ +----------+   |
| |  MEAN    | |  MEDIAN  | |  STD     |   |
| |  47 min  | |  20 min  | |  90 min  |   |
| +----------+ +----------+ +----------+   |
|                                          |
| +----------+ +----------+                |
| |  MIN     | |  MAX     |                |
| |  15 sec  | |  24 hrs  |                |
| +----------+ +----------+                |
|                                          |
| [Optional: Histogram if raw data avail]  |
+------------------------------------------+
```

---

#### Type F: Before/After Comparison (`dict` with before/after)
**Examples:** `activity_around_time`

**Layout: Split Panel Comparison**
```
+------------------------------------------+
|  Activity Around: Jun 15, 2024 14:30     |
+------------------------------------------+
|        BEFORE           |      AFTER     |
|       (6 hours)         |    (6 hours)   |
|-------------------------|----------------|
|  12 interactions        |  5 interactions|
|                         |                |
|  Top Contacts:          |  Top Contacts: |
|  - Contact A (5)        |  - Contact C (3)|
|  - Contact B (4)        |  - Contact A (2)|
|  - Contact C (3)        |                |
|-------------------------|----------------|
|      [Timeline showing both periods]     |
+------------------------------------------+
```

---

#### Type G: Single Result (`dict` or `None`)
**Examples:** `location_at_specific_time`, `first_contact_after_time`

**Layout: Focused Result Card**
```
+------------------------------------------+
|  Location at 14:30 on Jun 15, 2024       |
+------------------------------------------+
|                                          |
|  +------------------------------------+  |
|  |  ANTENNA: ANT_042                  |  |
|  |  CONFIDENCE: [====HIGH====]        |  |
|  +------------------------------------+  |
|                                          |
|  Coordinates: 43.6612, -79.3950          |
|  Actual Record: 14:28:30 (90 sec before) |
|                                          |
|  Activity: call out to Contact A         |
|                                          |
+------------------------------------------+
```

---

#### Type H: Multi-User Matrix (`dict[tuple, ...]`)
**Examples:** `build_communication_matrix`, `communication_volume_matrix`

**Layout: Heatmap Matrix**
```
+------------------------------------------+
|  Communication Matrix                    |
+------------------------------------------+
|        | User A | User B | User C | ... |
|--------|--------|--------|--------|-----|
| User A |   --   |   45   |   18   |     |
| User B |   32   |   --   |   67   |     |
| User C |   22   |   89   |   --   |     |
+------------------------------------------+
| Color scale: Light (low) -> Dark (high)  |
+------------------------------------------+
```

---

#### Type I: Multi-User Location Snapshot (`dict[str, dict]`)
**Examples:** `group_locations_at_time`

**Layout: Location Matrix Table**
```
+------------------------------------------+
|  Group Locations at 14:30 Jun 15, 2024   |
+------------------------------------------+
| User     | Location  | Confidence | Note |
|----------|-----------|------------|------|
| User A   | ANT_042   | HIGH       | call |
| User B   | ANT_042   | HIGH       | text |  <-- SAME!
| User C   | ANT_015   | MEDIUM     | call |
| User D   | UNKNOWN   | --         |      |
+------------------------------------------+
| [!] Users A and B at same location       |
+------------------------------------------+
```

---

#### Type J: Suspicion-Scored Events (`list[dict]` with scores)
**Examples:** `synchronized_silence`

**Layout: Scored Event List**
```
+------------------------------------------+
|  Synchronized Silence Events             |
|  (sorted by suspicion score)             |
+------------------------------------------+
| +--------------------------------------+ |
| | SUSPICION: 0.723 [==========]  HIGH  | |
| |--------------------------------------| |
| | Jun 15, 14:30 - 17:45 (3h 15m)       | |
| | Participants: User A, B, C (3/4)     | |
| | [Expand for details]                 | |
| +--------------------------------------+ |
|                                          |
| +--------------------------------------+ |
| | SUSPICION: 0.512 [======]    MEDIUM  | |
| |--------------------------------------| |
| | Jun 18, 22:00 - Jun 19, 06:30        | |
| | Participants: User A, B (2/4)        | |
| | [Expand for details]                 | |
| +--------------------------------------+ |
+------------------------------------------+
```

---

## Part 4: Template Technology Options

### 4.1 JavaScript Framework Options

#### Option A: Pure Vanilla ES6 (Recommended)

**Approach:** No external dependencies, all code inline.

```javascript
// Example: Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
        document.querySelectorAll('.panel').forEach(p => p.hidden = true);
        document.getElementById(e.target.dataset.panel).hidden = false;
    });
});
```

**Pros:**
- Zero dependencies
- No CDN required (offline works)
- Smallest file size
- Maximum compatibility

**Cons:**
- More code for complex interactions
- No reactive data binding

**Recommendation:** Use for all dashboards. Modern ES6 is sufficient for the UI requirements.

---

#### Option B: Alpine.js (via CDN or inline)

**Approach:** Lightweight reactivity for data binding.

```html
<div x-data="{ selected: 'tab1' }">
    <button @click="selected = 'tab1'">Tab 1</button>
    <div x-show="selected === 'tab1'">Content 1</div>
</div>
```

**Pros:**
- Declarative syntax
- Reactive updates
- Small (~15KB)

**Cons:**
- External dependency (can inline)
- Learning curve

**Recommendation:** Consider only if complex reactive UI needed.

---

### 4.2 Chart Library Options

#### Option A: Vanilla SVG Generation (Recommended)

**Approach:** Generate SVG charts directly from data.

```javascript
function barChart(data, width, height) {
    const maxValue = Math.max(...Object.values(data));
    let svg = `<svg width="${width}" height="${height}">`;
    // Generate bars...
    svg += '</svg>';
    return svg;
}
```

**Pros:**
- Zero dependencies
- Full control over styling
- Print-friendly
- Smallest size

**Cons:**
- More code to write
- Limited to simple charts

**Suitable for:** Bar charts, timelines, simple line charts.

---

#### Option B: Chart.js (via CDN)

**Approach:** Full-featured charting library.

**Pros:**
- Rich chart types
- Animations
- Tooltips built-in

**Cons:**
- ~200KB dependency
- Requires CDN or inline (large)
- Canvas-based (print issues)

**Recommendation:** Avoid unless complex charts needed.

---

#### Option C: D3.js Subset (Inline micro-library)

**Approach:** Extract only needed D3 functions.

**Pros:**
- Powerful for custom visualizations
- Can subset to ~20KB

**Cons:**
- Complex API
- Overkill for simple charts

**Recommendation:** Consider only for network diagrams.

---

### 4.3 CSS Framework Options

#### Option A: No Framework - Custom CSS (Recommended)

**Approach:** Write minimal, purpose-built CSS.

```css
:root {
    --primary: #2563eb;
    --danger: #dc2626;
    --success: #16a34a;
    --bg: #ffffff;
    --text: #1f2937;
}

.card { padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; }
.bar { height: 1.5rem; background: var(--primary); }
```

**Pros:**
- Minimal file size
- No unused styles
- Easy to customize
- Print-friendly

**Cons:**
- Must write everything

**Recommendation:** Use this approach. ~200-300 lines of CSS is sufficient.

---

#### Option B: Tailwind CSS (via CDN)

**Approach:** Utility classes.

**Pros:**
- Rapid styling
- Consistent design

**Cons:**
- Large CDN dependency
- Verbose HTML
- Offline issues

**Recommendation:** Avoid for single-file templates.

---

### 4.4 Technology Stack Summary

| Component | Recommendation | Rationale |
|-----------|----------------|-----------|
| JavaScript | Vanilla ES6 | Zero dependencies, offline capable |
| Charts | Vanilla SVG | Lightweight, print-friendly |
| CSS | Custom minimal | Purpose-built, small size |
| Data | JSON template literal | Simple, debuggable |

---

## Part 5: Data Flow Options

### 5.1 Python Results to Dashboard

#### Option A: Direct Template Injection (Recommended)

**Python side:**
```python
import json

def generate_dashboard(template_path, output_path, data):
    with open(template_path, 'r') as f:
        template = f.read()

    # Inject data
    json_data = json.dumps(data, default=str, indent=2)
    html = template.replace('/* INJECT_DATA_HERE */', json_data)

    with open(output_path, 'w') as f:
        f.write(html)
```

**Template side:**
```javascript
const INDICATOR_DATA = /* INJECT_DATA_HERE */;
```

**Pros:**
- Simple and reliable
- Data visible for verification
- Easy debugging

---

#### Option B: Multi-Section Injection

For dashboards with multiple indicators:

```javascript
const DATA = {
    relationship_strength: /* INJECT_RELATIONSHIP_STRENGTH */,
    reciprocity_score: /* INJECT_RECIPROCITY_SCORE */,
    // etc.
};
```

**Pros:**
- Clear separation
- Can inject partial data

---

### 5.2 Export/Save Mechanisms

#### Option A: Print to PDF (Browser Native)

```javascript
function exportToPDF() {
    window.print();
}
```

**Pros:**
- No dependencies
- Works everywhere

**Cons:**
- Pagination can be tricky
- Limited control

---

#### Option B: Download as HTML (Self-Contained)

```javascript
function downloadHTML() {
    const html = document.documentElement.outerHTML;
    const blob = new Blob([html], { type: 'text/html' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'dashboard-export.html';
    a.click();
}
```

**Pros:**
- Preserves interactivity
- Exact copy

---

#### Option C: Download Data as JSON

```javascript
function downloadData() {
    const json = JSON.stringify(INDICATOR_DATA, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'indicator-data.json';
    a.click();
}
```

**Pros:**
- Raw data for further analysis
- Small file size

---

#### Option D: Download as CSV (Selected Metrics)

```javascript
function downloadCSV(data, filename) {
    const rows = Object.entries(data).map(([k, v]) => `${k},${v}`);
    const csv = ['Key,Value', ...rows].join('\n');
    // ... download logic
}
```

**Pros:**
- Excel compatible
- Familiar format

---

### 5.3 Print-Friendly Considerations

```css
@media print {
    .no-print { display: none; }
    .page-break { page-break-before: always; }

    /* Remove interactive elements */
    nav, .export-buttons { display: none; }

    /* Ensure charts print well */
    svg { max-width: 100%; }

    /* Show all panels (not just selected tab) */
    .panel { display: block !important; }
}
```

**Recommendation:** Include print styles in all templates. Courts and legal proceedings often require paper documentation.

---

## Part 6: Implementation Considerations

### 6.1 Investigative Use Case Requirements

1. **Secure/Offline Environment:** Law enforcement systems may not have internet access. All resources must be embedded.

2. **Evidentiary Standards:** Data must be verifiable. Raw JSON should be viewable.

3. **Court Presentation:** Print output must be professional and readable.

4. **Quick Assessment:** Investigators need to rapidly identify key findings.

5. **Detail on Demand:** Summary views with expandable details.

### 6.2 Accessibility Considerations

- Color should not be the only indicator (add text labels)
- Sufficient contrast ratios
- Keyboard navigation for tabs
- Screen reader compatibility for tables

### 6.3 File Size Targets

| Dashboard | Target Size |
|-----------|-------------|
| Small (4 metrics) | < 50KB (without data) |
| Medium (7 metrics) | < 75KB (without data) |
| Large (9 metrics) | < 100KB (without data) |

Data injection will add to these sizes based on dataset size.

---

## Part 7: Recommended Implementation Order

### Phase 1: Foundation Templates
1. **Subject Profile Dashboard** - Most commonly needed, establishes patterns
2. **Alibi & Incident Dashboard** - Critical for time-of-crime questions

### Phase 2: Single-User Expansion
3. **Timeline & Events Dashboard** - Anomaly detection
4. **Location Intelligence Dashboard** - Movement analysis

### Phase 3: Multi-User Templates
5. **Co-Location Analysis Dashboard** - Two-person analysis
6. **Group Coordination Dashboard** - Multi-person coordination
7. **Network Structure Dashboard** - Network-level analysis

---

## Appendix A: Indicator-to-Dashboard Mapping

| Indicator | Dashboard(s) |
|-----------|--------------|
| `relationship_strength` | Subject Profile |
| `reciprocity_score` | Subject Profile |
| `initiation_ratio` | Subject Profile |
| `first_contact_of_day` | Subject Profile |
| `last_contact_of_day` | Subject Profile |
| `contact_interaction_summary` | Subject Profile |
| `hourly_activity_profile` | Subject Profile |
| `daily_activity_counts` | Subject Profile, Timeline & Events |
| `inter_event_times` | Subject Profile |
| `communication_gaps` | Timeline & Events |
| `activity_bursts` | Timeline & Events |
| `contact_first_appearance` | Timeline & Events |
| `contact_last_appearance` | Timeline & Events |
| `activity_around_time` | Timeline & Events, Alibi & Incident |
| `first_contact_after_time` | Timeline & Events, Alibi & Incident |
| `location_timeline` | Location Intelligence |
| `frequent_locations_ranked` | Location Intelligence |
| `unusual_locations` | Location Intelligence |
| `location_transitions` | Location Intelligence |
| `time_at_locations` | Location Intelligence |
| `location_at_specific_time` | Location Intelligence, Alibi & Incident |
| `locations_in_time_range` | Location Intelligence, Alibi & Incident |
| `antenna_overlap` | Co-Location Analysis |
| `travel_pattern_match` | Co-Location Analysis |
| `meeting_detection` | Co-Location Analysis |
| `multi_user_colocation` | Group Coordination |
| `synchronized_silence` | Group Coordination |
| `group_locations_at_time` | Group Coordination, Alibi & Incident |
| `proximity_to_location` | Group Coordination, Location Intelligence |
| `build_communication_matrix` | Network Structure |
| `degree_centrality` | Network Structure |
| `communication_chains` | Network Structure |
| `shared_contacts` | Network Structure |
| `communication_volume_matrix` | Network Structure |
| `network_timeline` | Network Structure |
| `identify_bridges` | Network Structure |

---

## Appendix B: Color Scheme Recommendations

### Primary Palette (Investigation Context)

| Purpose | Color | Hex |
|---------|-------|-----|
| Primary (links, actions) | Blue | `#2563eb` |
| High confidence/positive | Green | `#16a34a` |
| Medium confidence/warning | Amber | `#d97706` |
| Low confidence/danger | Red | `#dc2626` |
| Neutral background | Gray | `#f3f4f6` |
| Text | Dark gray | `#1f2937` |

### Suspicion Score Gradient

```css
.suspicion-high   { background: #dc2626; } /* 0.7-1.0 */
.suspicion-medium { background: #d97706; } /* 0.4-0.7 */
.suspicion-low    { background: #16a34a; } /* 0.0-0.4 */
```

---

*Plan created January 2026*
*For: Bandicoot MCP Plugin - Investigation Dashboard Visualization*
