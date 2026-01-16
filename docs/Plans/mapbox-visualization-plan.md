# Bandicoot Mapbox GL JS Visualization

## The Crown Jewel of Mobile Metadata Analysis

---

# Executive Summary

This document outlines the complete implementation plan for an extraordinary Mapbox GL JS visualization system that transforms raw phone metadata into a stunning, interactive temporal-spatial experience. This is not just a map with markers -- this is a premium, cinematic data exploration tool that will set Bandicoot apart from any mobile analysis tool ever created.

**What We're Building:**
A full-viewport, real-time animated visualization that brings phone call and text message patterns to life on a beautiful map. Users will watch their data unfold through time with a precision world clock ticker, explore clustered antenna locations that reveal their density as they zoom, and interact with floating glassmorphic control panels that feel like they're crafted from crystal and light.

**Why It Will Be Amazing:**
- **Immersive Full-Screen Experience**: Every pixel dedicated to the visualization
- **Temporal Animation System**: Watch patterns emerge as time flows through the data
- **Premium Glassmorphic UI**: Floating controls that look like they belong in a sci-fi film
- **Intelligent Clustering**: Antenna markers that dynamically aggregate based on zoom level
- **Dual Theme System**: Stunning dark and light modes, both equally polished
- **Zero Dependencies Build**: Pure ES6 modules with CDN delivery -- just works

---

# Architecture Overview

## System Architecture Diagram

```
+------------------------------------------------------------------+
|                      BANDICOOT VISUALIZER                         |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------------+     +---------------------------+      |
|  |     EVENT BUS          |<--->|    STATE MANAGER          |      |
|  |  (Pub/Sub System)      |     |  (Single Source of Truth) |      |
|  +------------------------+     +---------------------------+      |
|           ^                              ^                         |
|           |                              |                         |
|           v                              v                         |
|  +------------------+  +------------------+  +------------------+  |
|  | MAP CONTROLLER   |  | TIME CONTROLLER  |  | THEME CONTROLLER |  |
|  | - Mapbox GL JS   |  | - Animation Loop |  | - Dark/Light     |  |
|  | - Layers         |  | - World Clock    |  | - CSS Variables  |  |
|  | - Clusters       |  | - Playback       |  | - Transitions    |  |
|  | - Popups         |  | - Range Filters  |  +------------------+  |
|  +------------------+  +------------------+                        |
|           ^                    ^                                   |
|           |                    |                                   |
|           v                    v                                   |
|  +------------------+  +------------------+  +------------------+  |
|  | DATA LAYER       |  | UI COMPONENTS    |  | GEOJSON LOADER   |  |
|  | - GeoJSON Source |  | - Time Slider    |  | - File Input     |  |
|  | - Clustering     |  | - Controls Panel |  | - Validation     |  |
|  | - Filtering      |  | - Clock Display  |  | - Transform      |  |
|  +------------------+  +------------------+  +------------------+  |
|                                                                    |
+------------------------------------------------------------------+
```

## Pub/Sub Event Bus

The entire system communicates through a central event bus, ensuring loose coupling and maximum flexibility.

### Core Events

| Event Name | Publisher | Subscribers | Payload |
|------------|-----------|-------------|---------|
| `time:change` | TimeController | MapController, ClockDisplay | `{ timestamp, formatted }` |
| `time:play` | PlaybackControls | TimeController | `{ speed }` |
| `time:pause` | PlaybackControls | TimeController | `{}` |
| `time:seek` | TimeSlider | TimeController | `{ timestamp }` |
| `time:range` | RangeSelector | TimeController, MapController | `{ start, end }` |
| `map:ready` | MapController | All | `{ bounds, center }` |
| `map:click` | MapController | PopupManager | `{ feature, lngLat }` |
| `map:zoom` | MapController | ClusterManager | `{ zoom }` |
| `theme:change` | ThemePicker | All | `{ theme: 'dark' \| 'light' }` |
| `data:loaded` | GeoJSONLoader | MapController, TimeController | `{ features, timeRange }` |
| `cluster:expand` | MapController | PopupManager | `{ clusterId, features }` |

### Event Bus Implementation

```javascript
// core/EventBus.js
export class EventBus {
  #subscribers = new Map();
  #history = [];
  #maxHistory = 100;

  subscribe(event, callback, options = {}) {
    if (!this.#subscribers.has(event)) {
      this.#subscribers.set(event, new Set());
    }

    const subscription = { callback, once: options.once || false };
    this.#subscribers.get(event).add(subscription);

    // Return unsubscribe function
    return () => {
      this.#subscribers.get(event)?.delete(subscription);
    };
  }

  publish(event, payload = {}) {
    const timestamp = performance.now();
    this.#history.push({ event, payload, timestamp });

    if (this.#history.length > this.#maxHistory) {
      this.#history.shift();
    }

    const subscribers = this.#subscribers.get(event);
    if (!subscribers) return;

    subscribers.forEach(sub => {
      try {
        sub.callback(payload);
        if (sub.once) subscribers.delete(sub);
      } catch (error) {
        console.error(`EventBus error in ${event}:`, error);
      }
    });
  }

  once(event, callback) {
    return this.subscribe(event, callback, { once: true });
  }
}

export const eventBus = new EventBus();
```

## State Management

```javascript
// core/StateManager.js
export class StateManager {
  #state = {
    theme: 'dark',
    time: {
      current: null,
      start: null,
      end: null,
      isPlaying: false,
      speed: 1,
    },
    map: {
      center: [0, 0],
      zoom: 2,
      bounds: null,
    },
    data: {
      loaded: false,
      features: [],
      antennas: new Map(),
    },
    ui: {
      activePopup: null,
      expandedCluster: null,
    }
  };

  #listeners = new Set();

  getState(path) {
    return path ? this.#getNestedValue(this.#state, path) : { ...this.#state };
  }

  setState(path, value) {
    this.#setNestedValue(this.#state, path, value);
    this.#notifyListeners(path);
  }

  subscribe(callback) {
    this.#listeners.add(callback);
    return () => this.#listeners.delete(callback);
  }

  #getNestedValue(obj, path) {
    return path.split('.').reduce((acc, key) => acc?.[key], obj);
  }

  #setNestedValue(obj, path, value) {
    const keys = path.split('.');
    const lastKey = keys.pop();
    const target = keys.reduce((acc, key) => acc[key], obj);
    target[lastKey] = value;
  }

  #notifyListeners(path) {
    this.#listeners.forEach(cb => cb(path, this.#state));
  }
}

export const state = new StateManager();
```

---

# Phase Breakdown

## Phase 1: Foundation (Days 1-2)

### Objectives
- Project scaffolding with ES6 module structure
- Core infrastructure (EventBus, StateManager)
- Basic Mapbox GL JS integration
- Theme system with CSS custom properties

### Deliverables

1. **Project Structure** (see File Structure section)
2. **EventBus Module** - Complete pub/sub implementation
3. **StateManager Module** - Centralized state with subscriptions
4. **Theme System** - Dark/light mode with smooth transitions
5. **Base HTML Template** - Full viewport layout with glassmorphic panels
6. **Map Initialization** - Mapbox GL JS with both map styles

### Success Criteria
- [ ] Map loads full viewport with no scrollbars
- [ ] Theme toggle switches between dark and light modes smoothly
- [ ] EventBus successfully passes messages between modules
- [ ] Console shows no errors

---

## Phase 2: Data Layer (Days 3-4)

### Objectives
- GeoJSON data loading and validation
- Clustered source configuration
- Time-based filtering system
- Antenna marker layer with clustering

### Deliverables

1. **GeoJSONLoader Module**
   - File input handling
   - Schema validation
   - Time range extraction
   - Feature preprocessing

2. **ClusterManager Module**
   - Supercluster integration via Mapbox
   - Zoom-responsive clustering
   - Cluster expansion on click
   - Custom cluster styling

3. **FilterEngine Module**
   - Time-based filtering expressions
   - Event type filtering (call/text)
   - Direction filtering (in/out)
   - Combined filter expressions

### Data Schema

```javascript
// Expected GeoJSON Feature Properties
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [longitude, latitude]
  },
  "properties": {
    "antenna_id": "string",
    "datetime": "ISO8601 string",
    "timestamp": "number (unix ms)",
    "interaction_type": "call" | "text",
    "direction": "in" | "out",
    "duration": "number (seconds, calls only)",
    "contact_hash": "string (anonymized)",
    "event_count": "number (for clusters)"
  }
}
```

### Success Criteria
- [ ] GeoJSON loads and validates correctly
- [ ] Markers appear clustered on map
- [ ] Clusters expand when clicked
- [ ] Filtering by time range works
- [ ] Individual markers show correct properties

---

## Phase 3: Time System (Days 5-7)

### Objectives
- Time slider with range selection
- World clock ticker display
- Animation playback system
- Day/week/month quick selectors

### Deliverables

1. **TimeController Module**
   - Animation loop with requestAnimationFrame
   - Playback speed control (0.5x, 1x, 2x, 5x, 10x)
   - Pause/resume functionality
   - Time seeking

2. **TimeSlider Component**
   - Custom range slider with dual handles
   - Visual event density overlay
   - Scrubbing with preview
   - Touch-friendly interaction

3. **WorldClock Component**
   - Digital clock display
   - Animated digit transitions
   - Date display with day name
   - Timezone indicator

4. **QuickSelectors Component**
   - Day/Week/Month buttons
   - Date picker integration
   - Range presets

### Animation Loop

```javascript
// controllers/TimeController.js
export class TimeController {
  #animationId = null;
  #lastFrameTime = 0;
  #accumulatedTime = 0;
  #msPerTick = 100; // How many real ms per data second

  constructor(eventBus, state) {
    this.eventBus = eventBus;
    this.state = state;
    this.#bindEvents();
  }

  #bindEvents() {
    this.eventBus.subscribe('time:play', ({ speed }) => this.play(speed));
    this.eventBus.subscribe('time:pause', () => this.pause());
    this.eventBus.subscribe('time:seek', ({ timestamp }) => this.seek(timestamp));
  }

  play(speed = 1) {
    this.state.setState('time.isPlaying', true);
    this.state.setState('time.speed', speed);
    this.#lastFrameTime = performance.now();
    this.#animate();
  }

  pause() {
    this.state.setState('time.isPlaying', false);
    if (this.#animationId) {
      cancelAnimationFrame(this.#animationId);
      this.#animationId = null;
    }
  }

  seek(timestamp) {
    this.state.setState('time.current', timestamp);
    this.eventBus.publish('time:change', {
      timestamp,
      formatted: this.#formatTime(timestamp)
    });
  }

  #animate = (currentTime) => {
    if (!this.state.getState('time.isPlaying')) return;

    const delta = currentTime - this.#lastFrameTime;
    this.#lastFrameTime = currentTime;

    const speed = this.state.getState('time.speed');
    this.#accumulatedTime += delta * speed;

    if (this.#accumulatedTime >= this.#msPerTick) {
      const ticksElapsed = Math.floor(this.#accumulatedTime / this.#msPerTick);
      this.#accumulatedTime %= this.#msPerTick;

      const current = this.state.getState('time.current');
      const end = this.state.getState('time.end');
      const newTime = current + (ticksElapsed * 1000); // Add seconds

      if (newTime >= end) {
        this.pause();
        this.seek(end);
      } else {
        this.seek(newTime);
      }
    }

    this.#animationId = requestAnimationFrame(this.#animate);
  };

  #formatTime(timestamp) {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }),
      time: date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };
  }
}
```

### Success Criteria
- [ ] Time slider shows full data range
- [ ] Play/pause controls work smoothly
- [ ] World clock animates with time changes
- [ ] Speed controls affect playback rate
- [ ] Map filters update in sync with time
- [ ] Quick selectors set appropriate ranges

---

## Phase 4: Interactive Popups (Days 8-9)

### Objectives
- Rich popup design with glassmorphic styling
- Cluster expansion popup
- Individual event detail popup
- Event aggregation views

### Deliverables

1. **PopupManager Module**
   - Popup lifecycle management
   - Position calculations
   - Animation handling
   - Click-away dismissal

2. **ClusterPopup Component**
   - Donut chart showing event types
   - List of top contacts
   - Time range summary
   - "Zoom to expand" action

3. **EventPopup Component**
   - Event type icon
   - Full datetime display
   - Duration (for calls)
   - Direction indicator
   - Contact hash

4. **Popup Animations**
   - Scale-up entrance
   - Fade transitions
   - Pointer/arrow positioning

### Success Criteria
- [ ] Clicking cluster shows cluster popup
- [ ] Clicking individual marker shows event popup
- [ ] Popups close when clicking elsewhere
- [ ] Popups animate smoothly
- [ ] Popups reposition correctly on map movement

---

## Phase 5: Polish & Performance (Days 10-12)

### Objectives
- Performance optimization
- Animation refinement
- Accessibility improvements
- Final visual polish

### Deliverables

1. **Performance Optimization**
   - Debounced filter updates
   - Efficient cluster calculations
   - Lazy popup rendering
   - Memory leak prevention

2. **Animation Polish**
   - Micro-interactions on controls
   - Smooth theme transitions
   - Loading states
   - Error states

3. **Accessibility**
   - Keyboard navigation
   - ARIA labels
   - Focus management
   - Screen reader support

4. **Visual Polish**
   - Hover states
   - Active states
   - Disabled states
   - Loading spinners

### Success Criteria
- [ ] 60fps animations maintained
- [ ] No memory leaks during extended use
- [ ] Keyboard fully navigable
- [ ] WCAG 2.1 AA compliance for contrast
- [ ] All interactive elements have hover/focus states

---

# File Structure

```
bandicoot-visualizer/
├── index.html                    # Main entry point
├── styles/
│   ├── main.css                  # Core styles and CSS custom properties
│   ├── components/
│   │   ├── map.css               # Map container styles
│   │   ├── time-slider.css       # Time slider component
│   │   ├── world-clock.css       # Clock display styles
│   │   ├── controls.css          # Control panel styles
│   │   ├── popups.css            # Popup styling
│   │   └── theme-picker.css      # Theme toggle styles
│   ├── themes/
│   │   ├── dark.css              # Dark theme overrides
│   │   └── light.css             # Light theme overrides
│   └── animations.css            # Keyframe animations
├── js/
│   ├── main.js                   # Application entry point
│   ├── core/
│   │   ├── EventBus.js           # Pub/Sub implementation
│   │   ├── StateManager.js       # State management
│   │   └── constants.js          # App-wide constants
│   ├── controllers/
│   │   ├── MapController.js      # Mapbox GL JS wrapper
│   │   ├── TimeController.js     # Time/animation logic
│   │   └── ThemeController.js    # Theme switching
│   ├── components/
│   │   ├── TimeSlider.js         # Time slider UI
│   │   ├── WorldClock.js         # Clock display
│   │   ├── PlaybackControls.js   # Play/pause/speed
│   │   ├── RangeSelector.js      # Day/week/month
│   │   ├── ThemePicker.js        # Dark/light toggle
│   │   ├── PopupManager.js       # Popup handling
│   │   ├── ClusterPopup.js       # Cluster popup content
│   │   └── EventPopup.js         # Event popup content
│   ├── data/
│   │   ├── GeoJSONLoader.js      # Data loading
│   │   ├── ClusterManager.js     # Clustering logic
│   │   └── FilterEngine.js       # Filtering logic
│   └── utils/
│       ├── formatters.js         # Date/number formatting
│       ├── validators.js         # Schema validation
│       └── dom.js                # DOM utilities
├── assets/
│   ├── icons/
│   │   ├── call-incoming.svg
│   │   ├── call-outgoing.svg
│   │   ├── text-incoming.svg
│   │   ├── text-outgoing.svg
│   │   ├── play.svg
│   │   ├── pause.svg
│   │   ├── sun.svg
│   │   └── moon.svg
│   └── fonts/
│       └── (loaded from CDN)
└── data/
    └── sample.geojson            # Sample data for testing
```

---

# Component Specifications

## 1. Map Container

**Purpose**: Full viewport Mapbox GL JS map with data layers

**HTML Structure**:
```html
<div id="map-container" class="map-container">
  <div id="map" class="map"></div>
  <div class="map-overlay map-overlay--top-left">
    <!-- Theme picker, zoom controls -->
  </div>
  <div class="map-overlay map-overlay--bottom">
    <!-- Time slider, clock, controls -->
  </div>
</div>
```

**Map Configuration**:
```javascript
const mapConfig = {
  container: 'map',
  style: 'mapbox://styles/mapbox/dark-v11', // or light-v11
  center: [0, 0],
  zoom: 2,
  minZoom: 1,
  maxZoom: 18,
  attributionControl: false, // Custom attribution
  pitchWithRotate: false,
  dragRotate: false
};
```

---

## 2. Time Slider

**Purpose**: Visual timeline with range selection and event density

**Features**:
- Dual-handle range slider for start/end selection
- Single handle for current time during playback
- Event density visualization as background gradient
- Scrubbing with time preview tooltip

**HTML Structure**:
```html
<div class="time-slider">
  <div class="time-slider__track">
    <div class="time-slider__density"></div>
    <div class="time-slider__range"></div>
    <div class="time-slider__progress"></div>
  </div>
  <div class="time-slider__handles">
    <div class="time-slider__handle time-slider__handle--start" role="slider"></div>
    <div class="time-slider__handle time-slider__handle--current" role="slider"></div>
    <div class="time-slider__handle time-slider__handle--end" role="slider"></div>
  </div>
  <div class="time-slider__tooltip"></div>
  <div class="time-slider__labels">
    <span class="time-slider__label time-slider__label--start"></span>
    <span class="time-slider__label time-slider__label--end"></span>
  </div>
</div>
```

**Dimensions**:
- Width: 100% of control panel (max 800px)
- Height: 48px (track 8px, handles 24px)
- Handle width: 16px

---

## 3. World Clock Display

**Purpose**: Animated digital clock showing current data time

**Features**:
- Seven-segment inspired digital display
- Flip animation on digit changes
- Date with day name
- Timezone indicator

**HTML Structure**:
```html
<div class="world-clock">
  <div class="world-clock__date">
    <span class="world-clock__day">Wed</span>
    <span class="world-clock__month-day">Jan 15, 2025</span>
  </div>
  <div class="world-clock__time">
    <div class="world-clock__digit" data-digit="hour-tens">1</div>
    <div class="world-clock__digit" data-digit="hour-ones">4</div>
    <span class="world-clock__colon">:</span>
    <div class="world-clock__digit" data-digit="min-tens">3</div>
    <div class="world-clock__digit" data-digit="min-ones">0</div>
    <span class="world-clock__colon">:</span>
    <div class="world-clock__digit" data-digit="sec-tens">4</div>
    <div class="world-clock__digit" data-digit="sec-ones">5</div>
  </div>
  <div class="world-clock__timezone">UTC+0</div>
</div>
```

**Typography**:
- Time digits: JetBrains Mono, 48px, monospace
- Date: Inter, 14px
- Timezone: Inter, 12px, muted

---

## 4. Playback Controls

**Purpose**: Play/pause, speed selection, step controls

**Features**:
- Large play/pause toggle button
- Speed selector (0.5x, 1x, 2x, 5x, 10x)
- Step forward/backward buttons
- Visual feedback on state changes

**HTML Structure**:
```html
<div class="playback-controls">
  <button class="playback-controls__step playback-controls__step--back" aria-label="Step backward">
    <svg><!-- Step back icon --></svg>
  </button>
  <button class="playback-controls__play-pause" aria-label="Play" aria-pressed="false">
    <svg class="playback-controls__icon playback-controls__icon--play"><!-- Play icon --></svg>
    <svg class="playback-controls__icon playback-controls__icon--pause"><!-- Pause icon --></svg>
  </button>
  <button class="playback-controls__step playback-controls__step--forward" aria-label="Step forward">
    <svg><!-- Step forward icon --></svg>
  </button>
  <div class="playback-controls__speed">
    <button class="playback-controls__speed-btn" data-speed="0.5">0.5x</button>
    <button class="playback-controls__speed-btn" data-speed="1" aria-pressed="true">1x</button>
    <button class="playback-controls__speed-btn" data-speed="2">2x</button>
    <button class="playback-controls__speed-btn" data-speed="5">5x</button>
    <button class="playback-controls__speed-btn" data-speed="10">10x</button>
  </div>
</div>
```

---

## 5. Range Selector

**Purpose**: Quick date range selection

**Features**:
- Day/Week/Month preset buttons
- Custom date picker
- Visual indication of active range

**HTML Structure**:
```html
<div class="range-selector">
  <div class="range-selector__presets">
    <button class="range-selector__preset" data-range="day">Day</button>
    <button class="range-selector__preset" data-range="week">Week</button>
    <button class="range-selector__preset" data-range="month">Month</button>
    <button class="range-selector__preset" data-range="all" aria-pressed="true">All</button>
  </div>
  <div class="range-selector__custom">
    <input type="datetime-local" class="range-selector__input" id="range-start">
    <span class="range-selector__separator">to</span>
    <input type="datetime-local" class="range-selector__input" id="range-end">
  </div>
</div>
```

---

## 6. Theme Picker

**Purpose**: Toggle between dark and light themes

**Features**:
- Smooth icon morph animation
- System preference detection
- Persistent preference (localStorage)

**HTML Structure**:
```html
<button class="theme-picker" aria-label="Toggle theme" data-theme="dark">
  <div class="theme-picker__icon-container">
    <svg class="theme-picker__icon theme-picker__icon--sun"><!-- Sun --></svg>
    <svg class="theme-picker__icon theme-picker__icon--moon"><!-- Moon --></svg>
  </div>
</button>
```

---

## 7. Event Popup

**Purpose**: Display details for individual events

**Features**:
- Event type with icon
- Full datetime
- Duration for calls
- Direction indicator
- Contact identifier

**HTML Structure**:
```html
<div class="event-popup glass-panel">
  <div class="event-popup__header">
    <div class="event-popup__icon event-popup__icon--call-in">
      <svg><!-- Icon --></svg>
    </div>
    <div class="event-popup__type">Incoming Call</div>
  </div>
  <div class="event-popup__body">
    <div class="event-popup__row">
      <span class="event-popup__label">Time</span>
      <span class="event-popup__value">Jan 15, 2025 14:30:45</span>
    </div>
    <div class="event-popup__row">
      <span class="event-popup__label">Duration</span>
      <span class="event-popup__value">3m 42s</span>
    </div>
    <div class="event-popup__row">
      <span class="event-popup__label">Contact</span>
      <span class="event-popup__value event-popup__value--mono">a7b3c9d2</span>
    </div>
  </div>
  <div class="event-popup__antenna">
    <span class="event-popup__antenna-icon">📡</span>
    <span class="event-popup__antenna-id">ANT-00142</span>
  </div>
</div>
```

---

## 8. Cluster Popup

**Purpose**: Display aggregated data for clustered markers

**Features**:
- Event count with breakdown
- Mini donut chart
- Time range of events
- Zoom action button

**HTML Structure**:
```html
<div class="cluster-popup glass-panel">
  <div class="cluster-popup__header">
    <div class="cluster-popup__count">247 Events</div>
    <div class="cluster-popup__range">Jan 12-18, 2025</div>
  </div>
  <div class="cluster-popup__chart">
    <svg class="cluster-popup__donut">
      <!-- Donut chart segments -->
    </svg>
    <div class="cluster-popup__legend">
      <div class="cluster-popup__legend-item">
        <span class="cluster-popup__legend-color" style="--color: var(--color-call-in)"></span>
        <span>Calls In (89)</span>
      </div>
      <div class="cluster-popup__legend-item">
        <span class="cluster-popup__legend-color" style="--color: var(--color-call-out)"></span>
        <span>Calls Out (62)</span>
      </div>
      <div class="cluster-popup__legend-item">
        <span class="cluster-popup__legend-color" style="--color: var(--color-text-in)"></span>
        <span>Texts In (51)</span>
      </div>
      <div class="cluster-popup__legend-item">
        <span class="cluster-popup__legend-color" style="--color: var(--color-text-out)"></span>
        <span>Texts Out (45)</span>
      </div>
    </div>
  </div>
  <button class="cluster-popup__action">
    <svg><!-- Zoom icon --></svg>
    Zoom to Expand
  </button>
</div>
```

---

# Styling Guide

## Glassmorphic Design System

### Core Principles

1. **Transparency**: Semi-transparent backgrounds (10-25% opacity)
2. **Blur**: Backdrop blur (8-20px depending on element)
3. **Borders**: Subtle light borders (1px, 10-20% white)
4. **Shadows**: Soft, layered shadows for depth
5. **Light Edges**: Top/left highlights for that 3D glass effect

### Base Glass Panel CSS

```css
.glass-panel {
  /* Transparency */
  background: var(--glass-bg);

  /* Blur Effect */
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));

  /* Borders */
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);

  /* Shadows */
  box-shadow:
    0 8px 32px var(--glass-shadow),
    inset 0 1px 0 var(--glass-highlight);

  /* Transitions */
  transition:
    background-color 0.3s ease,
    box-shadow 0.3s ease,
    transform 0.2s ease;
}

.glass-panel:hover {
  box-shadow:
    0 12px 40px var(--glass-shadow-hover),
    inset 0 1px 0 var(--glass-highlight);
  transform: translateY(-2px);
}
```

## Color Palettes

### Dark Theme

```css
:root[data-theme="dark"] {
  /* Base Colors */
  --color-bg-primary: #0a0a0f;
  --color-bg-secondary: #12121a;
  --color-bg-elevated: #1a1a24;

  /* Text Colors */
  --color-text-primary: #ffffff;
  --color-text-secondary: #a0a0b0;
  --color-text-muted: #606070;

  /* Accent Colors */
  --color-accent-primary: #6366f1;    /* Indigo */
  --color-accent-secondary: #8b5cf6;  /* Purple */
  --color-accent-glow: rgba(99, 102, 241, 0.4);

  /* Event Type Colors */
  --color-call-in: #22c55e;           /* Green */
  --color-call-out: #3b82f6;          /* Blue */
  --color-text-in: #f59e0b;           /* Amber */
  --color-text-out: #ec4899;          /* Pink */

  /* Glass Properties */
  --glass-bg: rgba(18, 18, 26, 0.75);
  --glass-blur: 16px;
  --glass-border: rgba(255, 255, 255, 0.08);
  --glass-shadow: rgba(0, 0, 0, 0.5);
  --glass-shadow-hover: rgba(0, 0, 0, 0.6);
  --glass-highlight: rgba(255, 255, 255, 0.05);

  /* Map Style */
  --map-style: mapbox://styles/mapbox/dark-v11;

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  --gradient-glow: radial-gradient(circle at center, var(--color-accent-glow) 0%, transparent 70%);
}
```

### Light Theme

```css
:root[data-theme="light"] {
  /* Base Colors */
  --color-bg-primary: #f8fafc;
  --color-bg-secondary: #ffffff;
  --color-bg-elevated: #ffffff;

  /* Text Colors */
  --color-text-primary: #0f172a;
  --color-text-secondary: #475569;
  --color-text-muted: #94a3b8;

  /* Accent Colors */
  --color-accent-primary: #4f46e5;    /* Indigo */
  --color-accent-secondary: #7c3aed;  /* Purple */
  --color-accent-glow: rgba(79, 70, 229, 0.2);

  /* Event Type Colors */
  --color-call-in: #16a34a;           /* Green */
  --color-call-out: #2563eb;          /* Blue */
  --color-text-in: #d97706;           /* Amber */
  --color-text-out: #db2777;          /* Pink */

  /* Glass Properties */
  --glass-bg: rgba(255, 255, 255, 0.85);
  --glass-blur: 12px;
  --glass-border: rgba(0, 0, 0, 0.06);
  --glass-shadow: rgba(0, 0, 0, 0.08);
  --glass-shadow-hover: rgba(0, 0, 0, 0.12);
  --glass-highlight: rgba(255, 255, 255, 0.8);

  /* Map Style */
  --map-style: mapbox://styles/mapbox/light-v11;

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  --gradient-glow: radial-gradient(circle at center, var(--color-accent-glow) 0%, transparent 70%);
}
```

### Shared Properties

```css
:root {
  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --font-display: 'Space Grotesk', var(--font-sans);

  /* Font Sizes */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 2rem;
  --text-4xl: 2.5rem;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
  --radius-full: 9999px;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease;
  --transition-theme: 400ms ease;

  /* Z-Index Scale */
  --z-base: 0;
  --z-overlay: 100;
  --z-popup: 200;
  --z-controls: 300;
  --z-modal: 400;
  --z-toast: 500;
}
```

---

# Animation Specifications

## Animation Philosophy

Every animation serves a purpose: guide attention, provide feedback, or enhance understanding. No animation for animation's sake.

## Keyframe Definitions

```css
/* Fade In Up - For panels appearing */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale In - For popups */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Pulse Glow - For active elements */
@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 0 0 var(--color-accent-glow);
  }
  50% {
    box-shadow: 0 0 20px 4px var(--color-accent-glow);
  }
}

/* Digit Flip - For clock numbers */
@keyframes digitFlip {
  0% {
    transform: rotateX(0deg);
  }
  50% {
    transform: rotateX(-90deg);
  }
  100% {
    transform: rotateX(0deg);
  }
}

/* Slide In From Right - For controls */
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Shimmer - Loading state */
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* Ripple - Button click */
@keyframes ripple {
  to {
    transform: scale(4);
    opacity: 0;
  }
}

/* Marker Pulse - For active antenna */
@keyframes markerPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.5);
    opacity: 0.5;
  }
}
```

## Animation Timing

| Animation | Duration | Easing | Trigger |
|-----------|----------|--------|---------|
| Panel Enter | 300ms | cubic-bezier(0.16, 1, 0.3, 1) | On mount |
| Panel Exit | 200ms | ease-out | On unmount |
| Popup Open | 250ms | cubic-bezier(0.34, 1.56, 0.64, 1) | On click |
| Popup Close | 150ms | ease-in | On dismiss |
| Theme Switch | 400ms | ease-in-out | On toggle |
| Clock Digit | 200ms | ease-out | On change |
| Button Hover | 150ms | ease | On hover |
| Button Active | 50ms | ease | On click |
| Slider Handle | 100ms | ease | On drag |
| Progress Bar | 60fps | linear | Continuous |

## Staggered Animations

For multiple elements entering together:

```css
.control-panel > * {
  animation: fadeInUp 300ms cubic-bezier(0.16, 1, 0.3, 1) backwards;
}

.control-panel > *:nth-child(1) { animation-delay: 0ms; }
.control-panel > *:nth-child(2) { animation-delay: 50ms; }
.control-panel > *:nth-child(3) { animation-delay: 100ms; }
.control-panel > *:nth-child(4) { animation-delay: 150ms; }
```

## Micro-Interactions

### Button Press Effect

```css
.btn {
  position: relative;
  overflow: hidden;
  transform: translateZ(0); /* GPU acceleration */
}

.btn::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at var(--x) var(--y),
    rgba(255,255,255,0.3) 0%,
    transparent 60%);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.btn:active::after {
  opacity: 1;
}
```

### Slider Handle Glow

```css
.time-slider__handle:focus-visible,
.time-slider__handle:active {
  box-shadow:
    0 0 0 4px var(--color-accent-glow),
    0 2px 8px rgba(0, 0, 0, 0.2);
}
```

---

# API Integration Details

## Mapbox GL JS Setup

### CDN Links

```html
<!-- Mapbox GL JS -->
<link href="https://api.mapbox.com/mapbox-gl-js/v3.3.0/mapbox-gl.css" rel="stylesheet">
<script src="https://api.mapbox.com/mapbox-gl-js/v3.3.0/mapbox-gl.js"></script>
```

### Map Initialization

```javascript
// controllers/MapController.js
export class MapController {
  #map = null;
  #sources = new Map();
  #layers = new Map();

  constructor(eventBus, state, accessToken) {
    this.eventBus = eventBus;
    this.state = state;
    mapboxgl.accessToken = accessToken;
  }

  async initialize(container, options = {}) {
    const theme = this.state.getState('theme');

    this.#map = new mapboxgl.Map({
      container,
      style: theme === 'dark'
        ? 'mapbox://styles/mapbox/dark-v11'
        : 'mapbox://styles/mapbox/light-v11',
      center: options.center || [0, 0],
      zoom: options.zoom || 2,
      minZoom: 1,
      maxZoom: 18,
      attributionControl: false,
      pitchWithRotate: false,
      dragRotate: false,
      ...options
    });

    // Add custom attribution
    this.#map.addControl(
      new mapboxgl.AttributionControl({ compact: true }),
      'bottom-right'
    );

    // Add navigation control
    this.#map.addControl(
      new mapboxgl.NavigationControl({ showCompass: false }),
      'top-right'
    );

    return new Promise((resolve) => {
      this.#map.on('load', () => {
        this.eventBus.publish('map:ready', {
          bounds: this.#map.getBounds(),
          center: this.#map.getCenter()
        });
        resolve(this.#map);
      });
    });
  }

  setStyle(style) {
    const currentStyle = this.#map.getStyle();

    this.#map.setStyle(style);

    // Re-add custom sources and layers after style change
    this.#map.once('style.load', () => {
      this.#sources.forEach((data, id) => {
        if (!this.#map.getSource(id)) {
          this.#map.addSource(id, data);
        }
      });

      this.#layers.forEach((config, id) => {
        if (!this.#map.getLayer(id)) {
          this.#map.addLayer(config);
        }
      });
    });
  }

  addSource(id, config) {
    this.#sources.set(id, config);
    this.#map.addSource(id, config);
  }

  addLayer(config) {
    this.#layers.set(config.id, config);
    this.#map.addLayer(config);
  }

  get map() {
    return this.#map;
  }
}
```

### Cluster Layer Configuration

```javascript
// Add clustered GeoJSON source
map.addSource('phone-events', {
  type: 'geojson',
  data: geojsonData,
  cluster: true,
  clusterMaxZoom: 14,
  clusterRadius: 50,
  clusterProperties: {
    // Aggregate counts by type
    call_in_count: ['+', ['case',
      ['all',
        ['==', ['get', 'interaction_type'], 'call'],
        ['==', ['get', 'direction'], 'in']
      ], 1, 0]],
    call_out_count: ['+', ['case',
      ['all',
        ['==', ['get', 'interaction_type'], 'call'],
        ['==', ['get', 'direction'], 'out']
      ], 1, 0]],
    text_in_count: ['+', ['case',
      ['all',
        ['==', ['get', 'interaction_type'], 'text'],
        ['==', ['get', 'direction'], 'in']
      ], 1, 0]],
    text_out_count: ['+', ['case',
      ['all',
        ['==', ['get', 'interaction_type'], 'text'],
        ['==', ['get', 'direction'], 'out']
      ], 1, 0]],
    // Time range
    min_time: ['min', ['get', 'timestamp']],
    max_time: ['max', ['get', 'timestamp']]
  }
});

// Cluster circles layer
map.addLayer({
  id: 'clusters',
  type: 'circle',
  source: 'phone-events',
  filter: ['has', 'point_count'],
  paint: {
    'circle-color': [
      'step',
      ['get', 'point_count'],
      '#6366f1',  // < 10
      10, '#8b5cf6',  // 10-50
      50, '#a855f7',  // 50-100
      100, '#c084fc', // 100-500
      500, '#e879f9'  // > 500
    ],
    'circle-radius': [
      'step',
      ['get', 'point_count'],
      20,   // < 10
      10, 30,   // 10-50
      50, 40,   // 50-100
      100, 50,  // 100-500
      500, 60   // > 500
    ],
    'circle-stroke-width': 2,
    'circle-stroke-color': 'rgba(255, 255, 255, 0.3)'
  }
});

// Cluster count labels
map.addLayer({
  id: 'cluster-count',
  type: 'symbol',
  source: 'phone-events',
  filter: ['has', 'point_count'],
  layout: {
    'text-field': ['get', 'point_count_abbreviated'],
    'text-font': ['DIN Pro Medium', 'Arial Unicode MS Bold'],
    'text-size': 14
  },
  paint: {
    'text-color': '#ffffff'
  }
});

// Individual event markers
map.addLayer({
  id: 'unclustered-point',
  type: 'circle',
  source: 'phone-events',
  filter: ['!', ['has', 'point_count']],
  paint: {
    'circle-radius': 8,
    'circle-color': [
      'match',
      ['concat', ['get', 'interaction_type'], '-', ['get', 'direction']],
      'call-in', '#22c55e',
      'call-out', '#3b82f6',
      'text-in', '#f59e0b',
      'text-out', '#ec4899',
      '#6366f1' // fallback
    ],
    'circle-stroke-width': 2,
    'circle-stroke-color': 'rgba(255, 255, 255, 0.5)'
  }
});
```

---

# Time Slider Implementation

## Architecture

The time slider is a complex component with multiple responsibilities:

1. **Range Display**: Show the full data time range
2. **Selection Handles**: Start/end range selection
3. **Current Time Indicator**: Shows playback position
4. **Density Visualization**: Background showing event distribution
5. **Interactive Scrubbing**: Click/drag to seek

## Data Structure

```javascript
// Time slider internal state
const sliderState = {
  // Full data range
  dataStart: 1704067200000,  // Unix timestamp
  dataEnd: 1704672000000,

  // Selected range
  rangeStart: 1704067200000,
  rangeEnd: 1704672000000,

  // Current playback position
  current: 1704067200000,

  // Event density buckets (for visualization)
  density: [
    { time: 1704067200000, count: 5 },
    { time: 1704070800000, count: 12 },
    // ... hourly buckets
  ],

  // UI state
  dragging: null,  // 'start' | 'end' | 'current' | null
  hovering: false
};
```

## Component Implementation

```javascript
// components/TimeSlider.js
export class TimeSlider {
  #element = null;
  #state = null;
  #eventBus = null;
  #handles = {};
  #track = null;
  #progress = null;
  #density = null;
  #tooltip = null;

  constructor(container, eventBus, state) {
    this.#eventBus = eventBus;
    this.#state = state;
    this.#render(container);
    this.#bindEvents();
    this.#subscribeToEvents();
  }

  #render(container) {
    this.#element = document.createElement('div');
    this.#element.className = 'time-slider';
    this.#element.innerHTML = `
      <div class="time-slider__track">
        <div class="time-slider__density"></div>
        <div class="time-slider__range"></div>
        <div class="time-slider__progress"></div>
      </div>
      <div class="time-slider__handles">
        <div class="time-slider__handle time-slider__handle--start"
             role="slider"
             aria-label="Range start"
             tabindex="0"></div>
        <div class="time-slider__handle time-slider__handle--current"
             role="slider"
             aria-label="Current time"
             tabindex="0"></div>
        <div class="time-slider__handle time-slider__handle--end"
             role="slider"
             aria-label="Range end"
             tabindex="0"></div>
      </div>
      <div class="time-slider__tooltip"></div>
      <div class="time-slider__labels">
        <span class="time-slider__label time-slider__label--start"></span>
        <span class="time-slider__label time-slider__label--end"></span>
      </div>
    `;

    container.appendChild(this.#element);

    // Cache element references
    this.#track = this.#element.querySelector('.time-slider__track');
    this.#progress = this.#element.querySelector('.time-slider__progress');
    this.#density = this.#element.querySelector('.time-slider__density');
    this.#tooltip = this.#element.querySelector('.time-slider__tooltip');
    this.#handles = {
      start: this.#element.querySelector('.time-slider__handle--start'),
      current: this.#element.querySelector('.time-slider__handle--current'),
      end: this.#element.querySelector('.time-slider__handle--end')
    };
  }

  #bindEvents() {
    // Handle dragging
    Object.entries(this.#handles).forEach(([key, handle]) => {
      handle.addEventListener('mousedown', (e) => this.#startDrag(key, e));
      handle.addEventListener('touchstart', (e) => this.#startDrag(key, e));
    });

    // Track click to seek
    this.#track.addEventListener('click', (e) => this.#handleTrackClick(e));

    // Global mouse events for dragging
    document.addEventListener('mousemove', (e) => this.#handleDrag(e));
    document.addEventListener('mouseup', () => this.#endDrag());
    document.addEventListener('touchmove', (e) => this.#handleDrag(e));
    document.addEventListener('touchend', () => this.#endDrag());

    // Keyboard navigation
    Object.values(this.#handles).forEach(handle => {
      handle.addEventListener('keydown', (e) => this.#handleKeyboard(e));
    });
  }

  #subscribeToEvents() {
    this.#eventBus.subscribe('time:change', ({ timestamp }) => {
      this.#updateCurrent(timestamp);
    });

    this.#eventBus.subscribe('time:range', ({ start, end }) => {
      this.#updateRange(start, end);
    });

    this.#eventBus.subscribe('data:loaded', ({ timeRange, density }) => {
      this.#setDataRange(timeRange.start, timeRange.end);
      this.#renderDensity(density);
    });
  }

  #startDrag(handleKey, e) {
    e.preventDefault();
    this.#state.dragging = handleKey;
    this.#element.classList.add('time-slider--dragging');
    this.#handles[handleKey].classList.add('time-slider__handle--active');
  }

  #handleDrag(e) {
    if (!this.#state.dragging) return;

    const rect = this.#track.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const position = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));

    const time = this.#positionToTime(position);

    switch (this.#state.dragging) {
      case 'start':
        if (time < this.#state.rangeEnd) {
          this.#eventBus.publish('time:range', {
            start: time,
            end: this.#state.rangeEnd
          });
        }
        break;
      case 'end':
        if (time > this.#state.rangeStart) {
          this.#eventBus.publish('time:range', {
            start: this.#state.rangeStart,
            end: time
          });
        }
        break;
      case 'current':
        this.#eventBus.publish('time:seek', { timestamp: time });
        break;
    }

    this.#showTooltip(position, time);
  }

  #endDrag() {
    if (!this.#state.dragging) return;

    this.#handles[this.#state.dragging].classList.remove('time-slider__handle--active');
    this.#state.dragging = null;
    this.#element.classList.remove('time-slider--dragging');
    this.#hideTooltip();
  }

  #positionToTime(position) {
    const { dataStart, dataEnd } = this.#state;
    return dataStart + (dataEnd - dataStart) * position;
  }

  #timeToPosition(time) {
    const { dataStart, dataEnd } = this.#state;
    return (time - dataStart) / (dataEnd - dataStart);
  }

  #updateCurrent(timestamp) {
    const position = this.#timeToPosition(timestamp);
    this.#handles.current.style.left = `${position * 100}%`;
    this.#progress.style.width = `${position * 100}%`;
  }

  #renderDensity(densityData) {
    // Create gradient based on event density
    const maxCount = Math.max(...densityData.map(d => d.count));
    const stops = densityData.map((d, i) => {
      const position = i / (densityData.length - 1) * 100;
      const intensity = d.count / maxCount;
      const alpha = 0.1 + intensity * 0.4;
      return `rgba(99, 102, 241, ${alpha}) ${position}%`;
    });

    this.#density.style.background = `linear-gradient(to right, ${stops.join(', ')})`;
  }
}
```

## Density Visualization

The slider background shows event density over time:

```javascript
// Calculate hourly event density
function calculateDensity(features, bucketSize = 3600000) {
  const { min, max } = getTimeRange(features);
  const buckets = new Map();

  // Initialize buckets
  for (let t = min; t <= max; t += bucketSize) {
    buckets.set(t, 0);
  }

  // Count events per bucket
  features.forEach(feature => {
    const time = feature.properties.timestamp;
    const bucket = Math.floor(time / bucketSize) * bucketSize;
    buckets.set(bucket, (buckets.get(bucket) || 0) + 1);
  });

  return Array.from(buckets.entries())
    .map(([time, count]) => ({ time, count }))
    .sort((a, b) => a.time - b.time);
}
```

---

# Clustering Strategy

## Overview

Antenna clustering uses Mapbox GL JS's built-in Supercluster implementation for efficient spatial clustering that updates in real-time as users zoom and pan.

## Cluster Radius by Zoom Level

| Zoom Level | Cluster Radius (px) | Expected Behavior |
|------------|--------------------|--------------------|
| 0-4 | 80 | Large regional clusters |
| 5-8 | 60 | City-level clusters |
| 9-12 | 40 | Neighborhood clusters |
| 13-14 | 30 | Street-level clustering |
| 15+ | N/A | Individual markers |

## Dynamic Cluster Styling

```javascript
// Cluster size based on event count
'circle-radius': [
  'interpolate',
  ['linear'],
  ['get', 'point_count'],
  2, 20,     // 2 events = 20px
  10, 28,    // 10 events = 28px
  50, 36,    // 50 events = 36px
  100, 44,   // 100 events = 44px
  500, 52,   // 500 events = 52px
  1000, 60   // 1000+ events = 60px
],

// Cluster color based on dominant event type
'circle-color': [
  'case',
  // More calls than texts
  ['>',
    ['+', ['get', 'call_in_count'], ['get', 'call_out_count']],
    ['+', ['get', 'text_in_count'], ['get', 'text_out_count']]
  ],
  [
    'case',
    ['>', ['get', 'call_in_count'], ['get', 'call_out_count']],
    '#22c55e', // Mostly incoming calls - green
    '#3b82f6'  // Mostly outgoing calls - blue
  ],
  // More texts than calls
  [
    'case',
    ['>', ['get', 'text_in_count'], ['get', 'text_out_count']],
    '#f59e0b', // Mostly incoming texts - amber
    '#ec4899'  // Mostly outgoing texts - pink
  ]
]
```

## Cluster Click Behavior

```javascript
// When cluster is clicked
map.on('click', 'clusters', async (e) => {
  const features = map.queryRenderedFeatures(e.point, {
    layers: ['clusters']
  });

  if (!features.length) return;

  const cluster = features[0];
  const clusterId = cluster.properties.cluster_id;
  const source = map.getSource('phone-events');

  // Option 1: Zoom to expand
  const expansionZoom = await source.getClusterExpansionZoom(clusterId);

  map.easeTo({
    center: cluster.geometry.coordinates,
    zoom: expansionZoom,
    duration: 500
  });

  // Option 2: Show cluster popup with details
  // (Alternative behavior - could be toggled by user preference)
  // const leaves = await source.getClusterLeaves(clusterId, 100, 0);
  // showClusterPopup(cluster, leaves);
});
```

## Time-Filtered Clustering

The cluster must respect the current time filter:

```javascript
function updateTimeFilter(startTime, endTime) {
  const filter = [
    'all',
    ['>=', ['get', 'timestamp'], startTime],
    ['<=', ['get', 'timestamp'], endTime]
  ];

  map.setFilter('clusters', ['all', ['has', 'point_count'], filter]);
  map.setFilter('cluster-count', ['all', ['has', 'point_count'], filter]);
  map.setFilter('unclustered-point', ['all', ['!', ['has', 'point_count']], filter]);
}
```

---

# Key Code Snippets

## Main Entry Point

```javascript
// js/main.js
import { EventBus, eventBus } from './core/EventBus.js';
import { StateManager, state } from './core/StateManager.js';
import { MapController } from './controllers/MapController.js';
import { TimeController } from './controllers/TimeController.js';
import { ThemeController } from './controllers/ThemeController.js';
import { TimeSlider } from './components/TimeSlider.js';
import { WorldClock } from './components/WorldClock.js';
import { PlaybackControls } from './components/PlaybackControls.js';
import { ThemePicker } from './components/ThemePicker.js';
import { GeoJSONLoader } from './data/GeoJSONLoader.js';
import { MAPBOX_TOKEN } from './core/constants.js';

class BandicootVisualizer {
  constructor() {
    this.eventBus = eventBus;
    this.state = state;
    this.controllers = {};
    this.components = {};
  }

  async initialize() {
    // Initialize controllers
    this.controllers.theme = new ThemeController(this.eventBus, this.state);
    this.controllers.map = new MapController(this.eventBus, this.state, MAPBOX_TOKEN);
    this.controllers.time = new TimeController(this.eventBus, this.state);

    // Initialize map
    await this.controllers.map.initialize('map', {
      center: [0, 0],
      zoom: 2
    });

    // Initialize UI components
    this.components.timeSlider = new TimeSlider(
      document.querySelector('.controls__slider'),
      this.eventBus,
      this.state
    );

    this.components.worldClock = new WorldClock(
      document.querySelector('.controls__clock'),
      this.eventBus
    );

    this.components.playback = new PlaybackControls(
      document.querySelector('.controls__playback'),
      this.eventBus,
      this.state
    );

    this.components.themePicker = new ThemePicker(
      document.querySelector('.theme-picker-container'),
      this.eventBus,
      this.state
    );

    // Initialize data loader
    this.dataLoader = new GeoJSONLoader(this.eventBus, this.state);

    // Check for embedded data
    if (window.BANDICOOT_DATA) {
      await this.loadData(window.BANDICOOT_DATA);
    }

    console.log('Bandicoot Visualizer initialized');
  }

  async loadData(geojson) {
    await this.dataLoader.load(geojson);
    this.controllers.map.fitToData();
  }
}

// Bootstrap
document.addEventListener('DOMContentLoaded', () => {
  window.bandicoot = new BandicootVisualizer();
  window.bandicoot.initialize().catch(console.error);
});
```

## Theme Controller

```javascript
// controllers/ThemeController.js
export class ThemeController {
  #currentTheme = 'dark';

  constructor(eventBus, state) {
    this.eventBus = eventBus;
    this.state = state;
    this.#initialize();
  }

  #initialize() {
    // Check saved preference
    const saved = localStorage.getItem('bandicoot-theme');
    if (saved) {
      this.setTheme(saved);
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.setTheme(prefersDark ? 'dark' : 'light');
    }

    // Listen for system changes
    window.matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', (e) => {
        if (!localStorage.getItem('bandicoot-theme')) {
          this.setTheme(e.matches ? 'dark' : 'light');
        }
      });

    // Subscribe to theme change events
    this.eventBus.subscribe('theme:toggle', () => this.toggle());
    this.eventBus.subscribe('theme:set', ({ theme }) => this.setTheme(theme));
  }

  setTheme(theme) {
    this.#currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('bandicoot-theme', theme);
    this.state.setState('theme', theme);

    this.eventBus.publish('theme:change', { theme });
  }

  toggle() {
    this.setTheme(this.#currentTheme === 'dark' ? 'light' : 'dark');
  }

  get current() {
    return this.#currentTheme;
  }
}
```

## World Clock Component

```javascript
// components/WorldClock.js
export class WorldClock {
  #element = null;
  #digits = {};
  #dateElement = null;
  #timezoneElement = null;
  #lastTime = null;

  constructor(container, eventBus) {
    this.eventBus = eventBus;
    this.#render(container);
    this.#subscribeToEvents();
  }

  #render(container) {
    this.#element = document.createElement('div');
    this.#element.className = 'world-clock';
    this.#element.innerHTML = `
      <div class="world-clock__date">
        <span class="world-clock__day"></span>
        <span class="world-clock__month-day"></span>
      </div>
      <div class="world-clock__time">
        <div class="world-clock__digit-group">
          <div class="world-clock__digit" data-digit="h1"></div>
          <div class="world-clock__digit" data-digit="h2"></div>
        </div>
        <span class="world-clock__colon">:</span>
        <div class="world-clock__digit-group">
          <div class="world-clock__digit" data-digit="m1"></div>
          <div class="world-clock__digit" data-digit="m2"></div>
        </div>
        <span class="world-clock__colon">:</span>
        <div class="world-clock__digit-group">
          <div class="world-clock__digit" data-digit="s1"></div>
          <div class="world-clock__digit" data-digit="s2"></div>
        </div>
      </div>
      <div class="world-clock__timezone"></div>
    `;

    container.appendChild(this.#element);

    // Cache digit elements
    this.#element.querySelectorAll('.world-clock__digit').forEach(el => {
      this.#digits[el.dataset.digit] = el;
    });

    this.#dateElement = {
      day: this.#element.querySelector('.world-clock__day'),
      monthDay: this.#element.querySelector('.world-clock__month-day')
    };

    this.#timezoneElement = this.#element.querySelector('.world-clock__timezone');

    // Set timezone
    this.#timezoneElement.textContent = Intl.DateTimeFormat().resolvedOptions().timeZone;
  }

  #subscribeToEvents() {
    this.eventBus.subscribe('time:change', ({ timestamp }) => {
      this.#update(timestamp);
    });
  }

  #update(timestamp) {
    const date = new Date(timestamp);

    // Format time
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    // Update digits with animation
    this.#updateDigit('h1', hours[0]);
    this.#updateDigit('h2', hours[1]);
    this.#updateDigit('m1', minutes[0]);
    this.#updateDigit('m2', minutes[1]);
    this.#updateDigit('s1', seconds[0]);
    this.#updateDigit('s2', seconds[1]);

    // Update date
    this.#dateElement.day.textContent = date.toLocaleDateString('en-US', { weekday: 'short' });
    this.#dateElement.monthDay.textContent = date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });

    this.#lastTime = timestamp;
  }

  #updateDigit(key, value) {
    const el = this.#digits[key];
    if (el.textContent !== value) {
      el.classList.add('world-clock__digit--flip');
      el.textContent = value;

      setTimeout(() => {
        el.classList.remove('world-clock__digit--flip');
      }, 200);
    }
  }
}
```

## GeoJSON Loader

```javascript
// data/GeoJSONLoader.js
export class GeoJSONLoader {
  constructor(eventBus, state) {
    this.eventBus = eventBus;
    this.state = state;
  }

  async load(data) {
    // Validate GeoJSON structure
    if (!this.#validate(data)) {
      throw new Error('Invalid GeoJSON format');
    }

    // Preprocess features
    const processed = this.#preprocess(data);

    // Calculate time range
    const timeRange = this.#calculateTimeRange(processed.features);

    // Calculate event density for slider
    const density = this.#calculateDensity(processed.features);

    // Update state
    this.state.setState('data.features', processed.features);
    this.state.setState('data.loaded', true);
    this.state.setState('time.start', timeRange.start);
    this.state.setState('time.end', timeRange.end);
    this.state.setState('time.current', timeRange.start);

    // Publish event
    this.eventBus.publish('data:loaded', {
      features: processed.features,
      timeRange,
      density,
      bounds: this.#calculateBounds(processed.features)
    });

    return processed;
  }

  #validate(data) {
    if (!data || typeof data !== 'object') return false;
    if (data.type !== 'FeatureCollection') return false;
    if (!Array.isArray(data.features)) return false;

    // Validate first feature
    if (data.features.length > 0) {
      const first = data.features[0];
      if (!first.geometry || !first.properties) return false;
      if (!first.properties.datetime && !first.properties.timestamp) return false;
    }

    return true;
  }

  #preprocess(data) {
    const features = data.features.map(feature => {
      const props = feature.properties;

      // Ensure timestamp exists
      if (!props.timestamp && props.datetime) {
        props.timestamp = new Date(props.datetime).getTime();
      }

      // Normalize interaction type
      props.interaction_type = (props.interaction_type || props.type || 'unknown').toLowerCase();

      // Normalize direction
      props.direction = (props.direction || 'unknown').toLowerCase();

      return feature;
    });

    return { ...data, features };
  }

  #calculateTimeRange(features) {
    let min = Infinity;
    let max = -Infinity;

    features.forEach(f => {
      const t = f.properties.timestamp;
      if (t < min) min = t;
      if (t > max) max = t;
    });

    return { start: min, end: max };
  }

  #calculateDensity(features, bucketMs = 3600000) {
    const buckets = new Map();

    features.forEach(f => {
      const t = f.properties.timestamp;
      const bucket = Math.floor(t / bucketMs) * bucketMs;
      buckets.set(bucket, (buckets.get(bucket) || 0) + 1);
    });

    return Array.from(buckets.entries())
      .map(([time, count]) => ({ time, count }))
      .sort((a, b) => a.time - b.time);
  }

  #calculateBounds(features) {
    let minLng = Infinity, maxLng = -Infinity;
    let minLat = Infinity, maxLat = -Infinity;

    features.forEach(f => {
      const [lng, lat] = f.geometry.coordinates;
      if (lng < minLng) minLng = lng;
      if (lng > maxLng) maxLng = lng;
      if (lat < minLat) minLat = lat;
      if (lat > maxLat) maxLat = lat;
    });

    return [[minLng, minLat], [maxLng, maxLat]];
  }
}
```

---

# Success Criteria

## Functional Requirements

### Map Display
- [ ] Full viewport map with no scrollbars or overflow
- [ ] Map loads with correct theme (dark/light)
- [ ] Navigation controls (zoom) work correctly
- [ ] Map responds to mouse/touch interactions

### Data Visualization
- [ ] GeoJSON data loads and displays on map
- [ ] Markers cluster at appropriate zoom levels
- [ ] Clusters show accurate event counts
- [ ] Clicking cluster zooms to expand
- [ ] Individual markers display with correct type colors

### Time Controls
- [ ] Time slider shows full data range
- [ ] Range selection with dual handles works
- [ ] Current time handle moves during playback
- [ ] Play/pause toggles animation
- [ ] Speed controls affect playback rate (0.5x to 10x)
- [ ] World clock updates in sync with time changes
- [ ] Day/Week/Month presets set correct ranges

### Popups
- [ ] Cluster popup shows event breakdown
- [ ] Individual event popup shows all details
- [ ] Popups position correctly relative to markers
- [ ] Popups close when clicking elsewhere
- [ ] Popups animate smoothly

### Theme System
- [ ] Dark theme applies correctly
- [ ] Light theme applies correctly
- [ ] Theme toggle animates smoothly
- [ ] Map style changes with theme
- [ ] Preference persists in localStorage

## Non-Functional Requirements

### Performance
- [ ] Initial load under 3 seconds
- [ ] 60fps animations maintained
- [ ] No jank during time scrubbing
- [ ] Handles 10,000+ events smoothly
- [ ] Memory stable during extended use

### Design Quality
- [ ] Glassmorphic panels look professional
- [ ] Consistent spacing throughout
- [ ] Typography hierarchy clear
- [ ] Color contrast meets WCAG AA
- [ ] Hover states on all interactive elements
- [ ] Focus states visible for keyboard users

### Code Quality
- [ ] Clean ES6 module structure
- [ ] Pub/Sub properly decouples components
- [ ] No console errors in production
- [ ] Works in Chrome, Firefox, Safari, Edge
- [ ] Mobile-responsive (tablets minimum)

### Documentation
- [ ] Code comments on complex logic
- [ ] JSDoc on public methods
- [ ] README with usage instructions
- [ ] Sample data file included

---

# CDN Dependencies

```html
<!-- Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">

<!-- Mapbox GL JS -->
<link href="https://api.mapbox.com/mapbox-gl-js/v3.3.0/mapbox-gl.css" rel="stylesheet">
<script src="https://api.mapbox.com/mapbox-gl-js/v3.3.0/mapbox-gl.js"></script>
```

---

# Estimated Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Foundation | 2 days | Core infrastructure, theme system, basic map |
| Phase 2: Data Layer | 2 days | GeoJSON loading, clustering, filtering |
| Phase 3: Time System | 3 days | Time slider, world clock, playback controls |
| Phase 4: Popups | 2 days | Cluster and event popups, animations |
| Phase 5: Polish | 3 days | Performance, accessibility, final touches |
| **Total** | **12 days** | Production-ready visualization |

---

# Appendix: Sample GeoJSON

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-122.4194, 37.7749]
      },
      "properties": {
        "antenna_id": "ANT-00142",
        "datetime": "2025-01-15T14:30:45Z",
        "timestamp": 1736950245000,
        "interaction_type": "call",
        "direction": "in",
        "duration": 222,
        "contact_hash": "a7b3c9d2"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-122.4089, 37.7837]
      },
      "properties": {
        "antenna_id": "ANT-00156",
        "datetime": "2025-01-15T15:12:03Z",
        "timestamp": 1736952723000,
        "interaction_type": "text",
        "direction": "out",
        "duration": null,
        "contact_hash": "e4f2a891"
      }
    }
  ]
}
```

---

*This document serves as the complete implementation blueprint for the Bandicoot Mapbox Visualization. Every detail has been carefully considered to create a visualization that will truly set Bandicoot apart as a premium mobile metadata analysis tool.*

**Let's build something extraordinary.**
