"""PDF conversion service using LibreOffice headless."""

import subprocess
import os
from pathlib import Path
from typing import Optional


def convert_to_pdf(docx_path: str, output_dir: Optional[str] = None) -> str:
    """Convert a .docx file to PDF using LibreOffice headless.

    Args:
        docx_path: Path to the source .docx file.
        output_dir: Directory for the output PDF. Defaults to same directory as input.

    Returns:
        Path to the generated PDF file.

    Raises:
        RuntimeError: If conversion fails.
    """
    docx_file = Path(docx_path)
    if not docx_file.exists():
        raise FileNotFoundError(f"Document not found: {docx_path}")

    out_dir = output_dir or str(docx_file.parent)
    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)

    # LibreOffice converts to PDF and saves to the output directory
    result = subprocess.run(
        [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(out_dir_path),
            str(docx_file),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(f"PDF conversion failed: {result.stderr.strip()}")

    pdf_path = out_dir_path / f"{docx_file.stem}.pdf"
    if not pdf_path.exists():
        # Try alternate naming
        pdf_path = out_dir_path / docx_file.with_suffix(".pdf").name

    return str(pdf_path)
