"""Fetch raw content from each monitored source."""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import feedparser
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

USER_AGENT = "WeeklySignalBriefing/1.0"
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
MAX_ARTICLES = 20
REQUEST_TIMEOUT = 30

SOURCE_IDS = (
    "techcrunch",
    "a16z",
    "sequoia",
    "ycombinator",
    "mit_review",
    "producthunt",
    "hf_papers",
)

SOURCE_DISPLAY = {
    "techcrunch": "TechCrunch",
    "a16z": "a16z",
    "sequoia": "Sequoia Capital",
    "ycombinator": "Y Combinator",
    "mit_review": "MIT Technology Review",
    "producthunt": "Product Hunt",
    "hf_papers": "Hugging Face Papers",
}

_last_request_by_domain: dict[str, float] = {}


def _headers(browser: bool = False) -> dict[str, str]:
    if browser:
        return {
            "User-Agent": BROWSER_UA,
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
        }
    return {"User-Agent": USER_AGENT}


def _rate_limit(url: str) -> None:
    """Sleep 1s between requests to the same domain."""
    from urllib.parse import urlparse

    domain = urlparse(url).netloc
    last = _last_request_by_domain.get(domain)
    if last is not None:
        elapsed = time.time() - last
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
    _last_request_by_domain[domain] = time.time()


def _get(url: str, browser: bool = False, **kwargs: Any) -> requests.Response:
    _rate_limit(url)
    return requests.get(
        url,
        headers=_headers(browser=browser),
        timeout=REQUEST_TIMEOUT,
        **kwargs,
    )


def _clean_title(text: str) -> str:
    """Collapse whitespace and trim."""
    return " ".join(text.split()).strip()


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(value.replace("Z", "+0000"), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    try:
        from email.utils import parsedate_to_datetime

        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None


def _within_days(published_at: str, cutoff: datetime) -> bool:
    if not published_at:
        return True
    dt = _parse_date(published_at)
    if dt is None:
        return True
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt >= cutoff


def _article(
    title: str,
    url: str,
    description: str,
    published_at: str,
    source: str,
) -> dict[str, str]:
    desc = (description or "").strip()
    if len(desc) > 500:
        desc = desc[:497] + "..."
    return {
        "title": title.strip(),
        "url": url.strip(),
        "description": desc,
        "published_at": published_at or "",
        "source": source,
    }


def _fetch_rss(
    feed_url: str,
    display_name: str,
    days_back: int,
    cutoff: datetime,
) -> list[dict[str, str]]:
    _rate_limit(feed_url)
    parsed = feedparser.parse(feed_url, agent=USER_AGENT)
    articles: list[dict[str, str]] = []
    for entry in parsed.entries[: MAX_ARTICLES * 2]:
        title = entry.get("title", "")
        if not title:
            continue
        link = entry.get("link", "")
        summary = entry.get("summary", entry.get("description", ""))
        if summary and "<" in summary:
            summary = BeautifulSoup(summary, "lxml").get_text(separator=" ", strip=True)
        pub = ""
        if entry.get("published"):
            pub = entry.published
        elif entry.get("updated"):
            pub = entry.updated
        elif hasattr(entry, "published_parsed") and entry.published_parsed:
            pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
        if not _within_days(pub, cutoff):
            continue
        articles.append(_article(title, link, summary, pub, display_name))
        if len(articles) >= MAX_ARTICLES:
            break
    return articles


def fetch_techcrunch(days_back: int, cutoff: datetime) -> list[dict[str, str]]:
    return _fetch_rss(
        "https://techcrunch.com/feed/",
        SOURCE_DISPLAY["techcrunch"],
        days_back,
        cutoff,
    )


_A16Z_SKIP_PATHS = (
    "/about",
    "/tos-privacy",
    "/category/",
    "/author/",
    "/tag/",
    "/page/",
    "/podcasts/",
    "/news-content",
    "/team/",
    "/portfolio/",
    "/contact",
    "/careers",
    "/disclosure",
)


def fetch_a16z(days_back: int, cutoff: datetime) -> list[dict[str, str]]:
    """Scrape a16z news-content page (their RSS feed has been removed)."""
    url = "https://a16z.com/news-content/"
    resp = _get(url, browser=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    articles: list[dict[str, str]] = []
    seen: set[str] = set()

    for a in soup.select("a[href^='https://a16z.com/']"):
        href = a.get("href", "")
        if any(skip in href for skip in _A16Z_SKIP_PATHS):
            continue
        if href.rstrip("/").count("/") < 4:
            continue
        title = _clean_title(a.get_text(" ", strip=True))
        if not title or len(title) < 8:
            continue
        if href in seen:
            continue
        seen.add(href)
        articles.append(
            _article(title, href, "a16z perspective", "", SOURCE_DISPLAY["a16z"])
        )
        if len(articles) >= MAX_ARTICLES:
            break
    return articles


def fetch_mit_review(days_back: int, cutoff: datetime) -> list[dict[str, str]]:
    return _fetch_rss(
        "https://www.technologyreview.com/feed/",
        SOURCE_DISPLAY["mit_review"],
        days_back,
        cutoff,
    )


def fetch_ycombinator(days_back: int, cutoff: datetime) -> list[dict[str, str]]:
    url = (
        "https://hn.algolia.com/api/v1/search"
        "?tags=front_page&hitsPerPage=30"
    )
    resp = _get(url)
    resp.raise_for_status()
    data = resp.json()
    articles: list[dict[str, str]] = []
    for hit in data.get("hits", []):
        title = hit.get("title", "")
        if not title:
            continue
        story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
        created = hit.get("created_at", "")
        pub = created
        if created:
            try:
                pub = datetime.fromisoformat(created.replace("Z", "+00:00")).isoformat()
            except ValueError:
                pub = created
        if not _within_days(pub, cutoff):
            continue
        points = hit.get("points", 0)
        desc = f"HN front page · {points} points"
        articles.append(
            _article(title, story_url, desc, pub, SOURCE_DISPLAY["ycombinator"])
        )
        if len(articles) >= MAX_ARTICLES:
            break
    return articles


_SEQUOIA_TITLE_SUFFIX_RE = re.compile(
    r"\s+by\s+[^|]+?(?:\s+(?:Perspective|Spotlight|Insight|Story|Read)\s+Read)?\s*$",
    re.IGNORECASE,
)
_SEQUOIA_TRAILING_LABELS_RE = re.compile(
    r"\s+(?:Perspective|Spotlight|Insight|Story)\s+Read\s*$", re.IGNORECASE,
)


def _clean_sequoia_title(text: str) -> str:
    text = _clean_title(text)
    text = _SEQUOIA_TITLE_SUFFIX_RE.sub("", text)
    text = _SEQUOIA_TRAILING_LABELS_RE.sub("", text)
    return text.strip(" \u00b7-")


def fetch_sequoia(days_back: int, cutoff: datetime) -> list[dict[str, str]]:
    """Scrape Sequoia homepage for article links (their /our-thinking/ path is gone)."""
    url = "https://sequoiacap.com/"
    resp = _get(url, browser=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    articles: list[dict[str, str]] = []
    seen: set[str] = set()

    for a in soup.select("a[href*='sequoiacap.com/article/']"):
        href = a.get("href", "")
        if href.startswith("/"):
            href = f"https://sequoiacap.com{href}"
        title = _clean_sequoia_title(a.get_text(" ", strip=True))
        if not title or len(title) < 6:
            continue
        if href in seen:
            continue
        seen.add(href)
        articles.append(
            _article(title, href, "Sequoia perspective", "", SOURCE_DISPLAY["sequoia"])
        )
        if len(articles) >= MAX_ARTICLES:
            break
    return articles


_PH_RANK_PREFIX_RE = re.compile(r"^\d+\.\s+")


def fetch_producthunt(days_back: int, cutoff: datetime) -> list[dict[str, str]]:
    """Scrape Product Hunt homepage; they moved from /posts/ to /products/."""
    url = "https://www.producthunt.com/"
    resp = _get(url, browser=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    articles: list[dict[str, str]] = []
    seen: set[str] = set()

    for a in soup.select("a[href^='/products/']"):
        href = a.get("href", "")
        title = _PH_RANK_PREFIX_RE.sub("", _clean_title(a.get_text(" ", strip=True)))
        if not title or len(title) < 3:
            continue
        full = f"https://www.producthunt.com{href}"
        if full in seen:
            continue
        seen.add(full)
        articles.append(
            _article(title, full, "Product Hunt launch", "", SOURCE_DISPLAY["producthunt"])
        )
        if len(articles) >= MAX_ARTICLES:
            break
    return articles


def fetch_hf_papers(days_back: int, cutoff: datetime) -> list[dict[str, str]]:
    url = "https://huggingface.co/papers"
    resp = _get(url, browser=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    articles: list[dict[str, str]] = []
    seen: set[str] = set()

    for a in soup.select('a[href*="/papers/"]'):
        href = a.get("href", "")
        if href.count("/papers/") != 1 or href.endswith("/papers"):
            continue
        title = _clean_title(a.get_text(" ", strip=True))
        if not title or len(title) < 5:
            continue
        if href.startswith("/"):
            href = f"https://huggingface.co{href}"
        if href in seen:
            continue
        seen.add(href)
        articles.append(
            _article(title, href, "AI/ML research paper", "", SOURCE_DISPLAY["hf_papers"])
        )
        if len(articles) >= MAX_ARTICLES:
            break
    return articles


_FETCHERS: dict[str, Callable[[int, datetime], list[dict[str, str]]]] = {
    "techcrunch": fetch_techcrunch,
    "a16z": fetch_a16z,
    "sequoia": fetch_sequoia,
    "ycombinator": fetch_ycombinator,
    "mit_review": fetch_mit_review,
    "producthunt": fetch_producthunt,
    "hf_papers": fetch_hf_papers,
}


def fetch_all_sources(days_back: int = 7) -> dict[str, list[dict]]:
    """
    Returns a dict keyed by source_id.
    Each value is a list of article dicts with keys:
      title, url, description, published_at, source
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    results: dict[str, list[dict]] = {}

    import sys

    mod = sys.modules[__name__]
    for source_id in SOURCE_IDS:
        fetcher = getattr(mod, f"fetch_{source_id}")
        try:
            articles = fetcher(days_back, cutoff)
            results[source_id] = articles
            log.info("Fetched %d articles from %s", len(articles), source_id)
        except Exception as exc:
            log.error("Failed to fetch %s: %s", source_id, exc)
            results[source_id] = []

    return results
