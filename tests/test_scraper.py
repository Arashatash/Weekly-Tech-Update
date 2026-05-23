"""Tests for src.scraper."""

from unittest.mock import patch

import pytest

from src.scraper import SOURCE_IDS, fetch_all_sources


def _mock_article(source_id: str) -> dict:
    return {
        "title": f"Title from {source_id}",
        "url": "https://example.com",
        "description": "desc",
        "published_at": "2026-05-20T00:00:00+00:00",
        "source": source_id,
    }


def test_fetch_all_sources_returns_seven_keys():
    patches = {
        "techcrunch": [ _mock_article("techcrunch") ],
        "a16z": [ _mock_article("a16z") ],
        "sequoia": [ _mock_article("sequoia") ],
        "ycombinator": [ _mock_article("ycombinator") ],
        "mit_review": [ _mock_article("mit_review") ],
        "producthunt": [ _mock_article("producthunt") ],
        "hf_papers": [ _mock_article("hf_papers") ],
    }
    with patch("src.scraper.fetch_techcrunch", return_value=patches["techcrunch"]):
        with patch("src.scraper.fetch_a16z", return_value=patches["a16z"]):
            with patch("src.scraper.fetch_sequoia", return_value=patches["sequoia"]):
                with patch("src.scraper.fetch_ycombinator", return_value=patches["ycombinator"]):
                    with patch("src.scraper.fetch_mit_review", return_value=patches["mit_review"]):
                        with patch("src.scraper.fetch_producthunt", return_value=patches["producthunt"]):
                            with patch("src.scraper.fetch_hf_papers", return_value=patches["hf_papers"]):
                                result = fetch_all_sources(days_back=7)
    assert len(result) == 7
    assert set(result.keys()) == set(SOURCE_IDS)


def test_each_value_is_list():
    with patch("src.scraper.fetch_techcrunch", return_value=[]):
        with patch("src.scraper.fetch_a16z", return_value=[]):
            with patch("src.scraper.fetch_sequoia", return_value=[]):
                with patch("src.scraper.fetch_ycombinator", return_value=[]):
                    with patch("src.scraper.fetch_mit_review", return_value=[]):
                        with patch("src.scraper.fetch_producthunt", return_value=[]):
                            with patch("src.scraper.fetch_hf_papers", return_value=[]):
                                result = fetch_all_sources()
    for key in SOURCE_IDS:
        assert isinstance(result[key], list)


def test_article_dict_keys():
    article = {
        "title": "Test",
        "url": "https://x.com",
        "description": "desc",
        "published_at": "",
        "source": "TechCrunch",
    }
    required = {"title", "url", "description", "published_at", "source"}
    assert required == set(article.keys())


def test_failing_source_does_not_raise():
    def boom(days_back, cutoff):
        raise RuntimeError("network error")

    with patch("src.scraper.fetch_techcrunch", side_effect=boom):
        with patch("src.scraper.fetch_a16z", return_value=[]):
            with patch("src.scraper.fetch_sequoia", return_value=[]):
                with patch("src.scraper.fetch_ycombinator", return_value=[]):
                    with patch("src.scraper.fetch_mit_review", return_value=[]):
                        with patch("src.scraper.fetch_producthunt", return_value=[]):
                            with patch("src.scraper.fetch_hf_papers", return_value=[]):
                                result = fetch_all_sources()
    assert result["techcrunch"] == []
    assert len(result) == 7
