"""OpenXML patching for chart injection.

Handles all ZIP/XML manipulation required to inject native Office charts
(with embedded Excel workbooks) into DOCX files.
"""

from __future__ import annotations

import logging
import os
import re
import zipfile
from typing import Any

from reportkit.exceptions import RenderingError

__all__ = ["OXmlPatcher"]

logger = logging.getLogger(__name__)


class OXmlPatcher:
    """Patches DOCX files with Office charts and workbooks.

    The DOCX format is a ZIP archive containing XML files.  This class
    manipulates those XML entries to inject chart definitions, embedded
    Excel workbooks, and the necessary relationships/content-types.
    """

    @staticmethod
    def inject_charts(
        docx_path: str,
        chart_files: list[dict[str, Any]],
    ) -> None:
        """Inject charts and workbooks into an existing DOCX file.

        The DOCX is rewritten in-place using a temporary file to ensure
        atomicity.

        Args:
            docx_path: Path to the target DOCX file.
            chart_files: List of chart data dicts, each containing:
                - ``idx``: 1-based chart index
                - ``chart_id``: Unique chart identifier
                - ``xml``: Chart XML bytes
                - ``xlsx``: Excel workbook bytes
                - ``rels``: Chart relationships XML bytes

        Raises:
            RenderingError: If the DOCX file is not found or injection fails.
        """
        if not os.path.exists(docx_path):
            raise RenderingError(f"DOCX not found: {docx_path}")

        if not chart_files:
            return

        temp_docx = docx_path + ".tmp"

        try:
            with (
                zipfile.ZipFile(docx_path, "r") as zin,
                zipfile.ZipFile(temp_docx, "w") as zout,
            ):
                for item in zin.infolist():
                    data = zin.read(item.filename)

                    if item.filename == "word/document.xml":
                        data = OXmlPatcher._update_document_xml(data, chart_files)
                    elif item.filename == "word/_rels/document.xml.rels":
                        data = OXmlPatcher._update_relationships(data, chart_files)
                    elif item.filename == "[Content_Types].xml":
                        data = OXmlPatcher._update_content_types(data, chart_files)

                    zout.writestr(item, data)

                # Write chart and workbook entries
                for chart in chart_files:
                    idx = chart["idx"]
                    workbook_name = f"Microsoft_Excel_Sheet{idx}.xlsx"

                    zout.writestr(
                        f"word/charts/chart{idx}.xml",
                        chart["xml"],
                    )
                    zout.writestr(
                        f"word/embeddings/{workbook_name}",
                        chart["xlsx"],
                    )

                    # Update workbook reference in chart rels
                    rels_content = chart["rels"].decode("utf-8")
                    rels_content = re.sub(
                        r'Target="\.\./embeddings/Microsoft_Excel_.*\.xlsx"',
                        f'Target="../embeddings/{workbook_name}"',
                        rels_content,
                    )
                    zout.writestr(
                        f"word/charts/_rels/chart{idx}.xml.rels",
                        rels_content.encode("utf-8"),
                    )

            # Atomic replace
            if os.path.exists(docx_path):
                os.remove(docx_path)
            os.rename(temp_docx, docx_path)

            logger.debug("Injected %d charts into %s", len(chart_files), docx_path)

        except RenderingError:
            raise
        except Exception as exc:
            # Clean up temp file on failure
            if os.path.exists(temp_docx):
                os.remove(temp_docx)
            raise RenderingError(f"Chart injection failed: {exc}") from exc

    @staticmethod
    def _update_document_xml(
        xml_data: bytes,
        chart_files: list[dict[str, Any]],
    ) -> bytes:
        """Replace chart placeholder text with Office drawing XML."""
        content = xml_data.decode("utf-8")

        for chart in chart_files:
            chart_id = chart["chart_id"]
            idx = chart["idx"]

            placeholder = f"CHART_PLACEHOLDER_{chart_id}"
            drawing_xml = OXmlPatcher._create_drawing_xml(idx)

            # Try to replace the full <w:r> run containing the placeholder
            pattern = (
                rf"<w:r\b[^>]*>(?:(?!</w:r>).)*?"
                rf"{re.escape(placeholder)}.*?</w:r>"
            )
            if re.search(pattern, content):
                content = re.sub(pattern, drawing_xml, content)
            else:
                content = content.replace(placeholder, drawing_xml)

        return content.encode("utf-8")

    @staticmethod
    def _update_relationships(
        xml_data: bytes,
        chart_files: list[dict[str, Any]],
    ) -> bytes:
        """Add chart relationship entries to document.xml.rels."""
        content = xml_data.decode("utf-8")

        rel_tags = "".join(
            f'<Relationship Id="rIdChart{chart["idx"]}" '
            f'Type="http://schemas.openxmlformats.org/officeDocument/'
            f'2006/relationships/chart" '
            f'Target="charts/chart{chart["idx"]}.xml"/>'
            for chart in chart_files
        )

        content = content.replace("</Relationships>", f"{rel_tags}</Relationships>")
        return content.encode("utf-8")

    @staticmethod
    def _update_content_types(
        xml_data: bytes,
        chart_files: list[dict[str, Any]],
    ) -> bytes:
        """Add chart and xlsx content-type entries."""
        content = xml_data.decode("utf-8")

        # Ensure xlsx default type exists
        if 'Extension="xlsx"' not in content:
            default_xlsx = (
                '<Default Extension="xlsx" '
                'ContentType="application/vnd.openxmlformats-officedocument'
                '.spreadsheetml.sheet"/>'
            )
            content = content.replace("</Types>", f"{default_xlsx}</Types>")

        # Add chart overrides
        overrides = "".join(
            f'<Override PartName="/word/charts/chart{chart["idx"]}.xml" '
            f'ContentType="application/vnd.openxmlformats-officedocument'
            f'.drawingml.chart+xml"/>'
            for chart in chart_files
        )

        content = content.replace("</Types>", f"{overrides}</Types>")
        return content.encode("utf-8")

    @staticmethod
    def _create_drawing_xml(chart_idx: int) -> str:
        """Create Office Open XML drawing markup for a chart reference.

        Args:
            chart_idx: 1-based chart index.

        Returns:
            An XML string for a ``<w:r>`` containing an inline drawing.
        """
        doc_pr_id = 100 + chart_idx
        return (
            f"<w:r>"
            f"<w:drawing>"
            f'<wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="5486400" cy="3657600"/>'
            f'<wp:docPr id="{doc_pr_id}" name="Chart {chart_idx}"/>'
            f"<wp:cNvGraphicFramePr>"
            f"<a:graphicFrameLocks "
            f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            f'noChangeAspect="1"/>'
            f"</wp:cNvGraphicFramePr>"
            f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            f"<c:chart "
            f'xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
            f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            f'r:id="rIdChart{chart_idx}"/>'
            f"</a:graphicData>"
            f"</a:graphic>"
            f"</wp:inline>"
            f"</w:drawing>"
            f"</w:r>"
        )
