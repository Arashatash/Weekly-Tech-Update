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
    "generated_at",
    "week_of",
    "categories",
    "leader_voices",
    "top_signals",
    "commentary_synthesis",
    "follow_the_money",
)
MIN_CATEGORY_ITEMS = 15
MAX_CATEGORY_ITEMS = 25
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
def _has_thesis_tie(item: dict) -> bool:
    """Return True if the item explicitly ties to a capital thesis."""
    if str(item.get("aligned_thesis", "")).strip():
        return True
    summary = str(item.get("summary", "")).strip()
    return summary.lower().startswith("validates ")


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
                        "url": {"type": "string"},
                        "references": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string"},
                                    "url": {"type": "string"},
                                },
                                "required": ["url"],
                            },
                        },
                    },
                    "required": ["headline", "why_it_matters", "urgency"],
                },
            },
            "commentary_synthesis": {
                "type": "object",
                "properties": {
                    "grounded_view": {"type": "string"},
                    "comparison_table": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "topic": {"type": "string"},
                                "investor_view": {"type": "string"},
                                "operator_view": {"type": "string"},
                                "practical_implication": {"type": "string"},
                                "investor_source_url": {"type": "string"},
                                "operator_source_url": {"type": "string"},
                            },
                            "required": ["topic", "investor_view", "operator_view", "practical_implication"],
                        },
                    },
                },
                "required": ["grounded_view", "comparison_table"],
            },
            "follow_the_money": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "trend_type": {
                            "type": "string",
                            "enum": [
                                "capital_flow",
                                "enterprise_spend",
                                "infra_spend",
                                "acquisition_or_bet",
                                "overheated_signal",
                            ],
                        },
                        "observation": {"type": "string"},
                        "implication": {"type": "string"},
                        "source_url": {"type": "string"},
                    },
                    "required": ["trend_type", "observation", "implication"],
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
            "commentary_synthesis",
            "follow_the_money",
        ],
    },
}


def _trim_articles(raw_articles: dict[str, list[dict]]) -> dict[str, list[dict]]:
    return {k: v[:MAX_ARTICLES_IN_PROMPT] for k, v in raw_articles.items()}


def _build_system_prompt() -> str:
    """Build the static system prompt with role, constraints, and all rules.

    Everything here is context-independent — it does not change between runs.
    Placing these instructions in the dedicated ``system`` parameter improves
    Claude's instruction-following compared to stuffing them into the user turn.
    """
    category_lines = "\n".join(
        f"- {cid}: {CATEGORY_NAMES[cid]}" for cid in REQUIRED_CATEGORY_IDS
    )

    return f"""You are a senior AI strategy analyst producing a comprehensive weekly AI STRATEGY REPORT —
not a news digest. The reader is an operator or investor who needs a multi-angle view of where the AI
market is heading: how capital is positioning, what top leaders are saying, what companies are shipping,
which Product Hunt launches validate investor theses, and which opportunities are opening across horizons.

## Category structure (exactly 5 categories)
{category_lines}

### Per-category guidance
- **capital_theses**: How investors see and believe — rounds, fund theses, partner essays, valuation narratives, where smart money is moving in AI.
- **building**: How companies tackle and solve — frontier model releases, agent platforms, enterprise rollouts, infra/tooling that actually ships. Include aligned Product Hunt picks here when they validate a thesis.
- **opp_now** (0-6 months): Immediate plays — gaps to move on this quarter, acute wedges, near-term arbitrage. Each item MUST set horizon="now".
- **opp_mid** (6-18 months): Forming categories, positioning windows, second-order effects. Each item MUST set horizon="mid".
- **opp_long** (18+ months): Paradigm shifts, directional bets, weak signals that could compound. Each item MUST set horizon="long".

## Product Hunt investor alignment (HARD REQUIREMENT)
The combined `building` + `opp_now` categories MUST contain {PH_MIN_PICKS}-{PH_MAX_PICKS} Product
Hunt items that validate this week's capital theses. The audit pipeline will REJECT the briefing
otherwise and force a retry.

Rules for every Product Hunt item:
- `source` MUST be exactly "Product Hunt" (no variants).
- `url` MUST be the Product Hunt page URL.
- `aligned_thesis` MUST be set to the exact title of the `capital_theses` entry it validates.
- `summary` MUST begin with: "Validates [thesis title]: ..." so the tie is legible.
- Place in `building` when the PH launch shows what is being shipped against a thesis.
- Place in `opp_now` only when the PH product itself is the actionable wedge for an operator/investor.
- Drop non-AI Product Hunt launches and any PH item that does not map to a thesis from THIS week.
- Do NOT include random indie SaaS that doesn't connect to investor narratives.

## AI-only filter (hard rule)
Include ONLY items with a direct, material AI angle. DROP without exception:
- Generic space/hardware launches unless explicitly about AI compute
- Non-AI consumer apps, CMS releases, climate/energy unless AI is the core story
- Cryptocurrency/blockchain projects unless specifically about AI integration
- Indie SaaS unless it materially reshapes an AI category or validates a stated thesis

Inclusion test: "Would a serious AI investor or AI-company operator regret missing this?"
If no, drop it.

## Item quality rules
- 15-25 category items total (3-5 per category); skip weak categories rather than pad.
- Every item MUST have a non-empty, real https URL in the `url` field.
- Each `summary` must answer: what changed AND what it implies for capital allocation,
  company strategy, or which doors opened/closed. No descriptive news recaps.
- Opportunity items (opp_now, opp_mid, opp_long) must name: who could capture the play,
  what would have to be true, and roughly when. Set `horizon` to now/mid/long respectively.

## Source rules
- The `source` field is constrained by the tool schema — use only the allowed values.
- If web search enriched a story, `source` stays the original feed source from the raw list.
- Sources are best-effort: omit a source if nothing AI-relevant surfaced this week.

## Leader voices (required — use web search)
Add 4-8 entries in leader_voices from recent public statements by top AI/tech executives
(CEOs, CTOs, GP-level VCs, research lab directors) who made notable public statements in
the last 7-14 days. Prioritise statements that moved markets, signalled strategic shifts,
or revealed new product/investment direction. Do not force-include leaders who had no
notable public activity this week.
- Find interviews, earnings calls, keynotes, or verified posts.
- Paraphrase is OK if the source URL is real and recent.
- Each entry needs: name, org, quote_or_paragraph, https url, stance (bullish|bearish|neutral
  on AI direction), and strategic_implication (1-2 sentences for operators/investors).

## Commentary Synthesis
- Search for public commentary from leading AI investors (e.g., Sequoia, a16z, YC partners) and compare them with leading operators (e.g., Sam Altman, Jensen Huang).
- Create a `grounded_view` describing where AI is today, where it is heading, and what to expect next. Avoid hype, buzzwords, or exaggerated claims. Focus on patterns, evidence, and practical implications.
- Create a `comparison_table` mapping their differing views on 2-4 key topics, highlighting the practical implications.
- For each row, include `investor_source_url` and `operator_source_url` (real https URLs) whenever you can identify the source, so readers can click through to the original statement.

## Follow the Money
- Track capital flows, enterprise spend, infra spend, acquisitions, strategic bets, and overheated signals.
- Provide 4-8 concrete entries. Highlight what these money flows imply and what signals are worth paying attention to.
- Whenever possible, include `source_url` (real https URL) on each entry pointing to the primary article, filing, or press release.

## Top signals
- Exactly 3-5 items, ordered by urgency (act_now first).
- Each must be AI-strategic and actionable for an operator/investor this week.
- Every signal SHOULD include `url` (a primary source) and MAY include a `references` array of objects with `label` and `url` for additional supporting evidence. Prefer signals whose evidence is clickable.

## Signal levels
- high = actionable this week; medium = track monthly; low = background awareness
- tags: max 3 short strings per item

## Web search guidance
Make 3-6 targeted web searches focused on:
1. Leader statements and quotes from the last 7-14 days.
2. Verifying facts and URLs for high-signal items.
Do NOT use web search to duplicate information already in the supplied articles.

## Required output structure (ALL fields mandatory)
When calling submit_weekly_briefing, you MUST include ALL of these top-level fields:
- `weekly_theme`: one bold sentence capturing the week's dominant narrative
- `theme_context`: 2-3 sentences expanding on the theme with strategic context
- `generated_at`: ISO 8601 UTC timestamp
- `week_of`: Monday date in YYYY-MM-DD format
- `categories`: array of exactly 5 category objects (capital_theses, building, opp_now, opp_mid, opp_long)
- `leader_voices`: array of 4-8 leader voice objects (see Leader voices section)
- `top_signals`: array of 3-5 signal objects
- `commentary_synthesis`: object with `grounded_view` and `comparison_table`
- `follow_the_money`: array of 4-8 objects tracking financial flows

Omitting ANY of these fields will cause validation failure and a forced retry.

You MUST call submit_weekly_briefing when done. Do not reply with free-form JSON in text."""


def build_prompt(raw_articles: dict[str, list[dict]]) -> str:
    """Build the user-facing prompt with task steps, time context, and article data.

    This is the dynamic, per-run content placed in the ``user`` message.
    Static rules and constraints live in :func:`_build_system_prompt`.
    """
    now = datetime.now(timezone.utc)
    week_monday = now.date()
    week_monday = week_monday.fromordinal(
        week_monday.toordinal() - week_monday.weekday()
    )

    trimmed = _trim_articles(raw_articles)
    articles_blob = json.dumps(trimmed, indent=2, default=str)
    total = sum(len(v) for v in trimmed.values())
    sources_present = sorted({k for k, v in trimmed.items() if v})

    return f"""## Your task (run in this order)
1. Use the supplied raw articles as the PRIMARY data source ({total} articles from {len(sources_present)} sources).
2. Use web_search to find recent leader statements and verify facts/URLs (see web search guidance).
3. Draft `capital_theses` first (3-5 distinct investor theses for the week). Give each a short, memorable
   title so other items can reference it by name.
4. PRODUCT HUNT PICKS STEP (do this AFTER capital_theses is drafted, BEFORE finalising building/opp_now):
   - Re-list the capital_theses titles you just wrote.
   - Scan the Product Hunt items in the raw articles. For EACH thesis, look for a PH launch
     that operationalises/validates it. Discard PH items that do not map to a thesis.
   - Select {PH_MIN_PICKS}-{PH_MAX_PICKS} PH products total and place them per the Product Hunt
     alignment rules.
5. Finish building/opp_mid/opp_long with non-PH items as needed.
6. When finished, call submit_weekly_briefing with the complete report.

## Time context
- Today (UTC): {now.isoformat()}
- Week of (Monday): {week_monday.isoformat()}
- Set generated_at to current ISO 8601 UTC timestamp
- Set week_of to "{week_monday.isoformat()}"

## Raw articles by source
{articles_blob}"""


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
            if not str(item["url"]).strip().startswith("https://"):
                raise ValueError(
                    f"Item in {cat_id} url must start with https://: {item.get('url')}"
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

    if total_items < MIN_CATEGORY_ITEMS:
        raise ValueError(
            f"Too few category items ({total_items}); "
            f"target {MIN_CATEGORY_ITEMS}-{MAX_CATEGORY_ITEMS}"
        )
    if total_items > MAX_CATEGORY_ITEMS:
        raise ValueError(
            f"Too many category items ({total_items}); "
            f"target {MIN_CATEGORY_ITEMS}-{MAX_CATEGORY_ITEMS}"
        )

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
        if not str(lv["url"]).strip().startswith("https://"):
            raise ValueError(
                f"Leader voice url must start with https://: {lv.get('url')}"
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

    commentary = data.get("commentary_synthesis")
    if not isinstance(commentary, dict):
        raise ValueError("commentary_synthesis must be an object")
    if not str(commentary.get("grounded_view", "")).strip():
        raise ValueError("commentary_synthesis missing grounded_view")
    if not isinstance(commentary.get("comparison_table"), list):
        raise ValueError("commentary_synthesis missing comparison_table list")

    ftm = data.get("follow_the_money")
    if not isinstance(ftm, list) or len(ftm) < 4:
        raise ValueError(
            f"Expected at least 4 follow_the_money entries, got "
            f"{len(ftm) if isinstance(ftm, list) else 'invalid'}"
        )

    return data


def _call_claude(
    client: anthropic.Anthropic,
    system_prompt: str,
    user_prompt: str,
) -> dict:
    model = os.getenv("CLAUDE_MODEL", DEFAULT_MODEL)

    kwargs: dict = dict(
        model=model,
        max_tokens=16000,
        system=system_prompt,
        tools=[
            {"type": "web_search_20250305", "name": "web_search"},
            _BRIEFING_TOOL,
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Some models (e.g. claude-opus-4-7) deprecate the temperature param.
    # Only include it when the model is known to support it, or when
    # explicitly set via CLAUDE_TEMPERATURE env var.
    temp_env = os.getenv("CLAUDE_TEMPERATURE")
    if temp_env is not None:
        kwargs["temperature"] = float(temp_env)
    elif "opus" not in model:
        kwargs["temperature"] = 0.4

    response = client.messages.create(**kwargs)

    if getattr(response, "stop_reason", None) == "max_tokens":
        log.warning("Claude API hit max_tokens limit! Output may be truncated.")

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
    system_prompt = _build_system_prompt()
    user_prompt = build_prompt(raw_articles)

    # Prepend remediation at the TOP of the user message so it's in a
    # high-attention position (beginning of context) rather than buried
    # after the articles blob where it would be "lost in the middle".
    if audit_feedback:
        user_prompt = (
            f"## PRIORITY: Audit remediation (fix these issues FIRST)\n"
            f"{audit_feedback}\n\n{user_prompt}"
        )

    last_error: Exception | None = None

    for attempt in range(2):
        try:
            data = _call_claude(client, system_prompt, user_prompt)
            return _validate_briefing(data)
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            log.warning("Parse/validation failed (attempt %d): %s", attempt + 1, exc)
            if attempt == 0:
                log.info("Retrying Claude API call...")
                remediation = (
                    f"## PRIORITY: Fix validation errors from previous attempt\n"
                    f"Validation failed: {exc}\n"
                    f"Call submit_weekly_briefing again with ALL required fields:\n"
                    f"- weekly_theme (string)\n"
                    f"- theme_context (2-3 sentences of strategic context)\n"
                    f"- generated_at (ISO 8601 UTC)\n"
                    f"- week_of (YYYY-MM-DD Monday)\n"
                    f"- categories (exactly 5: capital_theses, building, opp_now, opp_mid, opp_long)\n"
                    f"- leader_voices (4-8 entries with name, org, quote_or_paragraph, url, stance, strategic_implication)\n"
                    f"- top_signals (3-5 entries)\n"
                    f"Every item needs a real https URL. AI-only content only. "
                    f"opp_* items need horizon now/mid/long matching their category. "
                    f"building+opp_now MUST include {PH_MIN_PICKS}-{PH_MAX_PICKS} "
                    f"Product Hunt items with aligned_thesis set and summary "
                    f"starting with 'Validates [thesis]: ...'.\n\n"
                )
                user_prompt = remediation + user_prompt
                continue
            raise ValueError(
                f"Failed to parse briefing after 2 attempts: {exc}"
            ) from exc
        except anthropic.APIError as exc:
            log.error("Anthropic API error: %s", exc)
            raise

    raise ValueError(f"Analysis failed: {last_error}")
