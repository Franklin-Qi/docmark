"""CLI for DocMark."""

from __future__ import annotations

from pathlib import Path

import click

from docmark import __version__
from docmark.convert import convert_path


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Output .md file or directory. Default: next to the input file.",
)
@click.option(
    "--overwrite/--no-overwrite",
    default=True,
    show_default=True,
    help="Overwrite an existing Markdown file.",
)
@click.version_option(__version__, prog_name="docmark")
def main(input_path: Path, output_path: Path | None, overwrite: bool) -> None:
    """Convert DOC, DOCX, PDF, and more into clean, editable Markdown.

    Images are written into the same directory as the output Markdown file,
    using relative links such as ``![...](image_001.png)``.
    """
    results = convert_path(input_path, output_path, overwrite=overwrite)
    for result in results:
        click.echo(f"Wrote {result.markdown_path}")
        if result.images:
            click.echo(f"  images: {len(result.images)} -> {result.markdown_path.parent}")


if __name__ == "__main__":
    main()
