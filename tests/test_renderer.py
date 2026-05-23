"""Tests for src.renderer."""

import json

from src.renderer import render_html, render_json, render_markdown

CATEGORY_IDS = ("products", "ai_research", "business", "trends", "signals")


def test_render_html_starts_with_doctype(sample_briefing):
    html = render_html(sample_briefing)
    assert html.startswith("<!DOCTYPE html>")


def test_render_html_contains_all_category_ids(sample_briefing):
    html = render_html(sample_briefing)
    for cat_id in CATEGORY_IDS:
        assert f'data-category="{cat_id}"' in html


def test_render_html_contains_weekly_theme(sample_briefing):
    html = render_html(sample_briefing)
    assert sample_briefing["weekly_theme"] in html


def test_render_markdown_contains_headings(sample_briefing):
    md = render_markdown(sample_briefing)
    assert "## " in md
    assert sample_briefing["weekly_theme"] in md


def test_render_json_is_valid(sample_briefing):
    raw = render_json(sample_briefing)
    parsed = json.loads(raw)
    assert parsed["weekly_theme"] == sample_briefing["weekly_theme"]
