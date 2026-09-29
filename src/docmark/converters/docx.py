"""DOCX converter (via pandoc)."""

from __future__ import annotations

from pathlib import Path

from docmark.converters.pandoc_util import convert_with_pandoc


class DocxConverter:
    extensions = (".docx",)

    def convert(self, input_path: Path, markdown_path: Path) -> list[Path]:
        return convert_with_pandoc(input_path, markdown_path, from_format="docx")
