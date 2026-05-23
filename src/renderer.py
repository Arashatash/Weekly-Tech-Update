"""Transform BriefingDict into HTML, Markdown, and JSON."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

CATEGORY_COLOURS = {
    "capital_theses": "#0F6E56",
    "building": "#185FA5",
    "opp_now": "#993C1D",
    "opp_mid": "#854F0B",
    "opp_long": "#534AB7",
}

HORIZON_LABELS = {
    "now": "0-6 mo",
    "mid": "6-18 mo",
    "long": "18+ mo",
}

URGENCY_LABELS = {
    "act_now": "Act now",
    "watch_closely": "Watch closely",
    "stay_informed": "Stay informed",
}

URGENCY_COLOURS = {
    "act_now": "#E24B4A",
    "watch_closely": "#EF9F27",
    "stay_informed": "#5F5E5A",
}

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _week_number(week_of: str) -> int:
    try:
        dt = datetime.strptime(week_of[:10], "%Y-%m-%d")
        return dt.isocalendar()[1]
    except ValueError:
        return datetime.now().isocalendar()[1]


def _date_range(week_of: str) -> str:
    try:
        monday = datetime.strptime(week_of[:10], "%Y-%m-%d")
        sunday = monday + timedelta(days=6)
        return f"{monday.strftime('%b %d')} – {sunday.strftime('%b %d, %Y')}"
    except ValueError:
        return week_of


def _count_items(briefing: dict) -> int:
    return sum(len(c.get("items", [])) for c in briefing.get("categories", []))


def _count_high_signal(briefing: dict) -> int:
    count = 0
    for cat in briefing.get("categories", []):
        for item in cat.get("items", []):
            if item.get("signal") == "high":
                count += 1
    return count


def signal_dots_html(level: str) -> str:
    """Return HTML for signal dots (3 dots max)."""
    filled = {"high": 3, "medium": 2, "low": 1}.get(level, 1)
    dots = []
    for i in range(3):
        cls = "dot filled" if i < filled else "dot"
        dots.append(f'<span class="{cls}"></span>')
    return "".join(dots)


def source_badge_style(category_id: str) -> str:
    colour = CATEGORY_COLOURS.get(category_id, "#5F5E5A")
    return (
        f"background: {colour}26; color: {colour}; "
        f"border: 1px solid {colour}40;"
    )


def _category_colour_map() -> dict[str, str]:
    return dict(CATEGORY_COLOURS)


def render_html(briefing: dict) -> str:
    """Returns complete HTML as a string."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("page.html")

    week_of = briefing.get("week_of", "")
    generated_at = briefing.get("generated_at", "")

    try:
        gen_display = datetime.fromisoformat(
            generated_at.replace("Z", "+00:00")
        ).strftime("%b %d, %Y %H:%M UTC")
    except ValueError:
        gen_display = generated_at

    context = {
        "briefing": briefing,
        "week_number": _week_number(week_of),
        "date_range": _date_range(week_of),
        "generated_display": gen_display,
        "total_items": _count_items(briefing),
        "high_signal_count": _count_high_signal(briefing),
        "sources_monitored": 7,
        "category_colours": _category_colour_map(),
        "urgency_labels": URGENCY_LABELS,
        "urgency_colours": URGENCY_COLOURS,
        "signal_dots": signal_dots_html,
        "source_badge_style": source_badge_style,
        "horizon_labels": HORIZON_LABELS,
    }
    return template.render(**context)


def render_markdown(briefing: dict) -> str:
    """Returns Markdown as a string."""
    week_of = briefing.get("week_of", "")
    week_num = _week_number(week_of)
    date_range = _date_range(week_of)
    lines = [
        f"# Weekly AI Strategy Briefing — Week {week_num}, {date_range}",
        "",
        f"> {briefing.get('weekly_theme', '')}",
        "",
        briefing.get("theme_context", ""),
        "",
        "---",
        "",
    ]

    for cat in briefing.get("categories", []):
        lines.append(f"## {cat.get('name', '')}")
        lines.append("")
        for item in cat.get("items", []):
            lines.append(f"### {item.get('title', '')}")
            horizon = item.get("horizon", "")
            horizon_part = f" | **Horizon:** {HORIZON_LABELS.get(horizon, horizon)}" if horizon else ""
            lines.append(
                f"**Source:** {item.get('source', '')} | **Signal:** {item.get('signal', '')}{horizon_part}"
            )
            lines.append("")
            lines.append(item.get("summary", ""))
            lines.append("")
            url = item.get("url", "")
            if url:
                lines.append(f"[Read more →]({url})")
            lines.append("")
            lines.append("---")
            lines.append("")

    lines.append("## Top Signals")
    lines.append("")
    for i, sig in enumerate(briefing.get("top_signals", []), 1):
        urgency = sig.get("urgency", "stay_informed")
        label = URGENCY_LABELS.get(urgency, urgency)
        lines.append(f"### {i}. {sig.get('headline', '')}")
        lines.append(f"**Urgency:** {label}")
        lines.append("")
        lines.append(sig.get("why_it_matters", ""))
        lines.append("")

    return "\n".join(lines)


def render_json(briefing: dict) -> str:
    """Returns pretty-printed JSON as a string."""
    return json.dumps(briefing, indent=2, ensure_ascii=False)
