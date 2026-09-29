"""Map file extensions to converter implementations."""

from __future__ import annotations

from docmark.converters.base import Converter
from docmark.converters.doc import DocConverter
from docmark.converters.docx import DocxConverter
from docmark.converters.pandoc_generic import PandocGenericConverter
from docmark.converters.pdf import PdfConverter

_CONVERTERS: list[Converter] = [
    DocxConverter(),
    DocConverter(),
    PdfConverter(),
    PandocGenericConverter(),
]

_REGISTRY: dict[str, Converter] = {}
for _converter in _CONVERTERS:
    for _ext in _converter.extensions:
        _REGISTRY[_ext.lower()] = _converter


def get_converter(suffix: str) -> Converter:
    key = suffix.lower() if suffix.startswith(".") else f".{suffix.lower()}"
    try:
        return _REGISTRY[key]
    except KeyError as exc:
        supported = ", ".join(sorted(supported_extensions()))
        raise ValueError(
            f"Unsupported file type: {suffix or '(none)'}. Supported: {supported}"
        ) from exc


def supported_extensions() -> set[str]:
    return set(_REGISTRY.keys())
