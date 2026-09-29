# DocMark

Convert DOC, DOCX, PDF, and more into clean, editable Markdown.

Images extracted from a document are written into **the same directory** as the
output Markdown file and referenced with relative filenames:

```markdown
![Diagram](report_img_001.png)
```

## Features

- **DOCX / DOC** via [pandoc](https://pandoc.org/) (DOC falls back to LibreOffice when needed)
- **PDF** via [PyMuPDF](https://pymupdf.readthedocs.io/) with embedded image extraction
- **Also**: HTML, ODT, RTF, EPUB, RST, LaTeX, Org, and Markdown (through pandoc)
- CLI for single files or whole directories
- Images always sit beside the `.md` output (no nested `media/` folder in the final result)

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
# Convert one file (writes report.md next to report.docx)
docmark report.docx

# Choose output path; images go into the same folder as the .md
docmark report.pdf -o out/report.md

# Convert every supported file under a directory
docmark ./docs -o ./markdown-out
```

Python API:

```python
from pathlib import Path
from docmark import convert_file

result = convert_file(Path("report.docx"), Path("out/report.md"))
print(result.markdown_path)
print(result.images)  # paths beside the markdown file
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
├── pyproject.toml
└── README.md
```

## Notes

- PDF text layout is best-effort; complex multi-column pages may need manual cleanup.
- Output Markdown aims to be editable GFM-style text, not a pixel-perfect replica.

## License

MIT
