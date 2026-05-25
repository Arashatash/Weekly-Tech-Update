"""Write output files and optionally push to GitHub Pages."""

from __future__ import annotations

import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)


def write_local(outputs: dict[str, str], output_dir: str = "output") -> None:
    """Writes all outputs to output_dir, preserving subdirectories."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for filename, content in outputs.items():
        path = out / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        log.info("Wrote %s", path)


def publish_to_github(output_dir: str = "output") -> None:
    """
    Commits and pushes output_dir contents to the gh-pages branch.
    Called automatically by GitHub Actions. Skip if not in CI.
    """
    if os.getenv("CI") != "true":
        log.info("Not in CI — skipping ghp-import publish")
        return

    username = os.getenv("GITHUB_USERNAME", "Arashatash")
    repo = os.getenv("REPO_NAME", "Weekly-Tech-Update")
    public_url = f"https://{username}.github.io/{repo}/"

    try:
        subprocess.run(
            [
                "ghp-import",
                output_dir,
                "-b",
                "gh-pages",
                "-m",
                f"briefing: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                "-f",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        log.info("Published to GitHub Pages: %s", public_url)
        print(f"Published: {public_url}")
    except FileNotFoundError:
        log.warning("ghp-import not found; GitHub Actions uses peaceiris/actions-gh-pages instead")
        print(f"Deploy via Actions. Public URL: {public_url}")
    except subprocess.CalledProcessError as exc:
        log.error("ghp-import failed: %s", exc.stderr)
        raise
