# Weekly Tech Update

**Weekly AI Strategy Briefing** — an automated intelligence document that shows where the AI market is heading, how investors are positioning, what companies are shipping, and which opportunities are opening across short, mid, and long horizons.

**Live URL:** https://arashatash.github.io/Weekly-Tech-Update/

## What it is

This is a **strategy document**, not a general tech news digest. Each week it:

1. Scrapes 7 frontier sources (TechCrunch, a16z, Sequoia, Hacker News, MIT Tech Review, Product Hunt, Hugging Face Papers)
2. Sends content to Claude (Opus 4.7 + web search) with a strict AI-only filter
3. Publishes a styled HTML briefing to GitHub Pages every Sunday 20:00 UTC (Monday 7am AEST)

## Three lenses (5 categories)

| Category | Lens |
|----------|------|
| **Capital & Theses** | How investors see and believe — rounds, theses, where smart money moves |
| **What's Being Built** | How companies tackle problems — models, agents, enterprise rollouts, infra |
| **Opportunities Now** | 0–6 month plays you can move on this quarter |
| **Opportunities Mid-term** | 6–18 month positioning windows and forming categories |
| **Opportunities Long-term** | 18+ month directional bets and compounding weak signals |

Plus a **Top Signals** panel with 3–5 must-not-miss items for the week.

## Leader Voices

A dedicated section surfaces what top AI/tech leaders said publicly in the last 7–14 days (via Claude web search): Jensen Huang, Satya Nadella, Sam Altman, and peers. Each entry includes stance (bullish/bearish/neutral), a sourced quote or paraphrase, and strategic implication for operators and investors.

## Product Hunt alignment

Product Hunt launches are not listed at random. The analyser selects 2–4 PH products that **directly validate** the week's capital theses or opportunity themes, with summaries that tie each pick to the thesis it supports.

## Multi-angle audit

After generation, `src/audit.py` runs automated checks: URL integrity, AI relevance blocklist, schema completeness, horizon consistency, source whitelist, and strategic depth. Critical failures trigger one re-analysis pass with audit feedback appended to the prompt.

## Quality bar — what gets in

- **AI-only:** Would a serious AI investor or operator regret missing this? If not, it is dropped.
- **Every item has a real URL** — linked title on the published page.
- **Strategic summaries** — what changed *and* what it implies for capital, company strategy, or open doors.
- **~15–20 category items + 4–8 leader voices** — no filler. SpaceX launches, generic CMS releases, and non-AI indie SaaS are excluded.

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
python generate.py --dry-run
open output/index.html
```

## CLI usage

```bash
python generate.py                # full run (publishes in CI only)
python generate.py --dry-run      # generate locally, skip GitHub publish
python generate.py --days-back 14 # look back 14 days
python generate.py --skip-scrape  # reuse output/raw_articles.json
```

## GitHub Actions

1. Push to `main`
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
│   ├── analyser.py       # Claude API + AI strategy JSON
│   ├── audit.py          # Multi-angle briefing quality checks
│   ├── renderer.py       # HTML / MD / JSON output
│   └── publisher.py      # Write files + gh-pages
├── templates/page.html   # Jinja2 HTML template
├── output/               # Generated artifacts
└── tests/
```
