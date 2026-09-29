# DocMark

Convert DOC, DOCX, PDF, and more into clean, editable Markdown.

Each conversion creates a **dedicated folder** for that document. Markdown and
images live together inside it:

```text
output/report/
├── report.md
├── img_001.png
└── img_002.png
```

```markdown
![Diagram](img_001.png)
```

## Features

- **DOCX / DOC** via [pandoc](https://pandoc.org/) (DOC falls back to LibreOffice when needed)
- **PDF** via [PyMuPDF](https://pymupdf.readthedocs.io/) with embedded image extraction
- **Also**: HTML, ODT, RTF, EPUB, RST, LaTeX, Org, and Markdown (through pandoc)
- CLI for single files or whole directories
- Default output under `./output/<name>/` (not scattered next to the source)

## Requirements

- Python 3.10+
- [pandoc](https://pandoc.org/installing.html) on `PATH` (for Office and most non-PDF formats)
- Optional: LibreOffice (`soffice`) for stubborn legacy `.doc` files

## Install

```bash
cd docmark
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
# Convert one file → ./output/report/report.md (+ images in the same folder)
docmark report.docx

# Parent directory: still creates a per-document subfolder
docmark report.pdf -o ./exports
# → ./exports/report/report.md

# Explicit Markdown path (images beside that file)
docmark report.pdf -o ./exports/custom.md

# Convert every supported file under a directory
docmark ./docs -o ./markdown-out
```

Python API:

```python
from pathlib import Path
from docmark import convert_file

result = convert_file(Path("report.docx"))  # → output/report/report.md
print(result.markdown_path)
print(result.images)
```

## Project layout

```text
docmark/
├── src/docmark/
│   ├── cli.py              # CLI entry
│   ├── convert.py          # public API
│   ├── media.py            # image co-location helpers
│   └── converters/         # format-specific converters
├── tests/
├── examples/
├── output/                 # default conversion results (gitignored)
├── pyproject.toml
└── README.md
```

## Notes

- PDF text layout is best-effort; complex multi-column pages may need manual cleanup.
- Output Markdown aims to be editable GFM-style text, not a pixel-perfect replica.

## License

MIT
