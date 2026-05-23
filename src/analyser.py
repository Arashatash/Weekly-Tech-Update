"""Send scraped content to Claude API and return structured AI strategy briefing JSON."""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone

import anthropic
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-opus-4-7"
MAX_ARTICLES_IN_PROMPT = 12

REQUIRED_TOP_KEYS = ("weekly_theme", "theme_context", "categories", "top_signals")
REQUIRED_CATEGORY_IDS = (
    "capital_theses",
    "building",
    "opp_now",
    "opp_mid",
    "opp_long",
)
CATEGORY_NAMES = {
    "capital_theses": "Capital & Theses",
    "building": "What's Being Built",
    "opp_now": "Opportunities Now",
    "opp_mid": "Opportunities Mid-term",
    "opp_long": "Opportunities Long-term",
}
OPPORTUNITY_CATEGORY_IDS = ("opp_now", "opp_mid", "opp_long")
VALID_SIGNALS = {"high", "medium", "low"}
VALID_URGENCY = {"act_now", "watch_closely", "stay_informed"}
VALID_HORIZONS = {"now", "mid", "long"}

ALLOWED_SOURCES = (
    "TechCrunch",
    "a16z",
    "Sequoia Capital",
    "Y Combinator",
    "MIT Technology Review",
    "Product Hunt",
    "Hugging Face Papers",
)

_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "source": {"type": "string", "enum": list(ALLOWED_SOURCES)},
        "url": {"type": "string"},
        "summary": {"type": "string"},
        "signal": {"type": "string", "enum": ["high", "medium", "low"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "horizon": {"type": "string", "enum": ["now", "mid", "long"]},
    },
    "required": ["title", "source", "url", "summary", "signal", "tags"],
}

_BRIEFING_TOOL = {
    "name": "submit_weekly_briefing",
    "description": (
        "Submit the completed weekly AI strategy briefing after analysing "
        "articles and optional web search"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "weekly_theme": {"type": "string"},
            "theme_context": {"type": "string"},
            "generated_at": {"type": "string"},
            "week_of": {"type": "string"},
            "categories": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "enum": list(REQUIRED_CATEGORY_IDS),
                        },
                        "name": {"type": "string"},
                        "items": {"type": "array", "items": _ITEM_SCHEMA},
                    },
                    "required": ["id", "name", "items"],
                },
            },
            "top_signals": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "headline": {"type": "string"},
                        "why_it_matters": {"type": "string"},
                        "urgency": {
                            "type": "string",
                            "enum": list(VALID_URGENCY),
                        },
                    },
                    "required": ["headline", "why_it_matters", "urgency"],
                },
            },
        },
        "required": [
            "weekly_theme",
            "theme_context",
            "generated_at",
            "week_of",
            "categories",
            "top_signals",
        ],
    },
}


def _trim_articles(raw_articles: dict[str, list[dict]]) -> dict[str, list[dict]]:
    return {k: v[:MAX_ARTICLES_IN_PROMPT] for k, v in raw_articles.items()}


def build_prompt(raw_articles: dict[str, list[dict]]) -> str:
    """Build the AI strategy briefing prompt for Claude."""
    now = datetime.now(timezone.utc)
    week_monday = now.date()
    week_monday = week_monday.fromordinal(
        week_monday.toordinal() - week_monday.weekday()
    )

    trimmed = _trim_articles(raw_articles)
    articles_blob = json.dumps(trimmed, indent=2, default=str)
    total = sum(len(v) for v in trimmed.values())

    sources_present = sorted({k for k, v in trimmed.items() if v})
    category_lines = "\n".join(
        f"- {cid}: {CATEGORY_NAMES[cid]}" for cid in REQUIRED_CATEGORY_IDS
    )

    return f"""You are a senior AI strategy analyst producing a weekly AI STRATEGY BRIEFING —
not a news digest. The reader is an operator or investor who needs to see where the AI
market is heading, how capital is positioning, what companies are shipping, and which
opportunities are opening across time horizons.

## Your task
1. Use the supplied raw articles as the PRIMARY data source ({total} articles from {len(sources_present)} sources).
2. Use web_search only to verify facts, fill missing URLs, or add brief strategic context.
3. When finished, call submit_weekly_briefing with the complete briefing.

## Time context
- Today (UTC): {now.isoformat()}
- Week of (Monday): {week_monday.isoformat()}
- Set generated_at to current ISO 8601 UTC timestamp
- Set week_of to "{week_monday.isoformat()}"

## Raw articles by source
{articles_blob}

## Category structure (exactly 5 categories)
{category_lines}

### Per-category guidance
- **capital_theses**: How investors see and believe — rounds, fund theses, partner essays, valuation narratives, where smart money is moving in AI.
- **building**: How companies tackle and solve — frontier model releases, agent platforms, enterprise rollouts, infra/tooling that actually ships.
- **opp_now** (0-6 months): Immediate plays — gaps to move on this quarter, acute wedges, near-term arbitrage. Each item MUST set horizon="now".
- **opp_mid** (6-18 months): Forming categories, positioning windows, second-order effects. Each item MUST set horizon="mid".
- **opp_long** (18+ months): Paradigm shifts, directional bets, weak signals that could compound. Each item MUST set horizon="long".

## AI-only filter (hard rule)
Include ONLY items with a direct, material AI angle. DROP without exception:
- Generic space/hardware launches (e.g. SpaceX) unless explicitly about AI compute
- Non-AI consumer apps, CMS releases, climate/energy unless AI is the core story
- Indie SaaS unless it materially reshapes an AI category

Inclusion test: "Would a serious AI investor or AI-company operator regret missing this?"
If no, drop it. Better 15 sharp items than 30 noisy ones.

## Item quality rules
- Every item MUST have a non-empty, real https URL in the `url` field.
- 3-5 items per category; total briefing ~15-20 items. Skip weak categories rather than pad.
- Each `summary` must answer: what changed AND what it implies for capital allocation,
  company strategy, or which doors opened/closed. No descriptive news recaps.
- Opportunity items (opp_now, opp_mid, opp_long) must name: who could capture the play,
  what would have to be true, and roughly when. Set `horizon` to now/mid/long respectively.

## Source rules
- `source` MUST be EXACTLY one of: {", ".join(repr(s) for s in ALLOWED_SOURCES)}
- Do NOT invent source names or combine with "/" or "+".
- If web_search enriched a story, `source` stays the original feed source from the raw list.
- Sources are best-effort: omit a source if nothing AI-relevant surfaced this week.

## Top signals
- Exactly 3-5 items, ordered by urgency (act_now first).
- Each must be AI-strategic and actionable for an operator/investor this week.

## signal levels
- high = actionable this week; medium = track monthly; low = background awareness
- tags: max 3 short strings per item

You MUST call submit_weekly_briefing when done. Do not reply with free-form JSON in text."""


def _extract_text(content: list) -> str:
    parts: list[str] = []
    for block in content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "".join(parts)


def _extract_tool_briefing(content: list) -> dict | None:
    for block in content:
        if (
            getattr(block, "type", None) == "tool_use"
            and getattr(block, "name", None) == "submit_weekly_briefing"
        ):
            inp = block.input
            if isinstance(inp, dict):
                return inp
    return None


def _repair_json(text: str) -> str:
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text.strip()


def _parse_json_from_text(text: str) -> dict:
    cleaned = _repair_json(text)
    start = cleaned.index("{")
    end = cleaned.rindex("}") + 1
    return json.loads(cleaned[start:end])


def _validate_briefing(data: dict) -> dict:
    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")

    categories = data["categories"]
    if not isinstance(categories, list) or len(categories) != 5:
        raise ValueError(
            f"Expected exactly 5 categories, got "
            f"{len(categories) if isinstance(categories, list) else 'invalid'}"
        )

    found_ids = {c.get("id") for c in categories}
    missing = set(REQUIRED_CATEGORY_IDS) - found_ids
    if missing:
        raise ValueError(f"Missing category ids: {missing}")

    total_items = 0
    for cat in categories:
        cat_id = cat.get("id")
        if "id" not in cat or "name" not in cat or "items" not in cat:
            raise ValueError(f"Category missing required fields: {cat_id}")
        for item in cat.get("items", []):
            total_items += 1
            for field in ("title", "source", "url", "summary", "signal", "tags"):
                if field not in item:
                    raise ValueError(f"Item missing '{field}' in category {cat_id}")
            if not str(item.get("url", "")).strip():
                raise ValueError(f"Item in {cat_id} has empty url: {item.get('title')}")
            if not str(item["url"]).strip().startswith("http"):
                raise ValueError(
                    f"Item in {cat_id} url must start with http: {item.get('url')}"
                )
            if item["signal"] not in VALID_SIGNALS:
                raise ValueError(f"Invalid signal: {item['signal']}")
            if item["source"] not in ALLOWED_SOURCES:
                raise ValueError(
                    f"Invalid source {item['source']!r}; must be one of "
                    f"{ALLOWED_SOURCES}"
                )
            if cat_id in OPPORTUNITY_CATEGORY_IDS:
                horizon = item.get("horizon")
                if horizon not in VALID_HORIZONS:
                    raise ValueError(
                        f"Item in {cat_id} must have horizon now|mid|long, got {horizon!r}"
                    )
                expected = cat_id.replace("opp_", "")
                if horizon != expected:
                    raise ValueError(
                        f"Item in {cat_id} should have horizon={expected}, got {horizon}"
                    )

    if total_items > 25:
        raise ValueError(f"Too many items ({total_items}); target 15-20 for a strategy doc")

    for sig in data["top_signals"]:
        for field in ("headline", "why_it_matters", "urgency"):
            if field not in sig:
                raise ValueError(f"Top signal missing '{field}'")
        if sig["urgency"] not in VALID_URGENCY:
            raise ValueError(f"Invalid urgency: {sig['urgency']}")

    if not (3 <= len(data["top_signals"]) <= 5):
        raise ValueError(
            f"Expected 3-5 top_signals, got {len(data['top_signals'])}"
        )

    return data


def _call_claude(client: anthropic.Anthropic, prompt: str) -> dict:
    model = os.getenv("CLAUDE_MODEL", DEFAULT_MODEL)
    response = client.messages.create(
        model=model,
        max_tokens=16000,
        tools=[
            {"type": "web_search_20250305", "name": "web_search"},
            _BRIEFING_TOOL,
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    tool_data = _extract_tool_briefing(response.content)
    if tool_data is not None:
        return tool_data

    text = _extract_text(response.content)
    if not text.strip():
        raise ValueError("Empty response from Claude")
    return _parse_json_from_text(text)


def analyse(raw_articles: dict[str, list[dict]]) -> dict:
    """
    Calls Claude API with web_search tool enabled.
    Returns a validated AI strategy BriefingDict.
    """
    client = anthropic.Anthropic()
    prompt = build_prompt(raw_articles)
    last_error: Exception | None = None

    for attempt in range(2):
        try:
            data = _call_claude(client, prompt)
            return _validate_briefing(data)
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            log.warning("Parse/validation failed (attempt %d): %s", attempt + 1, exc)
            if attempt == 0:
                log.info("Retrying Claude API call...")
                prompt += (
                    f"\n\nIMPORTANT: Validation failed: {exc}. "
                    "Call submit_weekly_briefing again. Every item needs a real https URL. "
                    "AI-only content. opp_* items need horizon now/mid/long matching their category. "
                    f"Sources must be one of {list(ALLOWED_SOURCES)}."
                )
                continue
            raise ValueError(
                f"Failed to parse briefing after 2 attempts: {exc}"
            ) from exc
        except anthropic.APIError as exc:
            log.error("Anthropic API error: %s", exc)
            raise

    raise ValueError(f"Analysis failed: {last_error}")
