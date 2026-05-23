"""Send scraped content to Claude API and return structured briefing JSON."""

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
REQUIRED_CATEGORY_IDS = ("products", "ai_research", "business", "trends", "signals")
CATEGORY_NAMES = {
    "products": "New Products & Launches",
    "ai_research": "AI & Research",
    "business": "Funding & Business Moves",
    "trends": "Trends & Shifts",
    "signals": "Signals Worth Watching",
}
VALID_SIGNALS = {"high", "medium", "low"}
VALID_URGENCY = {"act_now", "watch_closely", "stay_informed"}

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
    },
    "required": ["title", "source", "url", "summary", "signal", "tags"],
}

_BRIEFING_TOOL = {
    "name": "submit_weekly_briefing",
    "description": "Submit the completed weekly briefing after analysing articles and optional web search",
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
    """Build the analysis prompt for Claude."""
    now = datetime.now(timezone.utc)
    week_monday = now.date()
    week_monday = week_monday.fromordinal(
        week_monday.toordinal() - week_monday.weekday()
    )

    trimmed = _trim_articles(raw_articles)
    articles_blob = json.dumps(trimmed, indent=2, default=str)
    total = sum(len(v) for v in trimmed.values())

    sources_present = sorted({k for k, v in trimmed.items() if v})
    return f"""You are an expert tech intelligence analyst producing a weekly signal briefing.

## Your task
1. Use the supplied raw articles as the PRIMARY data source ({total} articles from {len(sources_present)} sources).
2. Use the web_search tool to verify facts, add brief context, and find URLs that were missing.
3. When finished, call the submit_weekly_briefing tool with the complete briefing.

## Time context
- Today (UTC): {now.isoformat()}
- Week of (Monday): {week_monday.isoformat()}
- Set generated_at to current ISO 8601 UTC timestamp
- Set week_of to "{week_monday.isoformat()}"

## Raw articles by source
{articles_blob}

## Category requirements
Include exactly 5 categories with these ids and names:
- products: {CATEGORY_NAMES["products"]}
- ai_research: {CATEGORY_NAMES["ai_research"]}
- business: {CATEGORY_NAMES["business"]}
- trends: {CATEGORY_NAMES["trends"]}
- signals: {CATEGORY_NAMES["signals"]}

## STRICT source rules (read carefully)
- The `source` field MUST be EXACTLY one of these seven literal strings:
  {", ".join(repr(s) for s in ALLOWED_SOURCES)}
- Do NOT invent new source names. Do NOT combine sources with "/" or "+".
- Do NOT cite blogs, docs, or sites discovered via web_search as the source.
  If you used web_search to enrich a story, the source is still the one of the
  seven sources that originally surfaced it.
- Every item MUST have its `source` set to the ORIGINAL source from the raw
  articles list above (e.g. an item from raw_articles["producthunt"] must have
  source="Product Hunt"; an item from raw_articles["ycombinator"] must have
  source="Y Combinator").

## Coverage requirement
- Each of the 7 sources present in the input MUST contribute AT LEAST ONE item
  somewhere in the briefing. Treat this as a hard constraint.
- Do NOT merge multiple items from the same source into a single "round-up"
  item. Pick the strongest 1-3 items per source and keep them separate.

## Quality rules
- Prioritise items from the last 7 days
- 4-7 items per category; skip weak items rather than pad
- top_signals: exactly 3-5 items, ordered by urgency (act_now first)
- signal: high = actionable this week; medium = track monthly; low = background
- tags: max 3 short strings per item
- Escape quotes properly in all string fields

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


def _validate_briefing(data: dict, expected_sources: set[str] | None = None) -> dict:
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

    cited_sources: set[str] = set()
    for cat in categories:
        if "id" not in cat or "name" not in cat or "items" not in cat:
            raise ValueError(f"Category missing required fields: {cat.get('id')}")
        for item in cat.get("items", []):
            for field in ("title", "source", "url", "summary", "signal", "tags"):
                if field not in item:
                    raise ValueError(f"Item missing '{field}' in category {cat['id']}")
            if item["signal"] not in VALID_SIGNALS:
                raise ValueError(f"Invalid signal: {item['signal']}")
            if item["source"] not in ALLOWED_SOURCES:
                raise ValueError(
                    f"Invalid source {item['source']!r}; must be one of "
                    f"{ALLOWED_SOURCES}"
                )
            cited_sources.add(item["source"])

    if expected_sources:
        missing_sources = expected_sources - cited_sources
        if missing_sources:
            raise ValueError(
                f"Missing coverage for sources: {sorted(missing_sources)}"
            )

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


SOURCE_ID_TO_DISPLAY = {
    "techcrunch": "TechCrunch",
    "a16z": "a16z",
    "sequoia": "Sequoia Capital",
    "ycombinator": "Y Combinator",
    "mit_review": "MIT Technology Review",
    "producthunt": "Product Hunt",
    "hf_papers": "Hugging Face Papers",
}


def analyse(raw_articles: dict[str, list[dict]]) -> dict:
    """
    Calls Claude API with web_search tool enabled.
    Returns a validated BriefingDict matching the schema in Section 3.3.
    """
    client = anthropic.Anthropic()
    prompt = build_prompt(raw_articles)
    expected = {
        SOURCE_ID_TO_DISPLAY[sid]
        for sid, items in raw_articles.items()
        if items and sid in SOURCE_ID_TO_DISPLAY
    }
    last_error: Exception | None = None

    for attempt in range(2):
        try:
            data = _call_claude(client, prompt)
            return _validate_briefing(data, expected_sources=expected)
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            log.warning("Parse/validation failed (attempt %d): %s", attempt + 1, exc)
            if attempt == 0:
                log.info("Retrying Claude API call...")
                prompt += (
                    f"\n\nIMPORTANT: Your previous attempt failed validation: {exc}. "
                    "Call submit_weekly_briefing again with strictly valid fields. "
                    "Remember: source MUST be exactly one of "
                    f"{list(ALLOWED_SOURCES)}, and every source present in the input "
                    "must contribute at least one item."
                )
                continue
            raise ValueError(
                f"Failed to parse briefing after 2 attempts: {exc}"
            ) from exc
        except anthropic.APIError as exc:
            log.error("Anthropic API error: %s", exc)
            raise

    raise ValueError(f"Analysis failed: {last_error}")
