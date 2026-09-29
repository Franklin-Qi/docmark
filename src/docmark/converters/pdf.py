"""PDF converter via PyMuPDF with images saved beside the Markdown file."""

from __future__ import annotations

from pathlib import Path

import pymupdf

from docmark.converters.base import write_markdown
from docmark.media import write_image_bytes


class PdfConverter:
    extensions = (".pdf",)

    def convert(self, input_path: Path, markdown_path: Path) -> list[Path]:
        output_dir = markdown_path.parent
        stem = markdown_path.stem
        images: list[Path] = []
        blocks: list[str] = []
        image_index = 1

        with pymupdf.open(input_path) as doc:
            for page_number, page in enumerate(doc, start=1):
                page_lines: list[str] = []
                text = page.get_text("text").strip()
                if text:
                    page_lines.append(text)

                for img in page.get_images(full=True):
                    xref = img[0]
                    try:
                        extracted = doc.extract_image(xref)
                    except Exception:
                        continue
                    image_bytes = extracted.get("image")
                    if not image_bytes:
                        continue
                    ext = extracted.get("ext") or "png"
                    saved = write_image_bytes(
                        image_bytes,
                        output_dir,
                        stem=stem,
                        index=image_index,
                        suffix=ext,
                    )
                    images.append(saved)
                    page_lines.append(f"![]({saved.name})")
                    image_index += 1

                if page_lines:
                    if page_number > 1:
                        blocks.append("")
                        blocks.append(f"<!-- page {page_number} -->")
                        blocks.append("")
                    blocks.append("\n\n".join(page_lines))

        write_markdown(markdown_path, "\n".join(blocks).strip())
        return images
