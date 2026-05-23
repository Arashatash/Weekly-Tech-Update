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

REQUIRED_TOP_KEYS = (
    "weekly_theme",
    "theme_context",
    "categories",
    "leader_voices",
    "top_signals",
)
VALID_STANCES = {"bullish", "bearish", "neutral"}
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
        "aligned_thesis": {"type": "string"},
    },
    "required": ["title", "source", "url", "summary", "signal", "tags"],
}

PH_SOURCE = "Product Hunt"
PH_REQUIRED_CATEGORIES = ("building", "opp_now")
PH_MIN_PICKS = 2
PH_MAX_PICKS = 4
PH_THESIS_PHRASES = (
    "validates",
    "validating",
    "validation",
    "aligned_thesis",
    "aligned with",
    "ties to",
    "tied to",
    "operationalizes",
    "proves out",
    "confirms",
    "evidence for",
    "instantiates",
)


def _has_thesis_tie(item: dict) -> bool:
    """Return True if the item explicitly ties to a capital thesis."""
    aligned = str(item.get("aligned_thesis", "")).strip()
    if aligned:
        return True
    summary = str(item.get("summary", "")).lower()
    return any(phrase in summary for phrase in PH_THESIS_PHRASES)


def collect_ph_items(briefing: dict) -> list[tuple[str, dict]]:
    """Return (category_id, item) pairs for Product Hunt items in building+opp_now."""
    out: list[tuple[str, dict]] = []
    for cat in briefing.get("categories", []):
        if not isinstance(cat, dict):
            continue
        cat_id = cat.get("id")
        if cat_id not in PH_REQUIRED_CATEGORIES:
            continue
        for item in cat.get("items", []):
            if isinstance(item, dict) and item.get("source") == PH_SOURCE:
                out.append((cat_id, item))
    return out

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
            "leader_voices": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "org": {"type": "string"},
                        "quote_or_paragraph": {"type": "string"},
                        "url": {"type": "string"},
                        "stance": {
                            "type": "string",
                            "enum": list(VALID_STANCES),
                        },
                        "strategic_implication": {"type": "string"},
                    },
                    "required": [
                        "name",
                        "org",
                        "quote_or_paragraph",
                        "url",
                        "stance",
                        "strategic_implication",
                    ],
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
            "leader_voices",
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

    return f"""You are a senior AI strategy analyst producing a comprehensive weekly AI STRATEGY REPORT —
not a news digest. The reader is an operator or investor who needs a multi-angle view of where the AI
market is heading: how capital is positioning, what top leaders are saying, what companies are shipping,
which Product Hunt launches validate investor theses, and which opportunities are opening across horizons.

## Your task (run in this order)
1. Use the supplied raw articles as the PRIMARY data source ({total} articles from {len(sources_present)} sources).
2. Use web_search to find recent (last 7-14 days) public statements from top AI leaders AND to verify facts/URLs.
3. First, draft `capital_theses` (3-5 distinct investor theses for the week). Give each a short, memorable
   title so other items can reference it by name.
4. PRODUCT HUNT PICKS STEP (do this AFTER capital_theses is drafted, BEFORE finalising building/opp_now):
   - Re-list the {PH_MIN_PICKS}-{PH_MAX_PICKS} capital_theses titles you just wrote.
   - Scan the Product Hunt items in the raw articles. For EACH thesis, look for a PH launch
     that operationalises/validates it. Discard PH items that do not map to a thesis.
   - Select {PH_MIN_PICKS}-{PH_MAX_PICKS} PH products total. Place them in `building` (preferred) OR
     `opp_now` (only when the PH launch is itself the wedge). Combined `building`+`opp_now` MUST
     contain at least {PH_MIN_PICKS} Product Hunt items this week.
   - For EACH PH item you include, set the optional field `aligned_thesis` to the exact title of the
     capital_theses entry it validates, AND begin the `summary` with: "Validates [thesis title]: ...".
   - `source` for these items MUST be exactly "Product Hunt"; `url` MUST be the Product Hunt URL.
5. Finish building/opp_mid/opp_long with non-PH items as needed.
6. When finished, call submit_weekly_briefing with the complete report.

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
- **building**: How companies tackle and solve — frontier model releases, agent platforms, enterprise rollouts, infra/tooling that actually ships. Include aligned Product Hunt picks here when they validate a thesis.
- **opp_now** (0-6 months): Immediate plays — gaps to move on this quarter, acute wedges, near-term arbitrage. Each item MUST set horizon="now". Include PH launches here when they validate a near-term thesis.
- **opp_mid** (6-18 months): Forming categories, positioning windows, second-order effects. Each item MUST set horizon="mid".
- **opp_long** (18+ months): Paradigm shifts, directional bets, weak signals that could compound. Each item MUST set horizon="long".

## Leader voices (required — use web_search)
Add 4-8 entries in leader_voices from recent public statements by top leaders such as:
Elon Musk, Jensen Huang, Satya Nadella, Sundar Pichai, Sam Altman, Demis Hassabis, Ben Horowitz,
Pat Grady, Andy Jassy, or comparable AI/tech executives.
- Find interviews, earnings calls, keynotes, or verified posts from the last 7-14 days.
- Paraphrase is OK if the source URL is real and recent.
- Each entry needs: name, org, quote_or_paragraph, https url, stance (bullish|bearish|neutral on AI direction),
  and strategic_implication (1-2 sentences for operators/investors).

## Product Hunt investor alignment (HARD REQUIREMENT)
- The combined `building` + `opp_now` categories MUST contain {PH_MIN_PICKS}-{PH_MAX_PICKS} Product
  Hunt items this week. The audit pipeline will REJECT the briefing otherwise and force a retry.
- Each Product Hunt item MUST:
  * have `source` exactly "Product Hunt" (no variants);
  * have `url` set to its Product Hunt page;
  * set `aligned_thesis` to the exact title of the `capital_theses` entry it validates;
  * begin its `summary` with the literal pattern: `Validates [thesis title]: ...` so the tie is
    legible to readers and to the audit checker.
- Drop non-AI Product Hunt launches and any PH item that does not map to a thesis from THIS week.
- Place PH picks in `building` when they show what is being shipped against a thesis, or in `opp_now`
  when the PH product itself is the actionable wedge for an operator/investor this quarter.
- Do NOT include random indie SaaS that doesn't connect to investor narratives.

## AI-only filter (hard rule)
Include ONLY items with a direct, material AI angle. DROP without exception:
- Generic space/hardware launches (e.g. SpaceX) unless explicitly about AI compute
- Non-AI consumer apps, CMS releases, climate/energy unless AI is the core story
- Indie SaaS unless it materially reshapes an AI category or validates a stated thesis

Inclusion test: "Would a serious AI investor or AI-company operator regret missing this?"
If no, drop it. Target ~15-20 category items plus 4-8 leader voices (~30 total entries max).

## Item quality rules
- Every item MUST have a non-empty, real https URL in the `url` field.
- 3-5 items per category; skip weak categories rather than pad.
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
        raise ValueError(f"Too many category items ({total_items}); target 15-20")

    ph_picks = collect_ph_items(data)
    if len(ph_picks) < PH_MIN_PICKS:
        raise ValueError(
            f"Product Hunt alignment: need >= {PH_MIN_PICKS} Product Hunt items in "
            f"building+opp_now, got {len(ph_picks)}. Add PH launches that validate this "
            f"week's capital_theses (set aligned_thesis and start summary with 'Validates ...')."
        )
    if len(ph_picks) > PH_MAX_PICKS:
        raise ValueError(
            f"Too many Product Hunt picks in building+opp_now ({len(ph_picks)}); "
            f"keep to {PH_MIN_PICKS}-{PH_MAX_PICKS} highest-conviction launches."
        )
    for cat_id, item in ph_picks:
        if not _has_thesis_tie(item):
            raise ValueError(
                f"Product Hunt item '{item.get('title')}' in {cat_id} lacks an explicit "
                "thesis tie. Set aligned_thesis to the capital_theses title it validates "
                "and begin the summary with 'Validates [thesis]: ...'."
            )

    leader_voices = data.get("leader_voices", [])
    if not isinstance(leader_voices, list):
        raise ValueError("leader_voices must be a list")
    if not (3 <= len(leader_voices) <= 8):
        raise ValueError(
            f"Expected 3-8 leader_voices, got {len(leader_voices)}"
        )
    for lv in leader_voices:
        for field in (
            "name",
            "org",
            "quote_or_paragraph",
            "url",
            "stance",
            "strategic_implication",
        ):
            if field not in lv or not str(lv.get(field, "")).strip():
                raise ValueError(f"Leader voice missing required field: {field}")
        if not str(lv["url"]).strip().startswith("https"):
            raise ValueError(
                f"Leader voice url must start with https: {lv.get('url')}"
            )
        if lv["stance"] not in VALID_STANCES:
            raise ValueError(f"Invalid leader stance: {lv['stance']}")

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


def analyse(
    raw_articles: dict[str, list[dict]],
    audit_feedback: str | None = None,
) -> dict:
    """
    Calls Claude API with web_search tool enabled.
    Returns a validated AI strategy BriefingDict.
    """
    client = anthropic.Anthropic()
    prompt = build_prompt(raw_articles)
    if audit_feedback:
        prompt += f"\n\n## Audit remediation (fix these issues)\n{audit_feedback}"
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
                    "Include 4-8 leader_voices with name, org, url, stance, strategic_implication. "
                    f"building+opp_now MUST include {PH_MIN_PICKS}-{PH_MAX_PICKS} Product Hunt items, "
                    "each with source='Product Hunt', a Product Hunt url, aligned_thesis set, and "
                    "summary starting with 'Validates [thesis title]: ...'. "
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
