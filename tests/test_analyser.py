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


def test_validate_briefing(sample_briefing):
    result = _validate_briefing(sample_briefing)
    assert result["weekly_theme"] == sample_briefing["weekly_theme"]


def test_analyse_returns_valid_schema(sample_raw_articles, sample_briefing, valid_briefing_json):
    with patch("src.analyser._call_claude", return_value=sample_briefing):
        result = analyse(sample_raw_articles)

    assert "weekly_theme" in result
    assert "categories" in result
    assert "top_signals" in result
    assert len(result["categories"]) == 5

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
