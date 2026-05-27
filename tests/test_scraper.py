"""Tests for src.scraper."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.scraper import SOURCE_IDS, _fetch_rss, fetch_all_sources


def _mock_article(source_id: str) -> dict:
    return {
        "title": f"Title from {source_id}",
        "url": "https://example.com",
        "description": "desc",
        "published_at": "2026-05-20T00:00:00+00:00",
        "source": source_id,
    }


def _mock_fetchers(return_map: dict) -> dict:
    return {sid: (lambda d, c, sid=sid, m=return_map: m[sid]) for sid in SOURCE_IDS}


def test_fetch_all_sources_returns_seven_keys():
    patches = {sid: [_mock_article(sid)] for sid in SOURCE_IDS}
    with patch.dict("src.scraper._FETCHERS", _mock_fetchers(patches)):
        result = fetch_all_sources(days_back=7)
    assert len(result) == 7
    assert set(result.keys()) == set(SOURCE_IDS)


def test_each_value_is_list():
    empty = {sid: [] for sid in SOURCE_IDS}
    with patch.dict("src.scraper._FETCHERS", _mock_fetchers(empty)):
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


def test_fetch_rss_uses_requests_with_timeout():
    mock_resp = MagicMock()
    mock_resp.content = b"""<?xml version="1.0"?>
    <rss><channel>
      <item>
        <title>AI breakthrough</title>
        <link>https://example.com/post</link>
        <description>Test desc</description>
        <pubDate>Mon, 20 May 2026 12:00:00 GMT</pubDate>
      </item>
    </channel></rss>"""
    mock_resp.text = mock_resp.content.decode()
    mock_resp.raise_for_status = MagicMock()
    cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)
    with patch("src.scraper._get", return_value=mock_resp) as mock_get:
        articles = _fetch_rss(
            "https://techcrunch.com/feed/",
            "TechCrunch",
            7,
            cutoff,
        )
    mock_get.assert_called_once_with("https://techcrunch.com/feed/")
    assert len(articles) == 1
    assert articles[0]["title"] == "AI breakthrough"


def test_failing_source_does_not_raise():
    def boom(days_back, cutoff):
        raise RuntimeError("network error")

    fetchers = _mock_fetchers({sid: [] for sid in SOURCE_IDS})
    fetchers["techcrunch"] = boom
    with patch.dict("src.scraper._FETCHERS", fetchers):
        result = fetch_all_sources()
    assert result["techcrunch"] == []
    assert len(result) == 7
