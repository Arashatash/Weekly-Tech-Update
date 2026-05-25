"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_briefing() -> dict:
    def _item(
        source: str,
        title: str = "Test item",
        horizon: str | None = None,
        summary: str | None = None,
        aligned_thesis: str | None = None,
        url: str = "https://example.com/article",
    ) -> dict:
        item = {
            "title": title,
            "source": source,
            "url": url,
            "summary": summary or (
                "Capability shifted this week. Implies reallocating toward agent infra "
                "and away from thin wrappers."
            ),
            "signal": "high",
            "tags": ["agents", "infra"],
        }
        if horizon:
            item["horizon"] = horizon
        if aligned_thesis:
            item["aligned_thesis"] = aligned_thesis
        return item

    categories = [
        {
            "id": "capital_theses",
            "name": "Capital & Theses",
            "items": [
                _item("a16z", "a16z backs agent search"),
                _item("Sequoia Capital", "Sequoia AGI thesis"),
            ],
        },
        {
            "id": "building",
            "name": "What's Being Built",
            "items": [
                _item("TechCrunch", "Anthropic ships agents"),
                _item("Hugging Face Papers", "Sparse attention paper"),
                _item(
                    "Product Hunt",
                    "AgentForge — multi-agent orchestrator",
                    summary=(
                        "Validates a16z backs agent search: AgentForge ships a "
                        "multi-agent orchestration platform that operationalises the "
                        "a16z thesis on agent-native developer infra."
                    ),
                    aligned_thesis="a16z backs agent search",
                    url="https://www.producthunt.com/products/agentforge",
                ),
            ],
        },
        {
            "id": "opp_now",
            "name": "Opportunities Now",
            "items": [
                _item(
                    "Product Hunt",
                    "AI QA wedge",
                    horizon="now",
                    summary=(
                        "Validates Sequoia AGI thesis: autonomous QA agents plug into "
                        "CI/CD and prove the Sequoia services-as-software thesis at the "
                        "developer-tooling layer."
                    ),
                    aligned_thesis="Sequoia AGI thesis",
                    url="https://www.producthunt.com/products/ai-qa",
                ),
            ],
        },
        {
            "id": "opp_mid",
            "name": "Opportunities Mid-term",
            "items": [
                _item("MIT Technology Review", "World models category", horizon="mid"),
            ],
        },
        {
            "id": "opp_long",
            "name": "Opportunities Long-term",
            "items": [
                _item("Y Combinator", "Autonomous science stack", horizon="long"),
            ],
        },
    ]
    return {
        "weekly_theme": "Agents compress the software stack",
        "theme_context": (
            "Capital is concentrating on agent infrastructure while enterprises "
            "shift from copilots to outcome-priced workflows."
        ),
        "generated_at": "2026-05-18T20:00:00+00:00",
        "week_of": "2026-05-18",
        "categories": categories,
        "top_signals": [
            {
                "headline": "Frontier labs race on agent reliability",
                "why_it_matters": "Winners will own enterprise workflow budgets this year.",
                "urgency": "act_now",
            },
            {
                "headline": "Inference cost floor keeps falling",
                "why_it_matters": "Changes unit economics for AI-native products.",
                "urgency": "watch_closely",
            },
            {
                "headline": "Regulatory clarity on training data",
                "why_it_matters": "Reduces tail risk for model providers.",
                "urgency": "stay_informed",
            },
        ],
        "leader_voices": [
            {
                "name": "Jensen Huang",
                "org": "NVIDIA",
                "quote_or_paragraph": (
                    "Physical AI and agentic systems will define the next platform shift."
                ),
                "url": "https://example.com/jensen-keynote",
                "stance": "bullish",
                "strategic_implication": (
                    "Operators should prioritize robotics and inference-at-scale plays "
                    "that NVIDIA's stack enables."
                ),
            },
            {
                "name": "Satya Nadella",
                "org": "Microsoft",
                "quote_or_paragraph": (
                    "Copilot is evolving from chat to autonomous workflow agents."
                ),
                "url": "https://example.com/nadella-interview",
                "stance": "bullish",
                "strategic_implication": (
                    "Enterprise distribution favors incumbents embedding agents in "
                    "existing suites; wedge startups need vertical depth."
                ),
            },
            {
                "name": "Sam Altman",
                "org": "OpenAI",
                "quote_or_paragraph": (
                    "Reasoning models unlock new categories of software automation."
                ),
                "url": "https://example.com/altman-statement",
                "stance": "bullish",
                "strategic_implication": (
                    "Capital should track agent reliability and eval infra as the "
                    "bottleneck to enterprise adoption."
                ),
            },
        ],
        "commentary_synthesis": {
            "grounded_view": "AI capabilities are transitioning from generalized reasoning to verticalized action.",
            "comparison_table": [
                {
                    "topic": "Agent autonomy",
                    "investor_view": "Agents will replace 50% of junior knowledge work in 3 years.",
                    "operator_view": "Reliability in edge cases remains the barrier to full autonomy.",
                    "practical_implication": "Build human-in-the-loop fallback mechanisms.",
                }
            ],
        },
        "follow_the_money": [
            {
                "trend_type": "infra_spend",
                "observation": "Cloud providers increasing GPU capex by 30%.",
                "implication": "Inference costs will continue to drop.",
            },
            {
                "trend_type": "capital_flow",
                "observation": "Series A rounds concentrating in evaluation tooling.",
                "implication": "Enterprise trust is the primary bottleneck.",
            },
            {
                "trend_type": "enterprise_spend",
                "observation": "Shift from generic chat tools to verticalized workflow automation.",
                "implication": "Wedge startups must integrate deeply with existing data silos.",
            },
            {
                "trend_type": "overheated_signal",
                "observation": "Foundational model wrappers raising at 100x ARR.",
                "implication": "Valuations are disconnected from moat defensibility.",
            },
        ],
    }


@pytest.fixture
def sample_raw_articles() -> dict:
    article = {
        "title": "Sample AI Article",
        "url": "https://example.com",
        "description": "A sample AI description.",
        "published_at": "2026-05-20T12:00:00+00:00",
        "source": "TechCrunch",
    }
    return {sid: [article] for sid in (
        "techcrunch", "a16z", "sequoia", "ycombinator",
        "mit_review", "producthunt", "hf_papers",
    )}
