"""Write output files for GitHub Pages deployment via Actions."""

from __future__ import annotations

import logging
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
