#!/usr/bin/env python3
"""
Weekly Tech Update — Main entrypoint.

Usage:
    python generate.py                # full run
    python generate.py --dry-run      # generate locally, don't publish
    python generate.py --days-back 14 # look back 14 days instead of 7
    python generate.py --skip-scrape  # use cached raw_articles.json if present
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from src.analyser import analyse
from src.audit import audit_briefing
from src.publisher import publish_to_github, write_local
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
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    log = logging.getLogger(__name__)

    cache_path = Path("output/raw_articles.json")

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
        log.warning("Audit failed with %d critical issues; retrying analyse once", len(critical))
        briefing = analyse(raw, audit_feedback=feedback)
        audit_result = audit_briefing(briefing)
        log.info(
            "Re-audit: passed=%s scores=%s",
            audit_result["passed"],
            audit_result["scores"],
        )

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
