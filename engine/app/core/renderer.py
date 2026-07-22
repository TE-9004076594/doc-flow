"""Document renderer - generates documents by replacing variables in templates."""

import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Optional

from docx import Document as DocxDocument
from docx.oxml.ns import qn

from .template_parser import (
    VARIABLE_PATTERN, IF_BLOCK_START, IF_BLOCK_ELSE, IF_BLOCK_END,
    EACH_BLOCK_START, EACH_BLOCK_END,
)
from .logic_blocks import evaluate_condition


def generate_document(
    template_path: str,
    variables: dict[str, Any],
    output_path: str,
) -> str:
    """Generate a document from a template by replacing variables and processing logic blocks.

    Returns the output path of the generated document.
    """
    # Copy template to preserve original
    shutil.copy2(template_path, output_path)

    doc = DocxDocument(output_path)

    # Process paragraphs
    for para in doc.paragraphs:
        _process_paragraph(para, variables)

    # Process tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    _process_paragraph(para, variables)

    doc.save(output_path)
    return output_path


def _process_paragraph(para, variables: dict[str, Any]) -> None:
    """Replace variables in a single paragraph's XML."""
    if not para.text:
        return

    # Simple variable replacement in runs
    for run in para.runs:
        if VARIABLE_PATTERN.search(run.text):
            run.text = _replace_variables_in_text(run.text, variables)

    # Also process the paragraph-level XML for blocks that span multiple runs
    xml = para._element.xml if hasattr(para, '_element') else ""
    if '{{' in (para.text or ""):
        _replace_in_paragraph_xml(para, variables)


def _replace_variables_in_text(text: str, variables: dict[str, Any]) -> str:
    """Replace {{variable}} patterns in text with actual values."""
    def replacer(match):
        var_name = match.group(1).strip()
        # Skip if it's a block tag (starts with # or /)
        if var_name.startswith("#") or var_name.startswith("/") or var_name == "else":
            return match.group(0)
        value = _resolve_variable(var_name, variables)
        return str(value) if value is not None else match.group(0)
    return VARIABLE_PATTERN.sub(replacer, text)


def _replace_in_paragraph_xml(para, variables: dict[str, Any]) -> None:
    """Replace variables at the paragraph XML level for multi-run variables."""
    for run in para.runs:
        run.text = _replace_variables_in_text(run.text, variables)


def _resolve_variable(name: str, variables: dict) -> Any:
    """Resolve a variable with dot-notation support."""
    parts = name.split(".")
    value = variables
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
        elif isinstance(value, list) and part.isdigit():
            value = value[int(part)]
        else:
            return None
    return value


def detect_unresolved_placeholders(output_path: str) -> list[str]:
    """Check generated document for unresolved {{placeholders}}."""
    doc = DocxDocument(output_path)
    text_parts = []
    for para in doc.paragraphs:
        text_parts.append(para.text or "")
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    text_parts.append(para.text or "")

    all_text = "\n".join(text_parts)
    found = VARIABLE_PATTERN.findall(all_text)
    return [v.strip() for v in found if not v.strip().startswith("#") and v.strip() != "else"]
