"""Shared pandoc invocation helpers."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from docmark.converters.base import write_markdown
from docmark.media import flatten_extracted_media


class PandocError(RuntimeError):
    """Raised when pandoc is missing or conversion fails."""


def require_pandoc() -> str:
    path = shutil.which("pandoc")
    if not path:
        raise PandocError(
            "pandoc is required for this format. "
            "Install it from https://pandoc.org/ and ensure it is on PATH."
        )
    return path


def convert_with_pandoc(
    input_path: Path,
    markdown_path: Path,
    *,
    from_format: str | None = None,
    extra_args: list[str] | None = None,
) -> list[Path]:
    """Convert via pandoc and place images beside the Markdown file."""
    pandoc = require_pandoc()
    output_dir = markdown_path.parent

    with tempfile.TemporaryDirectory(prefix="docmark-media-") as tmp:
        media_root = Path(tmp) / "media"
        media_root.mkdir(parents=True, exist_ok=True)

        cmd = [
            pandoc,
            str(input_path),
            "-t",
            "gfm",
            "--wrap=none",
            f"--extract-media={media_root.parent}",
        ]
        if from_format:
            cmd.extend(["-f", from_format])
        if extra_args:
            cmd.extend(extra_args)

        completed = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            raise PandocError(
                f"pandoc failed for {input_path.name}"
                + (f": {detail}" if detail else "")
            )

        markdown, images = flatten_extracted_media(
            completed.stdout,
            media_root.parent,
            output_dir,
            "img",
        )
        write_markdown(markdown_path, markdown)
        return images
