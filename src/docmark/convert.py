"""Public conversion API."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from docmark.converters.registry import get_converter, supported_extensions


@dataclass
class ConvertResult:
    """Outcome of a single file conversion."""

    source_path: Path
    markdown_path: Path
    images: list[Path] = field(default_factory=list)


def convert_file(
    input_path: Path,
    output_path: Path | None = None,
    *,
    overwrite: bool = True,
) -> ConvertResult:
    """Convert one document into Markdown.

    Images extracted from the document are saved in the same directory as the
    output Markdown file. Markdown image links use bare filenames.
    """
    input_path = input_path.expanduser().resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Not a file: {input_path}")

    converter = get_converter(input_path.suffix)
    markdown_path = _resolve_output_path(input_path, output_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    if markdown_path.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {markdown_path}")

    images = converter.convert(input_path, markdown_path)
    return ConvertResult(
        source_path=input_path,
        markdown_path=markdown_path,
        images=images,
    )


def convert_path(
    input_path: Path,
    output_path: Path | None = None,
    *,
    overwrite: bool = True,
) -> list[ConvertResult]:
    """Convert a file, or every supported file under a directory."""
    input_path = input_path.expanduser().resolve()

    if input_path.is_file():
        return [convert_file(input_path, output_path, overwrite=overwrite)]

    if not input_path.is_dir():
        raise FileNotFoundError(f"Path not found: {input_path}")

    extensions = supported_extensions()
    sources = sorted(
        p
        for p in input_path.rglob("*")
        if p.is_file() and p.suffix.lower() in extensions
    )
    if not sources:
        raise FileNotFoundError(
            f"No supported documents found under {input_path}. "
            f"Supported: {', '.join(sorted(extensions))}"
        )

    results: list[ConvertResult] = []
    for source in sources:
        relative = source.relative_to(input_path)
        if output_path is None:
            target = source.with_suffix(".md")
        else:
            out_root = output_path.expanduser().resolve()
            target = out_root / relative.with_suffix(".md")
        results.append(convert_file(source, target, overwrite=overwrite))
    return results


def _resolve_output_path(input_path: Path, output_path: Path | None) -> Path:
    if output_path is None:
        return input_path.with_suffix(".md")

    output_path = output_path.expanduser().resolve()
    if output_path.suffix.lower() == ".md" or (
        not output_path.exists() and output_path.suffix != ""
    ):
        return output_path

    # Treat as directory (existing dir, or path without .md suffix).
    return output_path / f"{input_path.stem}.md"
