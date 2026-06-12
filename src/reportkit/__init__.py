"""reportkit — Convert HTML to DOCX and PDF with native Office charts.

This package provides a Python library and optional Flask API for converting
HTML content (with embedded tables and charts) into production-quality
Microsoft Word (.docx) and PDF documents.

Quick Start::

    from reportkit import convert_html_to_docx, convert_html_to_pdf

    convert_html_to_docx("<h1>Hello</h1>", "output.docx")
    convert_html_to_pdf("<h1>Hello</h1>", "output.pdf")
"""

from __future__ import annotations

from typing import Any

from reportkit.exceptions import (
    ConversionError,
    ParsingError,
    RenderingError,
    ReportKitError,
    ValidationError,
)
from reportkit.models.chart import Chart, Series
from reportkit.models.document import Document, Paragraph
from reportkit.models.table import Table
from reportkit.parsers.chartjs_adapter import ChartJsAdapter
from reportkit.services.conversion import ConversionService, OutputFormat

__version__ = "0.1.1"

__all__ = [
    "Chart",
    "ChartJsAdapter",
    "ConversionError",
    "ConversionService",
    "Document",
    "OutputFormat",
    "Paragraph",
    "ParsingError",
    "RenderingError",
    "ReportKitError",
    "Series",
    "Table",
    "ValidationError",
    "__version__",
    "convert",
    "convert_html_to_docx",
    "convert_html_to_pdf",
]


# --- Convenience functions (the public API) ----------------------------------


def convert_html_to_docx(
    html: str,
    output_path: str,
    charts_data: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Convert HTML to a Microsoft Word (.docx) file.

    Args:
        html: Raw HTML string to convert.
        output_path: Filesystem path for the output file.
        charts_data: Optional dict mapping chart IDs to chart config dicts.

    Returns:
        The *output_path* for chaining convenience.

    Raises:
        ConversionError: If conversion fails.
    """
    return ConversionService.html_to_docx(html, output_path, charts_data)


def convert_html_to_pdf(
    html: str,
    output_path: str,
    charts_data: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Convert HTML to a PDF file.

    Args:
        html: Raw HTML string to convert.
        output_path: Filesystem path for the output file.
        charts_data: Optional dict mapping chart IDs to chart config dicts.

    Returns:
        The *output_path* for chaining convenience.

    Raises:
        ConversionError: If conversion fails.
    """
    return ConversionService.html_to_pdf(html, output_path, charts_data)


def convert(
    html: str,
    output_path: str,
    output_format: OutputFormat = OutputFormat.DOCX,
    charts_data: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Convert HTML to a document file (DOCX or PDF).

    Args:
        html: Raw HTML string to convert.
        output_path: Filesystem path for the output file.
        output_format: Target format (:attr:`OutputFormat.DOCX` or
            :attr:`OutputFormat.PDF`).
        charts_data: Optional dict mapping chart IDs to chart config dicts.

    Returns:
        The *output_path* for chaining convenience.

    Raises:
        ConversionError: If conversion fails.
    """
    return ConversionService.convert(
        html=html,
        output_path=output_path,
        output_format=output_format,
        charts_data=charts_data,
    )
