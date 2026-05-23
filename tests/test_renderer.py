"""Tests for src.renderer."""

import json

from src.renderer import (
    opportunity_horizon_matrix,
    render_html,
    render_json,
    render_markdown,
    thesis_map,
)

CATEGORY_IDS = (
    "capital_theses",
    "building",
    "opp_now",
    "opp_mid",
    "opp_long",
)


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


def test_render_html_contains_leader_voices(sample_briefing):
    html = render_html(sample_briefing)
    assert "Leader Voices" in html
    assert sample_briefing["leader_voices"][0]["name"] in html
    assert "Bullish" in html


def test_render_markdown_contains_leader_voices(sample_briefing):
    md = render_markdown(sample_briefing)
    assert "## Leader Voices" in md
    assert sample_briefing["leader_voices"][0]["name"] in md


def test_render_json_is_valid(sample_briefing):
    raw = render_json(sample_briefing)
    parsed = json.loads(raw)
    assert parsed["weekly_theme"] == sample_briefing["weekly_theme"]


def test_horizon_matrix_has_three_columns(sample_briefing):
    matrix = opportunity_horizon_matrix(sample_briefing)
    assert len(matrix) == 3
    assert [c["horizon"] for c in matrix] == ["now", "mid", "long"]
    assert sum(c["count"] for c in matrix) >= 3


def test_horizon_matrix_empty_when_too_few_opps():
    briefing = {
        "categories": [
            {"id": "opp_now", "name": "Now", "items": [{"title": "x"}]},
            {"id": "opp_mid", "name": "Mid", "items": []},
            {"id": "opp_long", "name": "Long", "items": []},
        ]
    }
    assert opportunity_horizon_matrix(briefing) == []


def test_thesis_map_pairs_aligned_items(sample_briefing):
    rows = thesis_map(sample_briefing)
    assert rows, "expected aligned thesis rows"
    titles_per_thesis = {
        row["thesis"]["title"]: [a["title"] for a in row["aligned"]]
        for row in rows
    }
    a16z_thesis = "a16z backs agent search"
    assert a16z_thesis in titles_per_thesis
    assert any(
        "AgentForge" in t for t in titles_per_thesis[a16z_thesis]
    )


def test_thesis_map_empty_when_no_overlap():
    briefing = {
        "categories": [
            {
                "id": "capital_theses",
                "name": "Capital",
                "items": [
                    {"title": "Lonely thesis", "tags": ["unique"]},
                ],
            },
            {
                "id": "building",
                "name": "Building",
                "items": [
                    {"title": "Unrelated item", "tags": ["other"]},
                ],
            },
        ]
    }
    assert thesis_map(briefing) == []


def test_render_html_includes_visual_sections(sample_briefing):
    html = render_html(sample_briefing)
    assert 'data-viz="thesis-map"' in html
    assert 'data-viz="horizon-matrix"' in html
    assert "Opportunity Horizon Matrix" in html
    assert "Thesis Map" in html


def test_render_html_shows_aligned_thesis_tag(sample_briefing):
    html = render_html(sample_briefing)
    assert "AgentForge" in html
    assert "↳" in html or "a16z backs agent search" in html
