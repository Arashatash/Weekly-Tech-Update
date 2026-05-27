#!/usr/bin/env python3
"""
Weekly Tech Update — Main entrypoint.

Usage:
    python generate.py                # full run
    python generate.py --dry-run      # generate locally, don't publish
    python generate.py --days-back 14 # look back 14 days instead of 7
    python generate.py --skip-scrape  # use cached raw_articles.json if present
    python generate.py --render-only  # re-render HTML from existing history (no API call)
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from src.analyser import analyse
from src.audit import audit_briefing
from src.publisher import write_local
from src.renderer import render_html, render_json, render_markdown
from src.scraper import fetch_all_sources

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description="Weekly Tech Update briefing generator")
    parser.add_argument("--dry-run", action="store_true", help="Skip GitHub publish")
    parser.add_argument("--days-back", type=int, default=7, help="Days to look back")
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Use cached output/raw_articles.json if present",
    )
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="Skip scrape + Claude call; re-render HTML from the latest history JSON",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    log = logging.getLogger(__name__)

    history_dir = Path("history")
    cache_path = Path("output/raw_articles.json")

    if args.render_only:
        history_dir.mkdir(exist_ok=True)
        history_files = sorted(history_dir.glob("*.json"), reverse=True)
        if not history_files:
            raise SystemExit("No history JSON found. Run a real generation first.")
        latest = history_files[0]
        log.info("Render-only mode — using %s", latest)
        briefing = json.loads(latest.read_text(encoding="utf-8"))
        _render_and_write(briefing, history_dir, log, dry_run=args.dry_run)
        return

    # Step 1: Scrape
    if args.skip_scrape and cache_path.exists():
        log.info("Using cached raw_articles.json")
        raw = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        log.info("Fetching sources...")
        raw = fetch_all_sources(days_back=args.days_back)
        Path("output").mkdir(exist_ok=True)
        cache_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        log.info("Fetched %d articles", sum(len(v) for v in raw.values()))

    # Step 2: Analyse
    log.info("Calling Claude API...")
    briefing = analyse(raw)

    audit_result = audit_briefing(briefing)
    log.info(
        "Audit: passed=%s scores=%s issues=%d",
        audit_result["passed"],
        audit_result["scores"],
        len(audit_result["issues"]),
    )
    for issue in audit_result["issues"]:
        log.log(
            logging.WARNING if issue["level"] == "warning" else logging.ERROR,
            "Audit [%s] %s: %s",
            issue["level"],
            issue["check"],
            issue["message"],
        )

    if not audit_result["passed"]:
        critical = [i for i in audit_result["issues"] if i["level"] == "critical"]
        feedback = "\n".join(
            f"- [{i['check']}] {i['message']}" for i in critical
        )
        log.warning(
            "Audit failed with %d critical issues; retrying analyse once", len(critical)
        )
        briefing = analyse(raw, audit_feedback=feedback)
        audit_result = audit_briefing(briefing)
        log.info(
            "Re-audit: passed=%s scores=%s issues=%d",
            audit_result["passed"],
            audit_result["scores"],
            len(audit_result["issues"]),
        )
        for issue in audit_result["issues"]:
            if issue["level"] == "critical":
                log.error(
                    "Re-audit [%s] %s: %s",
                    issue["level"],
                    issue["check"],
                    issue["message"],
                )

    if not audit_result["passed"]:
        critical = [i for i in audit_result["issues"] if i["level"] == "critical"]
        raise RuntimeError(
            f"Briefing failed audit after retry ({len(critical)} critical issues). "
            "Aborting before render/publish."
        )

    log.info("Analysis complete")

    # Step 3: Archive briefing JSON
    history_dir.mkdir(exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    history_path = history_dir / f"{date_str}.json"
    history_path.write_text(
        json.dumps(briefing, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    _render_and_write(briefing, history_dir, log, dry_run=args.dry_run)


def _render_and_write(
    briefing: dict,
    history_dir: Path,
    log: logging.Logger,
    *,
    dry_run: bool,
) -> None:
    """Render HTML/MD/JSON for the current + archive briefings and write output/."""
    history_menu: list[dict[str, str]] = []
    for p in history_dir.glob("*.json"):
        try:
            b = json.loads(p.read_text(encoding="utf-8"))
            history_menu.append(
                {"date": p.stem, "theme": b.get("weekly_theme", "Weekly Briefing")}
            )
        except Exception as exc:
            log.warning("Failed to load history %s: %s", p, exc)
    history_menu.sort(key=lambda x: x["date"], reverse=True)

    current_date = history_menu[0]["date"] if history_menu else ""

    outputs: dict[str, str] = {
        "index.html": render_html(
            briefing, history_menu, current_date, is_archive=False
        ),
        "briefing.json": render_json(briefing),
        "briefing.md": render_markdown(briefing),
    }

    for item in history_menu[1:]:
        b_path = history_dir / f"{item['date']}.json"
        try:
            old_b = json.loads(b_path.read_text(encoding="utf-8"))
            html = render_html(old_b, history_menu, item["date"], is_archive=True)
            outputs[f"archive/{item['date']}/index.html"] = html
        except Exception as exc:
            log.warning("Failed to render archive %s: %s", item["date"], exc)

    # GitHub Actions deploys output/ to gh-pages via peaceiris/actions-gh-pages.
    write_local(outputs)
    if dry_run:
        log.info("Dry run — outputs written locally only.")
        log.info("Open output/index.html in your browser to preview.")
    else:
        log.info("Outputs written to output/ for GitHub Pages deployment.")


if __name__ == "__main__":
    main()
