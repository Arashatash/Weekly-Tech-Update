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

STANCE_LABELS = {
    "bullish": "Bullish",
    "bearish": "Bearish",
    "neutral": "Neutral",
}

STANCE_COLOURS = {
    "bullish": "#0F6E56",
    "bearish": "#993C1D",
    "neutral": "#5F5E5A",
}

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

_JINJA_ENV = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


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


def _get_category(briefing: dict, cat_id: str) -> dict | None:
    for cat in briefing.get("categories", []):
        if isinstance(cat, dict) and cat.get("id") == cat_id:
            return cat
    return None


def opportunity_horizon_matrix(briefing: dict) -> list[dict]:
    """Build matrix data for the Opportunity Horizon visual.

    Returns one entry per horizon column in display order, with truncated card
    data ready for templating. Returns [] if there is not enough data to render
    a meaningful visual (fewer than 3 opportunity items combined).
    """
    columns_spec = (
        ("now", "0\u20136 mo", "Act now", "opp_now"),
        ("mid", "6\u201318 mo", "Position", "opp_mid"),
        ("long", "18+ mo", "Place bets", "opp_long"),
    )
    columns: list[dict] = []
    total = 0
    for horizon_key, range_label, action_label, cat_id in columns_spec:
        cat = _get_category(briefing, cat_id) or {}
        items = [i for i in cat.get("items", []) if isinstance(i, dict)]
        cards = [
            {
                "title": item.get("title", ""),
                "tags": item.get("tags", [])[:2],
                "signal": item.get("signal", "low"),
                "source": item.get("source", ""),
            }
            for item in items
        ]
        total += len(items)
        columns.append(
            {
                "horizon": horizon_key,
                "range_label": range_label,
                "action_label": action_label,
                "colour": CATEGORY_COLOURS.get(cat_id, "#5F5E5A"),
                "count": len(items),
                "items": cards,
            }
        )
    if total < 3:
        return []
    return columns


_GENERIC_TAGS = {"agents", "ai", "infra", "ml", "llm", "agentic", "ai-infra"}


def _thesis_match(thesis: dict, item: dict) -> bool:
    """Return True if an item aligns with a thesis.

    Priority order:
    1. If the item has an explicit `aligned_thesis` field, match ONLY against
       that exact thesis title (substring either way). This prevents items with
       generic tags from being attached to every thesis they share a tag with.
    2. Otherwise fall back to tag overlap, ignoring generic AI-wide tags so the
       visual stays signal over noise.
    """
    thesis_title = str(thesis.get("title", "")).strip().lower()
    aligned_field = str(item.get("aligned_thesis", "")).strip().lower()

    if aligned_field:
        if not thesis_title:
            return False
        if aligned_field == thesis_title:
            return True
        return aligned_field in thesis_title or thesis_title in aligned_field

    thesis_tags = {
        str(t).strip().lower() for t in thesis.get("tags", []) if t
    } - _GENERIC_TAGS
    item_tags = {
        str(t).strip().lower() for t in item.get("tags", []) if t
    } - _GENERIC_TAGS
    return bool(thesis_tags and thesis_tags & item_tags)


def thesis_map(briefing: dict) -> list[dict]:
    """Map each capital_theses entry to aligned items in other categories.

    Returns rows like:
        [{"thesis": {...}, "aligned": [{"cat_id": str, "item": dict}, ...]}]
    Only returns rows for theses that have at least one aligned item, and only
    returns the list itself when at least 2 alignments exist overall (so the
    visual is meaningful).
    """
    capital_cat = _get_category(briefing, "capital_theses")
    if not capital_cat:
        return []

    other_items: list[tuple[str, dict]] = []
    for cat in briefing.get("categories", []):
        cat_id = cat.get("id") if isinstance(cat, dict) else None
        if cat_id in (None, "capital_theses"):
            continue
        for item in cat.get("items", []):
            if isinstance(item, dict):
                other_items.append((cat_id, item))

    rows: list[dict] = []
    total_alignments = 0
    for thesis in capital_cat.get("items", []):
        if not isinstance(thesis, dict):
            continue
        aligned: list[dict] = []
        for cat_id, item in other_items:
            if _thesis_match(thesis, item):
                aligned.append(
                    {
                        "cat_id": cat_id,
                        "cat_colour": CATEGORY_COLOURS.get(cat_id, "#5F5E5A"),
                        "title": item.get("title", ""),
                        "source": item.get("source", ""),
                        "url": item.get("url", ""),
                        "is_ph": item.get("source") == "Product Hunt",
                    }
                )
        if aligned:
            total_alignments += len(aligned)
            rows.append({"thesis": thesis, "aligned": aligned})

    if total_alignments < 2:
        return []
    return rows


def render_html(
    briefing: dict | None,
    history_menu: list[dict] | None = None,
    current_date: str = "",
    is_archive: bool = False,
) -> str:
    """Render the full HTML page as a string.

    When ``briefing`` is None or empty, renders the pre-launch landing page —
    sidebar + TL;DR + "Coming Thursday" hero only, no briefing content. The
    template hides every briefing-dependent section via ``{% if briefing %}``
    guards.
    """
    template = _JINJA_ENV.get_template("page.html")

    if briefing:
        week_of = briefing.get("week_of", "")
        generated_at = briefing.get("generated_at", "")
        try:
            gen_display = datetime.fromisoformat(
                generated_at.replace("Z", "+00:00")
            ).strftime("%b %d, %Y %H:%M UTC")
        except ValueError:
            gen_display = generated_at
        week_number = _week_number(week_of)
        date_range = _date_range(week_of)
        total_items = _count_items(briefing)
        high_signal_count = _count_high_signal(briefing)
        horizon = opportunity_horizon_matrix(briefing)
        thesis_rows = thesis_map(briefing)
    else:
        gen_display = ""
        week_number = 0
        date_range = ""
        total_items = 0
        high_signal_count = 0
        horizon = []
        thesis_rows = []

    menu = history_menu or []
    current_entry = next(
        (h for h in menu if h["date"] == current_date),
        menu[0] if menu else None,
    )
    archive_entries = [
        h for h in menu if not current_entry or h["date"] != current_entry["date"]
    ]

    today_label = datetime.now().strftime("%b %d, %Y")

    context = {
        "briefing": briefing,
        "week_number": week_number,
        "date_range": date_range,
        "generated_display": gen_display,
        "total_items": total_items,
        "high_signal_count": high_signal_count,
        "sources_monitored": 7,
        "category_colours": _category_colour_map(),
        "urgency_labels": URGENCY_LABELS,
        "urgency_colours": URGENCY_COLOURS,
        "stance_labels": STANCE_LABELS,
        "stance_colours": STANCE_COLOURS,
        "signal_dots": signal_dots_html,
        "source_badge_style": source_badge_style,
        "horizon_labels": HORIZON_LABELS,
        "horizon_matrix": horizon,
        "thesis_map_rows": thesis_rows,
        "history_menu": menu,
        "current_entry": current_entry,
        "archive_entries": archive_entries,
        "current_date": current_date,
        "is_archive": is_archive,
        "today_label": today_label,
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

    lines.append("## Leader Voices")
    lines.append("")
    for lv in briefing.get("leader_voices", []):
        stance = lv.get("stance", "neutral")
        label = STANCE_LABELS.get(stance, stance)
        lines.append(f"### {lv.get('name', '')} — {lv.get('org', '')}")
        lines.append(f"**Stance:** {label}")
        lines.append("")
        lines.append(lv.get("quote_or_paragraph", ""))
        lines.append("")
        lines.append(lv.get("strategic_implication", ""))
        lines.append("")
        url = lv.get("url", "")
        if url:
            lines.append(f"[Source →]({url})")
        lines.append("")
        lines.append("---")
        lines.append("")

    if "commentary_synthesis" in briefing:
        lines.append("## Commentary Synthesis: Investors vs Operators")
        lines.append("")
        lines.append(briefing["commentary_synthesis"].get("grounded_view", ""))
        lines.append("")
        lines.append("| Topic | Investor View | Operator View | Practical Implication |")
        lines.append("|---|---|---|---|")
        for row in briefing["commentary_synthesis"].get("comparison_table", []):
            lines.append(f"| **{row.get('topic', '')}** | {row.get('investor_view', '')} | {row.get('operator_view', '')} | *{row.get('practical_implication', '')}* |")
        lines.append("")
        lines.append("---")
        lines.append("")

    if "follow_the_money" in briefing:
        lines.append("## Follow the Money")
        lines.append("")
        lines.append("| Trend Type | Observation | Implication |")
        lines.append("|---|---|---|")
        for item in briefing.get("follow_the_money", []):
            ttype = item.get("trend_type", "").replace("_", " ").title()
            lines.append(f"| **{ttype}** | {item.get('observation', '')} | {item.get('implication', '')} |")
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
