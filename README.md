# Weekly Tech Update

Automated weekly intelligence briefing that monitors 7 frontier tech sources, categorises signals with Claude, and publishes a styled HTML page to GitHub Pages.

**Live URL (after setup):** https://arashatash.github.io/Weekly-Tech-Update/

## What it does

1. Scrapes TechCrunch, a16z, Sequoia, Hacker News, MIT Tech Review, Product Hunt, and Hugging Face Papers
2. Sends content to Claude (Opus 4.7 + web search) for categorisation and insight extraction
3. Generates `index.html`, `briefing.json`, and `briefing.md`
4. Publishes to GitHub Pages every Sunday 20:00 UTC (Monday 7am AEST)

## Prerequisites

- Python 3.11+
- [Anthropic API key](https://platform.claude.com/settings/keys) with credits
- GitHub repo: `git@github.com:Arashatash/Weekly-Tech-Update.git`

## Setup (PowerShell)

```powershell
cd "C:\Users\arash\OneDrive\Desktop\weekly-tech-update"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...
python generate.py --dry-run
Start-Process output\index.html
```

## Setup (bash)

```bash
cd weekly-tech-update
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...
python generate.py --dry-run
open output/index.html   # macOS
xdg-open output/index.html  # Linux
```

## CLI usage

```bash
python generate.py                # full run (publishes in CI only)
python generate.py --dry-run      # generate locally, skip GitHub publish
python generate.py --days-back 14 # look back 14 days
python generate.py --skip-scrape  # reuse output/raw_articles.json
```

## GitHub Actions

1. Push this repo to `main`
2. **Settings → Secrets → Actions** → add `ANTHROPIC_API_KEY`
3. **Settings → Pages** → Source: **Deploy from branch** → `gh-pages` / `/ (root)`
4. **Actions → Weekly Signal Briefing → Run workflow** to test

## Cost

Roughly **$0.10–0.30 AUD** per weekly run with Claude Opus 4.7 and web search enabled.

## Tests

```bash
pytest tests/
```

## Project structure

```
├── generate.py           # Main entrypoint
├── src/
│   ├── scraper.py        # Source fetching
│   ├── analyser.py       # Claude API + JSON parsing
│   ├── renderer.py       # HTML / MD / JSON output
│   └── publisher.py      # Write files + gh-pages
├── templates/page.html   # Jinja2 HTML template
├── output/               # Generated artifacts
└── tests/
```
