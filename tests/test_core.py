"""Basic unit tests for DocMark helpers and conversion flow."""

from __future__ import annotations

from pathlib import Path

import pymupdf
import pytest

from docmark.convert import convert_file
from docmark.converters.registry import get_converter, supported_extensions
from docmark.media import flatten_extracted_media, write_image_bytes


def test_supported_extensions_include_core_formats() -> None:
    exts = supported_extensions()
    assert {".doc", ".docx", ".pdf"}.issubset(exts)


def test_get_converter_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        get_converter(".xyz")


def test_write_image_bytes_same_directory(tmp_path: Path) -> None:
    path = write_image_bytes(
        b"fake-image",
        tmp_path,
        stem="img",
        index=1,
        suffix="png",
    )
    assert path.parent == tmp_path
    assert path.name == "img_001.png"
    assert path.read_bytes() == b"fake-image"


def test_flatten_extracted_media_rewrites_links(tmp_path: Path) -> None:
    media_root = tmp_path / "extract"
    nested = media_root / "media"
    nested.mkdir(parents=True)
    (nested / "photo.png").write_bytes(b"png-bytes")

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    md = "Hello\n\n![Photo](media/photo.png)\n"
    rewritten, images = flatten_extracted_media(md, media_root, out_dir, "img")

    assert len(images) == 1
    assert images[0].parent == out_dir
    assert images[0].name == "img_001.png"
    assert "![Photo](img_001.png)" in rewritten
    assert "media/" not in rewritten


def test_default_output_uses_dedicated_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    pdf_path = tmp_path / "sample.pdf"
    _write_sample_pdf(pdf_path)

    result = convert_file(pdf_path)
    expected = tmp_path / "output" / "sample" / "sample.md"
    assert result.markdown_path == expected
    assert expected.exists()
    assert all(img.parent == expected.parent for img in result.images)


def test_output_directory_creates_per_document_subfolder(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    _write_sample_pdf(pdf_path)
    parent = tmp_path / "exports"

    result = convert_file(pdf_path, parent)
    expected = parent / "sample" / "sample.md"
    assert result.markdown_path == expected
    assert expected.exists()
    assert all(img.parent == expected.parent for img in result.images)


def test_pdf_conversion_places_images_beside_markdown(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    md_path = tmp_path / "out" / "sample.md"
    _write_sample_pdf(pdf_path)

    result = convert_file(pdf_path, md_path)
    assert result.markdown_path == md_path
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "Hello DocMark" in content
    assert result.images
    for image in result.images:
        assert image.parent == md_path.parent
        assert image.name in content


def _write_sample_pdf(pdf_path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello DocMark")
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 8, 8), 0)
    pix.set_rect(pix.irect, (255, 0, 0))
    page.insert_image(pymupdf.Rect(72, 100, 120, 148), pixmap=pix)
    doc.save(pdf_path)
    doc.close()
