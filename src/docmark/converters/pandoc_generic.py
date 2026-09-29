"""Extra formats handled through pandoc (HTML, ODT, RTF, EPUB, ...)."""

from __future__ import annotations

from pathlib import Path

from docmark.converters.pandoc_util import convert_with_pandoc

# Explicit from-format hints where pandoc benefits from them.
_FORMAT_HINTS = {
    ".html": "html",
    ".htm": "html",
    ".odt": "odt",
    ".rtf": "rtf",
    ".epub": "epub",
    ".markdown": "markdown",
    ".md": "markdown",
    ".rst": "rst",
    ".tex": "latex",
    ".org": "org",
}


class PandocGenericConverter:
    extensions = tuple(_FORMAT_HINTS.keys())

    def convert(self, input_path: Path, markdown_path: Path) -> list[Path]:
        suffix = input_path.suffix.lower()
        from_format = _FORMAT_HINTS.get(suffix)
        return convert_with_pandoc(
            input_path,
            markdown_path,
            from_format=from_format,
        )
