"""PDF renderer.

Converts a :class:`Document` model into a PDF file using ReportLab.
Charts are rendered as matplotlib figures embedded as images.
"""

from __future__ import annotations

import io
import logging
import tempfile
from typing import Any

import matplotlib  # type: ignore[import-untyped]
import matplotlib.pyplot as plt  # type: ignore[import-untyped]
import numpy as np  # type: ignore[import-untyped]
from matplotlib.figure import Figure  # type: ignore[import-untyped]
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    SimpleDocTemplate,
    Spacer,
    TableStyle,
)
from reportlab.platypus import (
    Paragraph as RLParagraph,
)
from reportlab.platypus import (
    Table as RLTable,
)

from html2docx.exceptions import RenderingError
from html2docx.models.chart import Chart
from html2docx.models.document import Document, Paragraph
from html2docx.models.table import Table

__all__ = ["PdfRenderer"]

logger = logging.getLogger(__name__)

# Use non-interactive backend for server-side rendering
matplotlib.use("Agg")

# --- Custom styles -----------------------------------------------------------

_STYLES = getSampleStyleSheet()

_HEADING_STYLES: dict[str, ParagraphStyle] = {
    "h1": ParagraphStyle(
        "CustomH1",
        parent=_STYLES["Heading1"],
        fontSize=22,
        spaceAfter=12,
    ),
    "h2": ParagraphStyle(
        "CustomH2",
        parent=_STYLES["Heading2"],
        fontSize=18,
        spaceAfter=10,
    ),
    "h3": ParagraphStyle(
        "CustomH3",
        parent=_STYLES["Heading3"],
        fontSize=14,
        spaceAfter=8,
    ),
    "h4": ParagraphStyle(
        "CustomH4",
        parent=_STYLES["Heading4"],
        fontSize=12,
        spaceAfter=6,
    ),
    "h5": ParagraphStyle(
        "CustomH5",
        parent=_STYLES["Heading5"],
        fontSize=11,
        spaceAfter=6,
    ),
    "h6": ParagraphStyle(
        "CustomH6",
        parent=_STYLES["Heading6"],
        fontSize=10,
        spaceAfter=4,
    ),
}

_BODY_STYLE = _STYLES["BodyText"]

# Table styling
_TABLE_STYLE = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F2F2F2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFBFBF")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
    ]
)

# Chart colour palette
_CHART_COLORS: list[str] = [
    "#4472C4",
    "#ED7D31",
    "#A5A5A5",
    "#FFC000",
    "#5B9BD5",
    "#70AD47",
    "#264478",
    "#9B57A0",
]


class PdfRenderer:
    """Renders a :class:`Document` to a PDF file using ReportLab + matplotlib."""

    @staticmethod
    def render(document: Document, output_path: str) -> None:
        """Render a document model to a PDF file.

        Args:
            document: Parsed document model.
            output_path: Filesystem path for the output ``.pdf``.

        Raises:
            RenderingError: If rendering fails.
        """
        try:
            pdf = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=0.75 * inch,
                rightMargin=0.75 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch,
            )

            flowables: list[Any] = []

            for element in document.elements:
                if isinstance(element, Paragraph):
                    flowables.extend(
                        PdfRenderer._render_paragraph(element)
                    )
                elif isinstance(element, Table):
                    flowables.extend(PdfRenderer._render_table(element))
                elif isinstance(element, Chart):
                    flowables.extend(PdfRenderer._render_chart(element))

            if not flowables:
                # Empty document — add a spacer so ReportLab doesn't error
                flowables.append(Spacer(1, 1))

            pdf.build(flowables)
            logger.debug("PDF saved to %s", output_path)

        except RenderingError:
            raise
        except Exception as exc:
            raise RenderingError(f"PDF rendering failed: {exc}") from exc

    # --- Private rendering helpers -------------------------------------------

    @staticmethod
    def _render_paragraph(paragraph: Paragraph) -> list[Any]:
        """Convert a Paragraph to ReportLab flowables."""
        style = _HEADING_STYLES.get(paragraph.tag, _BODY_STYLE)
        return [
            RLParagraph(paragraph.text, style),
            Spacer(1, 6),
        ]

    @staticmethod
    def _render_table(table_model: Table) -> list[Any]:
        """Convert a Table to ReportLab flowables."""
        if not table_model.headers and not table_model.rows:
            return []

        data: list[list[str]] = []

        if table_model.headers:
            data.append(table_model.headers)

        data.extend(table_model.rows)

        rl_table = RLTable(data, repeatRows=1 if table_model.headers else 0)
        rl_table.setStyle(_TABLE_STYLE)

        return [
            rl_table,
            Spacer(1, 12),
        ]

    @staticmethod
    def _render_chart(chart: Chart) -> list[Any]:
        """Render a Chart as a matplotlib figure embedded in the PDF.

        The chart is rendered to an in-memory PNG buffer, then wrapped
        in a ReportLab :class:`Image`.
        """
        if not chart.series or not chart.categories:
            return []

        try:
            fig = PdfRenderer._create_chart_figure(chart)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            plt.close(fig)
            buf.seek(0)

            # Save to a temp file that ReportLab can read
            with tempfile.NamedTemporaryFile(
                suffix=".png", prefix="html2docx_chart_", delete=False
            ) as tmp:
                tmp.write(buf.getvalue())
                tmp.flush()

            img = Image(tmp.name, width=5.5 * inch, height=3.5 * inch)

            # Add title above chart
            flowables: list[Any] = []
            if chart.title:
                title_style = ParagraphStyle(
                    "ChartTitle",
                    parent=_STYLES["Heading3"],
                    fontSize=12,
                    spaceAfter=4,
                )
                flowables.append(RLParagraph(chart.title, title_style))

            flowables.extend([img, Spacer(1, 12)])
            return flowables

        except Exception as exc:
            logger.error(
                "Failed to render chart '%s' to PDF: %s",
                chart.chart_id,
                exc,
            )
            # Fall back to a placeholder paragraph
            return [
                RLParagraph(
                    f"[Chart: {chart.title or chart.chart_id}]",
                    _BODY_STYLE,
                ),
                Spacer(1, 12),
            ]

    @staticmethod
    def _create_chart_figure(chart: Chart) -> Figure:
        """Create a matplotlib Figure for the given chart."""
        fig, ax = plt.subplots(figsize=(8, 5))

        chart_type = chart.chart_type.lower()

        if chart_type == "pie":
            # Pie charts use the first series only
            first_series = chart.series[0]
            pie_colors = _CHART_COLORS[: len(chart.categories)]
            ax.pie(
                first_series.values,
                labels=chart.categories,
                colors=pie_colors,
                autopct="%1.1f%%",
                startangle=90,
            )
            ax.set_aspect("equal")

        elif chart_type == "line":
            for i, series in enumerate(chart.series):
                color = _CHART_COLORS[i % len(_CHART_COLORS)]
                ax.plot(
                    chart.categories,
                    series.values,
                    marker="o",
                    color=color,
                    label=series.name,
                    linewidth=2,
                )
            ax.set_xlabel("Category")
            ax.set_ylabel("Value")
            if len(chart.series) > 1:
                ax.legend()
            ax.grid(True, alpha=0.3)

        elif chart_type == "area":
            for i, series in enumerate(chart.series):
                color = _CHART_COLORS[i % len(_CHART_COLORS)]
                ax.fill_between(
                    range(len(chart.categories)),
                    series.values,
                    alpha=0.4,
                    color=color,
                    label=series.name,
                )
                ax.plot(
                    range(len(chart.categories)),
                    series.values,
                    color=color,
                    linewidth=1.5,
                )
            ax.set_xticks(range(len(chart.categories)))
            ax.set_xticklabels(chart.categories)
            ax.set_xlabel("Category")
            ax.set_ylabel("Value")
            if len(chart.series) > 1:
                ax.legend()
            ax.grid(True, alpha=0.3)

        else:
            # Default: bar chart

            x = np.arange(len(chart.categories))
            n_series = len(chart.series)
            width = 0.8 / max(n_series, 1)

            for i, series in enumerate(chart.series):
                color = _CHART_COLORS[i % len(_CHART_COLORS)]
                offset = (i - n_series / 2 + 0.5) * width
                ax.bar(
                    x + offset,
                    series.values,
                    width=width,
                    color=color,
                    label=series.name,
                )

            ax.set_xticks(x)
            ax.set_xticklabels(chart.categories)
            ax.set_xlabel("Category")
            ax.set_ylabel("Value")
            if n_series > 1:
                ax.legend()
            ax.grid(True, axis="y", alpha=0.3)

        if chart.title and chart_type != "pie":
            ax.set_title(chart.title, fontsize=13, fontweight="bold", pad=12)

        fig.tight_layout()
        return fig
