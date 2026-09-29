"""DocMark — convert documents into clean, editable Markdown."""

from docmark.convert import ConvertResult, convert_file, convert_path

__version__ = "0.1.0"
__all__ = [
    "ConvertResult",
    "convert_file",
    "convert_path",
    "__version__",
]
