"""
Evidence Renderer
=================

Transforms structured evidence objects from data-first indicators into
plain-English statements for investigators.

Rules:
- Never use: confidence, suspicious, likely, probably, meeting, coordinated
- Allowed: found, within, closest, same tower, records, window, duration, count
- If data missing: say "unknown" or "no data present", not guesses

Usage:
    from custom_indicators.render import render_evidence, render_evidence_compact

    result = location_at_specific_time(user, target)
    if result:
        # Full multi-line output
        for line in render_evidence(result):
            print(line)

        # Or one-liner for tables
        print(render_evidence_compact(result))
"""

from typing import Any, Dict, List, Optional, Callable

Evidence = Dict[str, Any]

# ==============================================================================
# Dispatch System
# ==============================================================================

_RENDERERS: Dict[str, Callable[[Evidence], List[str]]] = {}


def register_renderer(evidence_type: str):
    """Decorator to register a renderer for an evidence type."""
    def decorator(func):
        _RENDERERS[evidence_type] = func
        return func
    return decorator


def render_evidence(e: Evidence) -> List[str]:
    """
    Main entry point. Dispatches on e['type'] and returns human-readable lines.

    Parameters
    ----------
    e : dict
        Evidence object with 'type' field

    Returns
    -------
    list of str
        Human-readable statements about the evidence
    """
    evidence_type = e.get("type", "unknown")
    renderer = _RENDERERS.get(evidence_type)

    if renderer is None:
        return [f"Unknown evidence type: {evidence_type}"]

    return renderer(e)


def render_evidence_compact(e: Evidence) -> str:
    """
    One-liner summary for table cells or quick lists.
    """
    t = e.get("type", "unknown")

    if t == "location_at_time":
        loc = e.get("location", {}) or {}
        s = e.get("support", {}) or {}
        return (
            f"{e.get('user_id', 'user')} | tower {loc.get('antenna_id', 'n/a')} | "
            f"closest delta {_fmt_delta_seconds(s.get('closest_event_delta_sec'))}"
        )

    if t == "colocation_with_context":
        coloc = e.get("colocation", {}) or {}
        return (
            f"Tower {coloc.get('antenna_id', 'n/a')} | "
            f"delta {_fmt_delta_seconds(coloc.get('delta_seconds'))}"
        )

    if t == "synchronized_silence":
        sil = e.get("silence", {}) or {}
        return (
            f"Silence | {_fmt_ts(sil.get('start_ts'))} to {_fmt_ts(sil.get('end_ts'))} | "
            f"{_fmt_minutes(sil.get('duration_minutes'))}"
        )

    if t == "group_locations_at_time":
        users = e.get("users", {})
        user_count = len(users)
        with_loc = sum(1 for u in users.values() if u.get("support", {}).get("has_location"))
        return f"{with_loc}/{user_count} users with location at {_fmt_ts(e.get('target_ts'))}"

    if t == "activity_bursts":
        bursts = e.get("bursts", [])
        return f"{len(bursts)} burst(s) detected"

    if t == "inter_event_times":
        summary = e.get("summary", {})
        mean = summary.get("mean")
        return f"Inter-event times: mean {_fmt_delta_seconds(mean) if mean else 'n/a'}"

    if t == "activity_around_time":
        s = e.get("support", {}) or {}
        return (
            f"Activity around {_fmt_ts(e.get('window', {}).get('center_ts'))}: "
            f"{s.get('events_before', 0)} before, {s.get('events_after', 0)} after"
        )

    if t == "relationship_strength":
        contacts = e.get("contacts", {})
        return f"{len(contacts)} contacts ranked"

    if t == "time_at_locations":
        locs = e.get("locations", {})
        return f"{len(locs)} locations with time estimates"

    if t == "location_visit_histogram":
        locs = e.get("all_locations", {})
        filtered = e.get("filtered_below_threshold", [])
        return f"{len(locs)} total locations, {len(filtered)} below threshold"

    return f"{t}"


# ==============================================================================
# Formatting Helpers
# ==============================================================================

def _fmt_ts(ts: Optional[str]) -> str:
    """Format ISO timestamp for display."""
    if not ts:
        return "unknown time"
    # Simple cleanup - remove microseconds and timezone for readability
    return ts.replace("T", " ").split(".")[0]


def _fmt_delta_seconds(sec: Optional[float]) -> str:
    """Format seconds delta as human-readable duration."""
    if sec is None:
        return "unknown"
    sec = abs(int(sec))
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def _fmt_minutes(mins: Optional[float]) -> str:
    """Format minutes as human-readable duration."""
    if mins is None:
        return "unknown"
    mins = float(mins)
    if mins >= 60:
        h = int(mins // 60)
        m = int(round(mins % 60))
        return f"{h}h {m}m" if m else f"{h}h"
    return f"{int(round(mins))}m"


def _fmt_coord(coord: Optional[dict]) -> str:
    """Format coordinate dict for display."""
    if not coord:
        return "no coordinates"
    lat = coord.get("lat")
    lon = coord.get("lon")
    if lat is None or lon is None:
        return "no coordinates"
    return f"{lat:.6f}, {lon:.6f}"


def _safe_int(x: Any, default: int = 0) -> int:
    """Safely convert to int."""
    try:
        return int(x)
    except Exception:
        return default


# ==============================================================================
# Evidence Type Renderers
# ==============================================================================

@register_renderer("location_at_time")
def render_location_at_time(e: Evidence) -> List[str]:
    """Render location_at_time evidence."""
    user_id = e.get("user_id", "unknown user")
    w = e.get("window", {}) or {}
    s = e.get("support", {}) or {}
    loc = e.get("location", {}) or {}
    cov = e.get("coverage", {}) or {}

    lines: List[str] = []
    lines.append(f"User: {user_id}")
    lines.append(
        f"Searched {w.get('before_min', '?')} min before and {w.get('after_min', '?')} min "
        f"after {_fmt_ts(w.get('center_ts'))}."
    )
    lines.append(
        f"Found {_safe_int(s.get('events_in_window'))} phone records in that window; "
        f"closest record is {_fmt_delta_seconds(s.get('closest_event_delta_sec'))} from the target time."
    )

    antenna_id = loc.get("antenna_id")
    coord = loc.get("coord")
    if antenna_id:
        lines.append(f"Closest tower near that time: {antenna_id} ({_fmt_coord(coord)}).")
    else:
        lines.append("No tower/location data available near that time.")

    # Coverage note
    total = cov.get("total_events_in_window")
    with_ant = cov.get("events_with_antenna")
    if total is not None and with_ant is not None:
        lines.append(f"Location data present on {with_ant} of {total} records in the window.")

    return lines


@register_renderer("group_locations_at_time")
def render_group_locations_at_time(e: Evidence) -> List[str]:
    """Render group_locations_at_time evidence."""
    lines: List[str] = []
    lines.append(f"Target time: {_fmt_ts(e.get('target_ts'))}")
    lines.append(f"Search window: {e.get('window_minutes', '?')} minutes")
    lines.append("")

    users = e.get("users", {})
    for uid, data in users.items():
        s = data.get("support", {}) or {}
        loc = data.get("location", {}) or {}

        if s.get("has_location"):
            lines.append(
                f"{uid}: Tower {loc.get('antenna_id')} ({_fmt_coord(loc.get('coord'))}), "
                f"closest record {_fmt_delta_seconds(s.get('closest_event_delta_sec'))} from target."
            )
        else:
            lines.append(f"{uid}: No location data within window.")

    # Co-location summary
    by_antenna = e.get("colocation_summary", {}).get("by_antenna", {})
    colocated = {ant: users for ant, users in by_antenna.items() if len(users) > 1}
    if colocated:
        lines.append("")
        lines.append("Same tower at target time:")
        for ant, user_list in colocated.items():
            lines.append(f"  {ant}: {', '.join(user_list)}")

    return lines


@register_renderer("colocation_with_context")
def render_colocation_with_context(e: Evidence) -> List[str]:
    """Render colocation_with_context evidence."""
    coloc = e.get("colocation", {}) or {}
    ctx = e.get("activity_context", {}) or {}
    params = e.get("parameters", {}) or {}

    lines: List[str] = []
    lines.append(
        f"Both devices at tower {coloc.get('antenna_id')} ({_fmt_coord(coloc.get('coord'))})."
    )
    lines.append(
        f"User A time: {_fmt_ts(coloc.get('user_a_time'))}. "
        f"User B time: {_fmt_ts(coloc.get('user_b_time'))}. "
        f"Time difference: {_fmt_delta_seconds(coloc.get('delta_seconds'))}."
    )

    for user_key in ["user_a", "user_b"]:
        user_ctx = ctx.get(user_key, {})
        if user_ctx:
            lines.append(
                f"{user_key.replace('_', ' ').title()}: "
                f"{user_ctx.get('records_around_count', 0)} records within "
                f"{user_ctx.get('gap_window_minutes', '?')} min of co-location time."
            )

    if params:
        lines.append(
            f"Parameters: co-location window {params.get('colocation_window_minutes', '?')} min, "
            f"activity context window {params.get('gap_threshold_minutes', '?')} min."
        )

    return lines


@register_renderer("synchronized_silence")
def render_synchronized_silence(e: Evidence) -> List[str]:
    """Render synchronized_silence evidence."""
    users = e.get("users") or []
    silence = e.get("silence", {}) or {}
    params = e.get("parameters", {}) or {}
    support = e.get("support", {}) or {}

    lines: List[str] = []
    lines.append(f"Devices: {', '.join(users) if users else 'none listed'}")
    lines.append(
        f"No phone records for all listed devices from {_fmt_ts(silence.get('start_ts'))} "
        f"to {_fmt_ts(silence.get('end_ts'))} (duration {_fmt_minutes(silence.get('duration_minutes'))})."
    )

    # Support data
    start_hour = support.get("start_hour")
    if start_hour is not None:
        is_daytime = support.get("is_daytime", False)
        time_period = "daytime" if is_daytime else "nighttime"
        lines.append(f"Silence started at hour {start_hour} ({time_period}).")

    if params:
        lines.append(
            f"Parameters: min individual silence {params.get('min_silence_minutes', '?')}m, "
            f"min overlap {params.get('min_overlap_minutes', '?')}m."
        )

    # Context - preceding and following events
    preceding = e.get("preceding_events", {}) or {}
    following = e.get("following_events", {}) or {}
    if preceding or following:
        lines.append("")
        lines.append("Activity context:")
        for uid in users:
            pre = preceding.get(uid, {})
            post = following.get(uid, {})
            pre_ts = _fmt_ts(pre.get('ts')) if pre and pre.get('ts') else "unknown"
            post_ts = _fmt_ts(post.get('ts')) if post and post.get('ts') else "unknown"
            lines.append(f"  {uid}: last before at {pre_ts}, first after at {post_ts}.")

    return lines


@register_renderer("activity_around_time")
def render_activity_around_time(e: Evidence) -> List[str]:
    """Render activity_around_time evidence."""
    user_id = e.get("user_id", "unknown user")
    w = e.get("window", {}) or {}
    s = e.get("support", {}) or {}
    before = e.get("before", {}) or {}
    after = e.get("after", {}) or {}

    lines: List[str] = []
    lines.append(f"User: {user_id}")
    lines.append(
        f"Window: {w.get('before_hours', '?')} hours before and "
        f"{w.get('after_hours', '?')} hours after {_fmt_ts(w.get('center_ts'))}."
    )
    lines.append(
        f"Records before: {_safe_int(s.get('events_before'))} "
        f"({before.get('unique_contacts', 0)} unique contacts)."
    )
    lines.append(
        f"Records after: {_safe_int(s.get('events_after'))} "
        f"({after.get('unique_contacts', 0)} unique contacts)."
    )

    return lines


@register_renderer("relationship_strength")
def render_relationship_strength(e: Evidence) -> List[str]:
    """Render relationship_strength evidence."""
    user_id = e.get("user_id", "unknown user")
    contacts = e.get("contacts", {})
    methodology = e.get("methodology", {})

    lines: List[str] = []
    lines.append(f"User: {user_id}")
    lines.append(f"Total contacts: {len(contacts)}")

    if methodology:
        lines.append(
            f"Scoring: {methodology.get('count_weight', 0)*100:.0f}% frequency, "
            f"{methodology.get('duration_weight', 0)*100:.0f}% call duration."
        )

    lines.append("")
    lines.append("Top contacts by computed intensity score:")

    for i, (cid, data) in enumerate(contacts.items()):
        if i >= 10:  # Limit to top 10
            lines.append(f"  ... and {len(contacts) - 10} more")
            break
        lines.append(
            f"  {cid}: score {data.get('score', 0):.3f} "
            f"({data.get('count', 0)} interactions, {data.get('duration_sec', 0)}s calls)"
        )

    return lines


@register_renderer("activity_bursts")
def render_activity_bursts(e: Evidence) -> List[str]:
    """Render activity_bursts evidence."""
    params = e.get("parameters", {}) or {}
    data_span = e.get("data_span", {}) or {}
    bursts = e.get("bursts", [])

    lines: List[str] = []
    lines.append(
        f"Analyzed {data_span.get('total_records', '?')} records from "
        f"{_fmt_ts(data_span.get('first_record'))} to {_fmt_ts(data_span.get('last_record'))}."
    )

    avg_rate = params.get("computed_avg_rate")
    threshold = params.get("computed_threshold")
    if avg_rate is not None and threshold is not None:
        lines.append(
            f"Average rate: {avg_rate:.2f} records per {params.get('window_minutes', '?')} min window. "
            f"Threshold for burst: {threshold:.2f} ({params.get('threshold_multiplier', '?')}x average)."
        )

    lines.append(f"Detected {len(bursts)} burst(s).")

    for i, burst in enumerate(bursts[:5]):  # Limit display
        lines.append(
            f"  Burst {i+1}: {_fmt_ts(burst.get('start_ts'))} to {_fmt_ts(burst.get('end_ts'))}, "
            f"{burst.get('count', 0)} records, {len(burst.get('contacts', []))} contacts."
        )

    if len(bursts) > 5:
        lines.append(f"  ... and {len(bursts) - 5} more bursts")

    return lines


@register_renderer("inter_event_times")
def render_inter_event_times(e: Evidence) -> List[str]:
    """Render inter_event_times evidence."""
    deltas = e.get("deltas_seconds", [])
    summary = e.get("summary", {}) or {}

    lines: List[str] = []
    lines.append(f"Analyzed {summary.get('count', 0)} inter-event gaps.")

    if summary.get('mean') is not None:
        lines.append(
            f"Mean gap: {_fmt_delta_seconds(summary.get('mean'))}. "
            f"Median: {_fmt_delta_seconds(summary.get('median'))}."
        )
        lines.append(
            f"Range: {_fmt_delta_seconds(summary.get('min'))} to {_fmt_delta_seconds(summary.get('max'))}."
        )

    return lines


@register_renderer("time_at_locations")
def render_time_at_locations(e: Evidence) -> List[str]:
    """Render time_at_locations evidence."""
    locations = e.get("locations", {})
    totals = e.get("totals", {}) or {}

    lines: List[str] = []
    lines.append(
        f"Analyzed {totals.get('total_records_with_location', '?')} records "
        f"across {totals.get('unique_antennas', '?')} locations."
    )

    # Sort by hit count descending
    sorted_locs = sorted(locations.items(), key=lambda x: x[1].get('hit_count', 0), reverse=True)

    for antenna_id, data in sorted_locs[:10]:  # Limit display
        assumption = data.get("assumption_minutes_per_hit", 30)
        lines.append(
            f"  {antenna_id}: {data.get('hit_count', 0)} records "
            f"(est. {data.get('estimated_hours', 0):.1f} hours at {assumption} min/record)"
        )

    if len(sorted_locs) > 10:
        lines.append(f"  ... and {len(sorted_locs) - 10} more locations")

    return lines


@register_renderer("location_visit_histogram")
def render_location_visit_histogram(e: Evidence) -> List[str]:
    """Render location_visit_histogram evidence (unusual_locations)."""
    all_locations = e.get("all_locations", {})
    params = e.get("parameters", {}) or {}
    filtered = e.get("filtered_below_threshold", [])

    lines: List[str] = []
    threshold = params.get("threshold_visits", "?")
    lines.append(
        f"Total locations: {len(all_locations)}. "
        f"Locations with {threshold} or fewer visits: {len(filtered)}."
    )

    if filtered:
        lines.append("")
        lines.append(f"Locations at or below threshold ({threshold} visits):")
        for antenna_id in filtered[:10]:
            data = all_locations.get(antenna_id, {})
            lines.append(
                f"  {antenna_id}: {data.get('visit_count', 0)} visit(s) "
                f"({_fmt_coord(data.get('coord'))})"
            )
        if len(filtered) > 10:
            lines.append(f"  ... and {len(filtered) - 10} more")

    return lines
