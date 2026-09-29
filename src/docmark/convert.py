"""Public conversion API."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from docmark.converters.registry import get_converter, supported_extensions

DEFAULT_OUTPUT_ROOT = Path("output")


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

    By default each document gets its own folder under ``./output/<stem>/``,
    containing ``<stem>.md`` and any extracted images (same directory).
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
        target = _resolve_batch_output_path(relative, source.stem, output_path)
        results.append(convert_file(source, target, overwrite=overwrite))
    return results


def output_bundle_dir(stem: str, parent: Path | None = None) -> Path:
    """Return the dedicated folder for one document's Markdown + images."""
    root = parent if parent is not None else (Path.cwd() / DEFAULT_OUTPUT_ROOT)
    return root / stem


def _resolve_output_path(input_path: Path, output_path: Path | None) -> Path:
    stem = input_path.stem

    if output_path is None:
        return output_bundle_dir(stem) / f"{stem}.md"

    output_path = output_path.expanduser().resolve()

    # Explicit Markdown file: images still go beside it.
    if output_path.suffix.lower() == ".md":
        return output_path

    # Directory (or non-.md path): create a per-document subfolder.
    return output_bundle_dir(stem, parent=output_path) / f"{stem}.md"


def _resolve_batch_output_path(
    relative: Path,
    stem: str,
    output_path: Path | None,
) -> Path:
    """Map a relative source path to ``.../<rel-stem>/<name>.md``."""
    bundle = relative.with_suffix("")  # e.g. docs/a/report.docx -> docs/a/report
    if output_path is None:
        parent = Path.cwd() / DEFAULT_OUTPUT_ROOT / bundle
    else:
        parent = output_path.expanduser().resolve() / bundle
    return parent / f"{stem}.md"
