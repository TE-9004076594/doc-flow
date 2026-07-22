"""OOXML to HTML renderer for document preview."""

from docx import Document as DocxDocument
from docx.oxml.ns import qn


def render_to_html(file_path: str) -> str:
    """Convert a .docx document to HTML for web preview.

    Produces simplified HTML suitable for preview. Not pixel-perfect,
    but preserves structure, text styling, and basic formatting.
    """
    doc = DocxDocument(file_path)
    html_parts = ['<div class="doc-preview">']

    for para in doc.paragraphs:
        html_parts.append(_paragraph_to_html(para))

    for table in doc.tables:
        html_parts.append(_table_to_html(table))

    html_parts.append('</div>')
    return "\n".join(html_parts)


def _paragraph_to_html(para) -> str:
    """Convert a paragraph to HTML."""
    style = para.style.name.lower() if para.style else ""
    text = para.text or ""

    if not text.strip():
        return '<p class="empty">&nbsp;</p>'

    tag = "p"
    css_class = ""
    if "heading" in style or "title" in style:
        level = style.replace("heading", "").replace(" ", "").strip()
        if level.isdigit():
            n = min(int(level), 6)
            tag = f"h{n}"
        else:
            tag = "h2"
        css_class = "heading"

    # Build inner HTML with run-level formatting
    inner_html = ""
    for run in para.runs:
        t = run.text or ""
        if not t:
            continue
        # Wrap with formatting
        if run.bold:
            t = f"<strong>{t}</strong>"
        if run.italic:
            t = f"<em>{t}</em>"
        if run.underline:
            t = f"<u>{t}</u>"
        inner_html += t

    if not inner_html:
        inner_html = text

    css = f' class="{css_class}"' if css_class else ""
    return f"<{tag}{css}>{inner_html}</{tag}>"


def _table_to_html(table) -> str:
    """Convert a table to HTML."""
    rows_html = []
    for row in table.rows:
        cells_html = []
        for cell in row.cells:
            cell_text = cell.text or "&nbsp;"
            cells_html.append(f"<td>{cell_text}</td>")
        rows_html.append("<tr>" + "".join(cells_html) + "</tr>")
    return "<table>" + "".join(rows_html) + "</table>"
