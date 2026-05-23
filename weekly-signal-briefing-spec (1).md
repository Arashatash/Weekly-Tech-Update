# Weekly Signal Briefing — Spec-Driven Development Document

**Version:** 1.0  
**Status:** Ready for implementation  
**Target:** Cursor / Claude Code / any AI dev agent  
**Estimated build time:** 2–4 hours

---

## 0. How to use this spec

This document is a complete, self-contained specification. Hand it to an AI coding agent (Cursor, Claude Code, Windsurf, etc.) and instruct it to:

1. Read the full spec before writing any code.
2. Implement each module in the order listed in Section 6.
3. Run the acceptance tests in Section 7 before declaring done.
4. Never deviate from the folder structure in Section 4.

> **One sentence summary:** Build a Python system that runs on a schedule, scrapes 7 tech intelligence sources, sends the results to the Claude API for categorisation and insight extraction, generates a styled HTML page, and publishes it to GitHub Pages automatically.

---

## 1. Product Vision

### What it is
An automated weekly intelligence briefing that monitors 7 frontier tech sources, surfaces the most important products, research, trends, and signals, and publishes a visual HTML page to a public URL anyone can access — with zero manual effort after setup.

### Who it is for
A single operator (the owner) who needs to stay at the frontier of AI, deep tech, and venture activity without spending hours reading. The published page is also readable by anyone the owner shares the URL with.

### Core job to be done
> "Every Monday morning I want to open a page and immediately understand what moved last week and what I should pay attention to — without reading anything else."

---

## 2. Sources to Monitor

| ID | Source | URL | Content type |
|----|--------|-----|-------------|
| `techcrunch` | TechCrunch | https://techcrunch.com | Startup news, product launches, funding |
| `a16z` | a16z blog | https://a16z.com/news-content | VC perspective, essays, trend reports |
| `sequoia` | Sequoia Capital | https://www.sequoiacap.com/our-thinking | Investing theses, market takes |
| `ycombinator` | Y Combinator | https://news.ycombinator.com | Hacker News top posts, YC launches |
| `mit_review` | MIT Technology Review | https://www.technologyreview.com | Deep tech journalism, research coverage |
| `producthunt` | Product Hunt | https://www.producthunt.com | New product launches, top of the day |
| `hf_papers` | Hugging Face Daily Papers | https://huggingface.co/papers | AI/ML research papers (daily digest) |

---

## 3. Output Specification

### 3.1 Primary output: HTML briefing page

The system generates a single self-contained `index.html` file with the following sections, in order:

1. **Header bar** — week number, date range, generation timestamp
2. **Weekly theme** — one bold sentence + 2–3 sentences of context
3. **Signal dashboard** — 3 metric cards: total items, high-signal count, categories covered
4. **Category sections** (5 categories, order below) — each with a coloured left-border, item cards, signal dots, tags, and source badges
5. **Top signals panel** — 3–5 distilled signals with urgency labels
6. **Footer** — source list, generation info

### 3.2 Categories

| ID | Display name | Colour (hex) | Description |
|----|-------------|-------------|-------------|
| `products` | New Products & Launches | `#185FA5` | New tools, apps, demos released this week |
| `ai_research` | AI & Research | `#534AB7` | Model releases, papers, breakthroughs |
| `business` | Funding & Business Moves | `#0F6E56` | Rounds, acquisitions, strategic shifts |
| `trends` | Trends & Shifts | `#993C1D` | Emerging behavioural or adoption patterns |
| `signals` | Signals Worth Watching | `#854F0B` | Early, weak signals that could compound |

### 3.3 Per-item data model

```json
{
  "title": "string — exact article/product title",
  "source": "string — source display name",
  "url": "string — direct link, empty string if not found",
  "summary": "string — 2–3 sentences: what it is, what it does, why it matters",
  "signal": "high | medium | low",
  "tags": ["array", "of", "short", "strings", "max 3"]
}
```

### 3.4 Signal levels

| Level | Dot indicator | Meaning |
|-------|-------------|---------|
| `high` | 3 filled red dots | Actionable now. Founder/investor should respond this week |
| `medium` | 2 filled amber dots | Worth tracking. Review monthly |
| `low` | 1 filled grey dot | Background awareness. File and forget |

### 3.5 Urgency labels (for Top Signals section)

| Value | Label | Colour |
|-------|-------|--------|
| `act_now` | Act now | `#E24B4A` |
| `watch_closely` | Watch closely | `#EF9F27` |
| `stay_informed` | Stay informed | `#5F5E5A` |

### 3.6 Secondary outputs

- `briefing.json` — raw structured data (same schema as API response)
- `briefing.md` — markdown version for Notion/Substack/email

---

## 4. Folder Structure

```
weekly-signal-briefing/
├── .github/
│   └── workflows/
│       └── briefing.yml          # GitHub Actions automation
├── src/
│   ├── __init__.py
│   ├── scraper.py                # Source fetching logic
│   ├── analyser.py               # Claude API calls + parsing
│   ├── renderer.py               # HTML/MD generation
│   └── publisher.py              # GitHub Pages commit logic
├── templates/
│   └── page.html                 # Jinja2 HTML template
├── output/
│   ├── index.html                # Generated (do not edit manually)
│   ├── briefing.json             # Generated
│   └── briefing.md               # Generated
├── tests/
│   ├── test_scraper.py
│   ├── test_analyser.py
│   └── test_renderer.py
├── .env.example                  # Required env vars (no secrets)
├── .gitignore
├── generate.py                   # Main entrypoint (run this locally)
├── requirements.txt
└── README.md
```

---

## 5. Architecture

```
generate.py
    │
    ├── scraper.py          → Fetches raw content from each of the 7 sources
    │   └── returns: Dict[source_id, List[ArticleDict]]
    │
    ├── analyser.py         → Sends content to Claude API with web_search enabled
    │   └── returns: BriefingDict (matches Section 3.3 schema)
    │
    ├── renderer.py         → Renders BriefingDict into HTML, MD, JSON
    │   └── returns: Dict[format, str]
    │
    └── publisher.py        → Writes output/ files, optionally commits to gh-pages
        └── returns: None
```

The system is intentionally linear. No async, no queues, no databases. Each module is independently testable.

---

## 6. Implementation Modules

Implement in this exact order.

---

### Module 1: `src/scraper.py`

**Purpose:** Fetch raw content from each source. Return structured article data.

**Strategy per source:**

| Source | Strategy | Notes |
|--------|----------|-------|
| TechCrunch | RSS feed | `https://techcrunch.com/feed/` |
| a16z | RSS feed | `https://a16z.com/feed/` |
| Sequoia | Web scrape | Parse `https://www.sequoiacap.com/our-thinking/` for article links + titles |
| Y Combinator | HN Algolia API | `https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30` |
| MIT Tech Review | RSS feed | `https://www.technologyreview.com/feed/` |
| Product Hunt | Web scrape | Parse `https://www.producthunt.com` for top posts by upvote |
| HF Papers | Web scrape | Parse `https://huggingface.co/papers` for daily paper cards |

**Interface:**

```python
def fetch_all_sources(days_back: int = 7) -> dict[str, list[dict]]:
    """
    Returns a dict keyed by source_id.
    Each value is a list of article dicts with keys:
      title: str
      url: str
      description: str  # snippet, abstract, or first 200 chars
      published_at: str  # ISO 8601 or empty string
      source: str        # display name
    """
```

**Requirements:**
- Use `requests` + `feedparser` + `beautifulsoup4`.
- Set a `User-Agent` header on all requests: `"WeeklySignalBriefing/1.0"`.
- Use `days_back` to filter out articles older than N days. Default 7.
- Catch exceptions per source. A failing source must not crash the whole run. Log the error and return an empty list for that source.
- Respect rate limits with `time.sleep(1)` between requests to the same domain.
- Cap at 20 articles per source to stay within token limits.

---

### Module 2: `src/analyser.py`

**Purpose:** Send scraped content to Claude API, get back structured briefing JSON.

**Interface:**

```python
def analyse(raw_articles: dict[str, list[dict]]) -> dict:
    """
    Calls Claude API with web_search tool enabled.
    Returns a validated BriefingDict matching the schema in Section 3.3.
    """
```

**Claude API call spec:**

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

response = client.messages.create(
    model="claude-opus-4-5",       # use opus for quality
    max_tokens=8000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{"role": "user", "content": build_prompt(raw_articles)}]
)
```

**Prompt construction (`build_prompt`):**

The prompt must instruct the model to:

1. Use the supplied raw articles as the primary data source.
2. Use web_search to fill gaps, verify facts, and find URLs that were missing.
3. Return ONLY valid JSON. No markdown. No preamble. Start with `{` end with `}`.
4. Match the exact schema:

```
{
  "weekly_theme": "string",
  "theme_context": "string",
  "generated_at": "ISO 8601 timestamp",
  "week_of": "YYYY-MM-DD of the Monday of this week",
  "categories": [
    {
      "id": "products | ai_research | business | trends | signals",
      "name": "string",
      "items": [ ...per Section 3.3... ]
    }
  ],
  "top_signals": [
    {
      "headline": "string",
      "why_it_matters": "string",
      "urgency": "act_now | watch_closely | stay_informed"
    }
  ]
}
```

**Response parsing:**

- Extract all `text` blocks from `response.content`.
- Find the JSON substring: `text[text.index('{'):text.rindex('}')+1]`.
- Parse with `json.loads()`.
- Validate required keys are present. Raise `ValueError` with a clear message if not.
- Retry once on parse failure before raising.

---

### Module 3: `src/renderer.py`

**Purpose:** Transform BriefingDict into HTML, Markdown, and JSON files.

**Interface:**

```python
def render_html(briefing: dict) -> str:
    """Returns complete HTML as a string."""

def render_markdown(briefing: dict) -> str:
    """Returns Markdown as a string."""

def render_json(briefing: dict) -> str:
    """Returns pretty-printed JSON as a string."""
```

**HTML design spec:**

The HTML page must be:
- **Self-contained** — all CSS and JS inline. No external dependencies at runtime.
- **Mobile-friendly** — responsive at 375px, 768px, and 1280px.
- **Dark-mode aware** — uses `prefers-color-scheme: dark` media query.
- **Printable** — `@media print` hides nav, collapses padding.

**Visual design rules:**

| Element | Spec |
|---------|------|
| Font family | `'Inter', system-ui, sans-serif` (loaded from Google Fonts) |
| Background | `#F8F7F2` light / `#0F0F0F` dark |
| Card background | `#FFFFFF` light / `#1A1A1A` dark |
| Card border | `1px solid #E8E6DF` light / `1px solid #2A2A2A` dark |
| Card border radius | `8px` |
| Primary text | `#1A1A1A` light / `#F0EEE8` dark |
| Secondary text | `#6B6860` light / `#888680` dark |
| Max content width | `960px` centered |
| Category left border | Category colour (see Section 3.2), `3px` width |
| Signal dots | 7px circles, filled or hollow per signal level |
| Source badge | Category colour at 15% opacity background, category colour text |

**Header spec:**

```html
<header>
  <div class="week-label">WEEK {week_number} · {date_range}</div>
  <h1>{weekly_theme}</h1>
  <p class="context">{theme_context}</p>
  <div class="meta-row">
    <span>{total_items} items</span>
    <span>{high_signal_count} high signal</span>
    <span>Generated {generated_at}</span>
  </div>
</header>
```

**Metric cards spec (3 cards, horizontal row):**

- Total items scanned
- High signal items (count)
- Sources monitored (always 7)

**Category section spec (repeat for each of 5 categories):**

```html
<section class="category" data-category="{id}">
  <div class="category-header">
    <div class="category-stripe" style="background:{colour}"></div>
    <h2>{name}</h2>
    <span class="item-count">{count} items</span>
  </div>
  <div class="items-grid">
    <!-- one card per item -->
    <article class="item-card">
      <div class="item-header">
        <a href="{url}" class="item-title">{title}</a>
        <div class="signal-dots" data-level="{signal}"></div>
      </div>
      <p class="item-summary">{summary}</p>
      <div class="item-meta">
        <span class="source-badge" style="...">{source}</span>
        <!-- tags -->
        <span class="tag">{tag}</span>
      </div>
    </article>
  </div>
</section>
```

**Top signals panel spec:**

```html
<section class="top-signals">
  <h2>Top Signals This Week</h2>
  <div class="signals-list">
    <!-- one row per signal -->
    <div class="signal-row">
      <div class="signal-number" style="background:{urgency_colour}">{index}</div>
      <div class="signal-body">
        <div class="signal-headline">{headline}</div>
        <div class="signal-detail">{why_it_matters}</div>
        <span class="urgency-badge" style="...">{urgency_label}</span>
      </div>
    </div>
  </div>
</section>
```

**Footer spec:**

```html
<footer>
  <div>Sources: TechCrunch · a16z · Sequoia · Y Combinator · MIT Tech Review · Product Hunt · HF Papers</div>
  <div>Generated by Weekly Signal Briefing · {generated_at}</div>
</footer>
```

**Markdown output spec:**

```markdown
# Weekly Signal Briefing — Week {N}, {date_range}

> {weekly_theme}

{theme_context}

---

## {category_name}

### {item_title}
**Source:** {source} | **Signal:** {signal}

{summary}

[Read more →]({url})

---

## Top Signals

### 1. {headline}
**Urgency:** {urgency_label}

{why_it_matters}
```

---

### Module 4: `src/publisher.py`

**Purpose:** Write output files and optionally push to GitHub Pages.

**Interface:**

```python
def write_local(outputs: dict[str, str], output_dir: str = "output") -> None:
    """Writes index.html, briefing.json, briefing.md to output_dir."""

def publish_to_github(output_dir: str = "output") -> None:
    """
    Commits and pushes output_dir contents to the gh-pages branch.
    Called automatically by GitHub Actions. Skip if not in CI.
    """
```

**Local write spec:**
- Create `output/` directory if it does not exist.
- Write `index.html`, `briefing.json`, `briefing.md`.
- Also write `output/archive/{YYYY-MM-DD}/index.html` to preserve history.

**GitHub Pages publish spec:**
- Use `ghp-import` Python package to push `output/` to `gh-pages` branch.
- Only run this if `CI=true` environment variable is present.
- Print the public URL on success: `https://{github_username}.github.io/{repo_name}/`.

---

### Module 5: `generate.py` (entrypoint)

```python
#!/usr/bin/env python3
"""
Weekly Signal Briefing — Main entrypoint.

Usage:
    python generate.py                # full run
    python generate.py --dry-run      # generate locally, don't publish
    python generate.py --days-back 14 # look back 14 days instead of 7
    python generate.py --skip-scrape  # use cached raw_articles.json if present
"""

import argparse
import json
import logging
from pathlib import Path
from src.scraper import fetch_all_sources
from src.analyser import analyse
from src.renderer import render_html, render_markdown, render_json
from src.publisher import write_local, publish_to_github

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--days-back", type=int, default=7)
    parser.add_argument("--skip-scrape", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log = logging.getLogger(__name__)

    # Step 1: Scrape
    if args.skip_scrape and Path("output/raw_articles.json").exists():
        log.info("Using cached raw_articles.json")
        raw = json.loads(Path("output/raw_articles.json").read_text())
    else:
        log.info("Fetching sources...")
        raw = fetch_all_sources(days_back=args.days_back)
        Path("output").mkdir(exist_ok=True)
        Path("output/raw_articles.json").write_text(json.dumps(raw, indent=2))
        log.info(f"Fetched {sum(len(v) for v in raw.values())} articles")

    # Step 2: Analyse
    log.info("Calling Claude API...")
    briefing = analyse(raw)
    log.info("Analysis complete")

    # Step 3: Render
    outputs = {
        "index.html": render_html(briefing),
        "briefing.json": render_json(briefing),
        "briefing.md": render_markdown(briefing),
    }

    # Step 4: Publish
    write_local(outputs)
    if not args.dry_run:
        publish_to_github()
    else:
        log.info("Dry run. Skipping GitHub publish.")
        log.info("Open output/index.html in your browser to preview.")

if __name__ == "__main__":
    main()
```

---

### Module 6: `.github/workflows/briefing.yml`

```yaml
name: Weekly Signal Briefing

on:
  schedule:
    - cron: '0 20 * * SUN'   # Sunday 8pm UTC = Monday 7am AEST
  workflow_dispatch:           # Manual trigger from GitHub UI

permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  generate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate briefing
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          CI: true
        run: python generate.py

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./output
          keep_files: false
          commit_message: "briefing: week ${{ github.run_number }}"
```

---

## 7. Dependencies (`requirements.txt`)

```
anthropic>=0.40.0
requests>=2.31.0
feedparser>=6.0.10
beautifulsoup4>=4.12.0
lxml>=5.0.0
jinja2>=3.1.0
python-dotenv>=1.0.0
ghp-import>=2.1.0
```

---

## 8. Environment Variables

Create `.env` for local development (never commit this file):

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...         # Required
GITHUB_USERNAME=your-github-username  # Required for publish URL
REPO_NAME=weekly-signal-briefing      # Required for publish URL
```

Create `.env.example` (commit this):

```bash
ANTHROPIC_API_KEY=your_key_here
GITHUB_USERNAME=your_github_username
REPO_NAME=weekly-signal-briefing
```

---

## 9. Acceptance Tests

The build is complete when all of the following pass.

### 9.1 Unit tests (`pytest tests/`)

**`test_scraper.py`**
- [ ] `fetch_all_sources()` returns a dict with exactly 7 keys.
- [ ] Each value is a list (empty list is acceptable, not None).
- [ ] Each article dict has keys: `title`, `url`, `description`, `published_at`, `source`.
- [ ] A single failing source does not raise an exception.

**`test_analyser.py`**
- [ ] `analyse()` returns a dict with keys: `weekly_theme`, `categories`, `top_signals`.
- [ ] `categories` has exactly 5 items.
- [ ] Each category has `id`, `name`, `items`.
- [ ] Each item has `title`, `source`, `url`, `summary`, `signal`, `tags`.
- [ ] `signal` is one of `high`, `medium`, `low`.

**`test_renderer.py`**
- [ ] `render_html()` returns a string starting with `<!DOCTYPE html>`.
- [ ] HTML contains all 5 category IDs.
- [ ] HTML contains the `weekly_theme` string.
- [ ] `render_markdown()` returns a string containing `## `.
- [ ] `render_json()` is valid JSON parseable by `json.loads()`.

### 9.2 Manual checks (human review)

- [ ] Run `python generate.py --dry-run`. It completes without error.
- [ ] Open `output/index.html` in a browser. All 5 categories are visible.
- [ ] Each item card shows: title, source badge, signal dots, summary, tags.
- [ ] Top signals panel shows 3–5 signals with urgency badges.
- [ ] Page is readable on mobile (375px viewport).
- [ ] Dark mode renders correctly (enable in OS settings).
- [ ] All links in the page are real URLs (not empty href).

### 9.3 Automation checks

- [ ] Push to `main` and trigger workflow manually from GitHub Actions UI.
- [ ] Workflow completes in under 5 minutes.
- [ ] GitHub Pages URL is accessible publicly.
- [ ] Archive directory is created at `output/archive/{date}/index.html`.

---

## 10. Setup Instructions for Implementer

Follow these steps in order:

```bash
# 1. Clone or create the repo
git clone https://github.com/YOUR_USERNAME/weekly-signal-briefing.git
cd weekly-signal-briefing

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 4. Run locally
python generate.py --dry-run

# 5. Open preview
open output/index.html  # macOS
xdg-open output/index.html  # Linux

# 6. Set up GitHub repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/weekly-signal-briefing.git
git push -u origin main

# 7. Add secret in GitHub
# Go to: Settings > Secrets and variables > Actions > New repository secret
# Name: ANTHROPIC_API_KEY
# Value: sk-ant-...

# 8. Enable GitHub Pages
# Go to: Settings > Pages > Source: Deploy from gh-pages branch

# 9. Trigger first run
# Go to: Actions > Weekly Signal Briefing > Run workflow
```

---

## 11. Extension Points (do not build now, document for future)

These are known future features. Do not implement them in v1. Document them as `# TODO:` comments in the relevant modules.

| Feature | Module | Notes |
|---------|--------|-------|
| Email newsletter delivery | `publisher.py` | Integrate Resend or SendGrid API |
| Slack/Discord webhook | `publisher.py` | Post summary + link to channel |
| Custom source addition | `scraper.py` | Accept `sources.json` config file |
| Keyword filtering | `analyser.py` | Focus briefing on topics relevant to owner |
| Historical archive page | `renderer.py` | Index of all past briefings |
| RSS feed output | `renderer.py` | Generate `feed.xml` alongside `index.html` |
| Notion publish | `publisher.py` | Push structured data to a Notion database |

---

## 12. Known Constraints and Decisions

| Decision | Rationale |
|----------|-----------|
| Single Python file per module | Keeps the codebase readable for a solo operator |
| No database | Output files are the source of truth. Git history is the archive. |
| Claude Opus for analysis | Quality over cost. Each run costs ~$0.10–0.30 AUD at current pricing. |
| `ghp-import` for deployment | Simpler than the GitHub Pages Action. Zero config. |
| Jinja2 for HTML | Separates template from logic. Easy to redesign without touching Python. |
| `--skip-scrape` flag | Allows re-running analysis without re-hitting all sources. Saves time during testing. |
| 7-day lookback default | Matches weekly cadence. Use `--days-back 14` for first run to backfill. |

---

*End of spec. Total implementation: approximately 600–900 lines of Python + 1 HTML template + 1 GitHub Actions YAML.*
