"""Converter protocol and shared helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class Converter(Protocol):
    """Convert a source document into Markdown next to extracted images."""

    extensions: tuple[str, ...]

    def convert(self, input_path: Path, markdown_path: Path) -> list[Path]:
        """Write Markdown to ``markdown_path`` and return saved image paths.

        Images must be written into ``markdown_path.parent`` and referenced
        from Markdown by filename only (same directory).
        """


def write_markdown(markdown_path: Path, content: str) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    text = content.strip() + "\n"
    markdown_path.write_text(text, encoding="utf-8")
