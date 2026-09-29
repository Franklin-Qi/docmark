"""Legacy .doc converter.

Tries pandoc first. If that fails, converts to DOCX with LibreOffice/soffice
when available, then converts the DOCX.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from docmark.converters.pandoc_util import PandocError, convert_with_pandoc


class DocConverter:
    extensions = (".doc",)

    def convert(self, input_path: Path, markdown_path: Path) -> list[Path]:
        try:
            return convert_with_pandoc(input_path, markdown_path, from_format="doc")
        except PandocError:
            docx_path = self._to_docx_via_libreoffice(input_path)
            try:
                return convert_with_pandoc(docx_path, markdown_path, from_format="docx")
            finally:
                if docx_path.exists():
                    docx_path.unlink(missing_ok=True)
                    # LibreOffice may create the file in a temp dir we own.
                    parent = docx_path.parent
                    if parent.name.startswith("docmark-doc-") and parent.exists():
                        shutil.rmtree(parent, ignore_errors=True)

    def _to_docx_via_libreoffice(self, input_path: Path) -> Path:
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if not soffice:
            raise PandocError(
                "Cannot convert .doc: pandoc failed and LibreOffice/soffice "
                "was not found. Install LibreOffice or convert the file to "
                ".docx first."
            )

        out_dir = Path(tempfile.mkdtemp(prefix="docmark-doc-"))
        completed = subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "docx",
                "--outdir",
                str(out_dir),
                str(input_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        docx_path = out_dir / f"{input_path.stem}.docx"
        if completed.returncode != 0 or not docx_path.exists():
            detail = (completed.stderr or completed.stdout or "").strip()
            shutil.rmtree(out_dir, ignore_errors=True)
            raise PandocError(
                f"LibreOffice failed to convert {input_path.name} to DOCX"
                + (f": {detail}" if detail else "")
            )
        return docx_path
