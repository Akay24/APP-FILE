"""DOCX renderer.

Converts a :class:`Document` model into a Microsoft Word ``.docx`` file,
including native Office charts injected via OpenXML patching.
"""

from __future__ import annotations

import logging
import os
import tempfile
import zipfile
from typing import Any

from docx import Document as WordDocument
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE as PPTX_XL_CHART_TYPE
from pptx.util import Inches as PPTXInches

from reportkit.exceptions import RenderingError
from reportkit.models.chart import Chart
from reportkit.models.document import Document, Paragraph
from reportkit.models.table import Table
from reportkit.services.openxml_patcher import OXmlPatcher

__all__ = ["DocxRenderer"]

logger = logging.getLogger(__name__)

_HEADING_LEVELS: dict[str, int] = {
    "h1": 1,
    "h2": 2,
    "h3": 3,
    "h4": 4,
    "h5": 5,
    "h6": 6,
}

_CHART_TYPE_MAP: dict[str, PPTX_XL_CHART_TYPE] = {
    "bar": PPTX_XL_CHART_TYPE.COLUMN_CLUSTERED,
    "line": PPTX_XL_CHART_TYPE.LINE,
    "pie": PPTX_XL_CHART_TYPE.PIE,
    "area": PPTX_XL_CHART_TYPE.AREA,
}


class DocxRenderer:
    """Renders a :class:`Document` to a ``.docx`` file.

    Charts are injected as native Office charts (not images) by:

    1. Generating a temporary PPTX with the chart via python-pptx.
    2. Extracting the chart XML and embedded Excel workbook.
    3. Patching them into the DOCX via :class:`OXmlPatcher`.
    """

    @staticmethod
    def render(document: Document, output_path: str) -> None:
        """Render a document model to a DOCX file.

        Args:
            document: Parsed document model.
            output_path: Filesystem path for the output ``.docx``.

        Raises:
            RenderingError: If chart injection fails.
        """
        doc = WordDocument()
        charts_to_inject: list[Chart] = []

        for element in document.elements:
            if isinstance(element, Paragraph):
                DocxRenderer._render_paragraph(doc, element)
            elif isinstance(element, Table):
                DocxRenderer._render_table(doc, element)
            elif isinstance(element, Chart):
                charts_to_inject.append(element)
                doc.add_paragraph(f"CHART_PLACEHOLDER_{element.chart_id}")

        doc.save(output_path)

        if charts_to_inject:
            DocxRenderer._inject_native_charts(output_path, charts_to_inject)

    @staticmethod
    def _render_paragraph(doc: Any, paragraph: Paragraph) -> None:
        """Add a heading or paragraph to the Word document."""
        level = _HEADING_LEVELS.get(paragraph.tag)
        if level is not None:
            doc.add_heading(paragraph.text, level=level)
        else:
            doc.add_paragraph(paragraph.text)

    @staticmethod
    def _render_table(doc: Any, table_model: Table) -> None:
        """Add a table to the Word document."""
        if not table_model.headers:
            return

        row_count = len(table_model.rows) + 1
        col_count = len(table_model.headers)
        table = doc.add_table(rows=row_count, cols=col_count)
        table.style = "Table Grid"

        for col, header in enumerate(table_model.headers):
            table.cell(0, col).text = header

        for row_idx, row in enumerate(table_model.rows):
            for col_idx, value in enumerate(row):
                table.cell(row_idx + 1, col_idx).text = value

    @staticmethod
    def _inject_native_charts(
        output_path: str,
        charts: list[Chart],
    ) -> None:
        """Generate chart XML from PPTX and inject into the DOCX.

        Temporary PPTX files are created in the system temp directory and
        cleaned up after extraction.

        Raises:
            RenderingError: If chart generation fails for any chart.
        """
        if not charts:
            return

        chart_files: list[dict[str, object]] = []

        for idx, chart_model in enumerate(charts, start=1):
            temp_pptx: str | None = None
            try:
                # Create temp PPTX in system temp dir (not working dir)
                fd, temp_pptx = tempfile.mkstemp(
                    suffix=".pptx", prefix="reportkit_chart_"
                )
                os.close(fd)

                prs = Presentation()
                slide = prs.slides.add_slide(prs.slide_layouts[6])

                chart_data = CategoryChartData()  # type: ignore[no-untyped-call]
                chart_data.categories = chart_model.categories

                for series in chart_model.series:
                    chart_data.add_series(series.name, tuple(series.values))  # type: ignore[no-untyped-call]

                x, y, cx, cy = (
                    PPTXInches(1),
                    PPTXInches(1),
                    PPTXInches(6),
                    PPTXInches(4),
                )

                chart_type = _CHART_TYPE_MAP.get(
                    chart_model.chart_type,
                    PPTX_XL_CHART_TYPE.COLUMN_CLUSTERED,
                )

                slide.shapes.add_chart(chart_type, x, y, cx, cy, chart_data)
                prs.save(temp_pptx)

                with zipfile.ZipFile(temp_pptx, "r") as z:
                    excel_sheet_path: str | None = None
                    for fname in z.namelist():
                        if fname.startswith(
                            "ppt/embeddings/Microsoft_Excel_"
                        ):
                            excel_sheet_path = fname
                            break

                    if not excel_sheet_path:
                        raise RenderingError(
                            f"No embedded workbook found in chart {idx}"
                        )

                    xml = z.read("ppt/charts/chart1.xml")
                    rels = z.read("ppt/charts/_rels/chart1.xml.rels")
                    xlsx = z.read(excel_sheet_path)

                chart_files.append(
                    {
                        "idx": idx,
                        "chart_id": chart_model.chart_id,
                        "xml": xml,
                        "rels": rels,
                        "xlsx": xlsx,
                    }
                )

            except RenderingError:
                raise
            except Exception as exc:
                logger.error(
                    "Failed to generate chart %d (%s): %s",
                    idx,
                    chart_model.chart_id,
                    exc,
                )
                raise RenderingError(
                    f"Failed to generate chart '{chart_model.chart_id}'"
                ) from exc
            finally:
                if temp_pptx and os.path.exists(temp_pptx):
                    os.remove(temp_pptx)

        if chart_files:
            OXmlPatcher.inject_charts(output_path, chart_files)
