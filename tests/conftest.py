"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_briefing() -> dict:
    def _item(source: str, title: str = "Test item") -> dict:
        return {
            "title": title,
            "source": source,
            "url": "https://example.com/article",
            "summary": "A new item. It does X. It matters because Y.",
            "signal": "high",
            "tags": ["AI", "SaaS"],
        }

    categories = [
        {
            "id": "products",
            "name": "New Products & Launches",
            "items": [
                _item("TechCrunch", "TC product"),
                _item("Product Hunt", "PH launch"),
            ],
        },
        {
            "id": "ai_research",
            "name": "AI & Research",
            "items": [
                _item("Hugging Face Papers", "Paper"),
                _item("MIT Technology Review", "Article"),
            ],
        },
        {
            "id": "business",
            "name": "Funding & Business Moves",
            "items": [
                _item("a16z", "VC piece"),
                _item("Sequoia Capital", "Sequoia thesis"),
            ],
        },
        {
            "id": "trends",
            "name": "Trends & Shifts",
            "items": [_item("Y Combinator", "HN trend")],
        },
        {
            "id": "signals",
            "name": "Signals Worth Watching",
            "items": [_item("TechCrunch", "Signal")],
        },
    ]
    return {
        "weekly_theme": "AI agents reshape the stack",
        "theme_context": "This week saw major agent launches and funding rounds.",
        "generated_at": "2026-05-18T20:00:00+00:00",
        "week_of": "2026-05-18",
        "categories": categories,
        "top_signals": [
            {
                "headline": "Agent platforms go mainstream",
                "why_it_matters": "Developers are shifting to agent-first workflows.",
                "urgency": "act_now",
            },
            {
                "headline": "New model efficiency gains",
                "why_it_matters": "Inference costs dropping 40%.",
                "urgency": "watch_closely",
            },
            {
                "headline": "Regulatory clarity emerging",
                "why_it_matters": "EU guidelines reduce uncertainty.",
                "urgency": "stay_informed",
            },
        ],
    }


@pytest.fixture
def sample_raw_articles() -> dict:
    article = {
        "title": "Sample Article",
        "url": "https://example.com",
        "description": "A sample description.",
        "published_at": "2026-05-20T12:00:00+00:00",
        "source": "TechCrunch",
    }
    return {sid: [article] for sid in (
        "techcrunch", "a16z", "sequoia", "ycombinator",
        "mit_review", "producthunt", "hf_papers",
    )}
