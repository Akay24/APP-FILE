"""Conversion orchestration service.

Provides the high-level API that ties parsing and rendering together.
Supports both DOCX and PDF output formats.
"""

from __future__ import annotations

import logging
import os
import tempfile
from enum import Enum
from typing import Any

from reportkit.exceptions import ConversionError
from reportkit.parsers.html_parser import HtmlParser
from reportkit.renderers.docx_renderer import DocxRenderer
from reportkit.renderers.pdf_renderer import PdfRenderer

__all__ = ["ConversionService", "OutputFormat"]

logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    """Supported output document formats."""

    DOCX = "docx"
    PDF = "pdf"


class ConversionService:
    """Orchestrates HTML-to-document conversion.

    Usage::

        path = ConversionService.convert(
            html="<h1>Hello</h1>",
            output_path="report.docx",
            output_format=OutputFormat.DOCX,
        )
    """

    @staticmethod
    def convert(
        html: str,
        output_path: str,
        output_format: OutputFormat = OutputFormat.DOCX,
        charts_data: dict[str, dict[str, Any]] | None = None,
    ) -> str:
        """Convert HTML content to a document file.

        Args:
            html: Raw HTML string to convert.
            output_path: Filesystem path for the output file.
            output_format: Target format (DOCX or PDF).
            charts_data: Optional chart data dict keyed by chart ID.

        Returns:
            The *output_path* for chaining convenience.

        Raises:
            ConversionError: If parsing or rendering fails.
        """
        try:
            document = HtmlParser.parse(html, charts_data)

            if output_format == OutputFormat.PDF:
                PdfRenderer.render(document, output_path)
            else:
                DocxRenderer.render(document, output_path)

            logger.info(
                "Converted HTML to %s → %s",
                output_format.value.upper(),
                output_path,
            )
            return output_path

        except ConversionError:
            raise
        except Exception as exc:
            raise ConversionError(
                f"Conversion to {output_format.value} failed: {exc}"
            ) from exc

    @staticmethod
    def html_to_docx(
        html: str,
        output_path: str,
        charts_data: dict[str, dict[str, Any]] | None = None,
    ) -> str:
        """Shortcut for DOCX conversion.

        Args:
            html: Raw HTML string.
            output_path: Output file path.
            charts_data: Optional chart data.

        Returns:
            The output path.
        """
        return ConversionService.convert(
            html=html,
            output_path=output_path,
            output_format=OutputFormat.DOCX,
            charts_data=charts_data,
        )

    @staticmethod
    def html_to_pdf(
        html: str,
        output_path: str,
        charts_data: dict[str, dict[str, Any]] | None = None,
    ) -> str:
        """Shortcut for PDF conversion.

        Args:
            html: Raw HTML string.
            output_path: Output file path.
            charts_data: Optional chart data.

        Returns:
            The output path.
        """
        return ConversionService.convert(
            html=html,
            output_path=output_path,
            output_format=OutputFormat.PDF,
            charts_data=charts_data,
        )

    @staticmethod
    def create_temp_output(
        format_ext: str = "docx",
    ) -> str:
        """Create a unique temporary file path for output.

        This avoids the race condition of hardcoded output paths.

        Args:
            format_ext: File extension without dot (e.g. "docx", "pdf").

        Returns:
            A unique temporary file path.
        """
        fd, path = tempfile.mkstemp(
            suffix=f".{format_ext}", prefix="reportkit_"
        )
        os.close(fd)
        return path
