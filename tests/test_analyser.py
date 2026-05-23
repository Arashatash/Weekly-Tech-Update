"""Tests for src.analyser."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.analyser import analyse, build_prompt, _validate_briefing


class FakeTextBlock:
    def __init__(self, text: str):
        self.type = "text"
        self.text = text


class FakeResponse:
    def __init__(self, text: str):
        self.content = [FakeTextBlock(text)]


@pytest.fixture
def valid_briefing_json(sample_briefing) -> str:
    return json.dumps(sample_briefing)


def test_build_prompt_includes_articles(sample_raw_articles):
    prompt = build_prompt(sample_raw_articles)
    assert "techcrunch" in prompt
    assert "submit_weekly_briefing" in prompt
    assert "AI-only" in prompt or "AI-only filter" in prompt
    assert "capital_theses" in prompt
    assert "opp_now" in prompt
    assert "leader_voices" in prompt
    assert "Product Hunt" in prompt


def test_build_prompt_enforces_product_hunt_alignment(sample_raw_articles):
    prompt = build_prompt(sample_raw_articles)
    assert "PRODUCT HUNT PICKS STEP" in prompt
    assert "aligned_thesis" in prompt
    assert "Validates" in prompt
    assert "building+opp_now" in prompt or "building" in prompt and "opp_now" in prompt


def test_validate_briefing(sample_briefing):
    result = _validate_briefing(sample_briefing)
    assert result["weekly_theme"] == sample_briefing["weekly_theme"]


def test_validate_briefing_rejects_missing_ph(sample_briefing):
    for cat in sample_briefing["categories"]:
        if cat["id"] in ("building", "opp_now"):
            cat["items"] = [i for i in cat["items"] if i["source"] != "Product Hunt"]
    with pytest.raises(ValueError, match="Product Hunt"):
        _validate_briefing(sample_briefing)


def test_validate_briefing_rejects_ph_without_thesis_tie(sample_briefing):
    for cat in sample_briefing["categories"]:
        if cat["id"] in ("building", "opp_now"):
            for item in cat["items"]:
                if item["source"] == "Product Hunt":
                    item.pop("aligned_thesis", None)
                    item["summary"] = (
                        "Just a vanilla product description with no thesis hook of "
                        "any kind anywhere in the text whatsoever."
                    )
    with pytest.raises(ValueError, match="thesis tie"):
        _validate_briefing(sample_briefing)


def test_analyse_returns_valid_schema(sample_raw_articles, sample_briefing, valid_briefing_json):
    with patch("src.analyser._call_claude", return_value=sample_briefing):
        result = analyse(sample_raw_articles)

    assert "weekly_theme" in result
    assert "categories" in result
    assert "leader_voices" in result
    assert "top_signals" in result
    assert len(result["categories"]) == 5
    assert len(result["leader_voices"]) >= 3

    for cat in result["categories"]:
        assert "id" in cat
        assert "name" in cat
        assert "items" in cat
        for item in cat["items"]:
            assert "title" in item
            assert "source" in item
            assert "url" in item
            assert "summary" in item
            assert "signal" in item
            assert "tags" in item
            assert item["signal"] in ("high", "medium", "low")


def test_analyse_retries_on_parse_failure(sample_raw_articles, sample_briefing):
    call_count = 0

    def flaky_call(client, prompt):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError("bad briefing")
        return sample_briefing

    with patch("src.analyser._call_claude", side_effect=flaky_call):
        result = analyse(sample_raw_articles)

    assert call_count == 2
    assert result["weekly_theme"] == sample_briefing["weekly_theme"]
