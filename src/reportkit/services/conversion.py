"""Conversion orchestration service.

Provides the high-level API that ties parsing and rendering together.
Supports both DOCX and PDF output formats.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
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
                # Try high-fidelity DOCX-to-PDF conversion first
                rendered_via_docx = False
                if ConversionService._has_docx_to_pdf_converter():
                    temp_docx = ConversionService.create_temp_output("docx")
                    try:
                        # 1. Render to temporary DOCX
                        DocxRenderer.render(document, temp_docx)
                        # 2. Convert DOCX to PDF
                        ConversionService._convert_docx_to_pdf(temp_docx, output_path)
                        rendered_via_docx = True
                    except Exception as e:
                        logger.warning(
                            "Failed to convert PDF via DOCX: %s. Falling back to ReportLab.",
                            e,
                        )
                    finally:
                        if os.path.exists(temp_docx):
                            os.remove(temp_docx)

                if not rendered_via_docx:
                    # Fallback to pure-Python ReportLab renderer
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
        fd, path = tempfile.mkstemp(suffix=f".{format_ext}", prefix="reportkit_")
        os.close(fd)
        return path

    @staticmethod
    def _has_docx_to_pdf_converter() -> bool:
        """Check if an external DOCX-to-PDF converter is available in the environment."""
        # 1. Check LibreOffice
        if shutil.which("soffice") or shutil.which("libreoffice"):
            return True

        # 2. Check macOS Apple Pages
        if sys.platform == "darwin":
            try:
                res = subprocess.run(
                    ["osascript", "-e", 'id of application "Pages"'],
                    capture_output=True,
                    text=True,
                )
                if res.returncode == 0 and "com.apple.Pages" in res.stdout:
                    return True
            except Exception:
                pass

        # 3. Check docx2pdf / MS Word (if installed)
        try:
            import docx2pdf  # noqa: F401

            if sys.platform == "darwin":
                res = subprocess.run(
                    ["osascript", "-e", 'id of application "Microsoft Word"'],
                    capture_output=True,
                    text=True,
                )
                if res.returncode == 0:
                    return True
            elif sys.platform == "win32":
                return True
        except ImportError:
            pass

        return False

    @staticmethod
    def _convert_docx_to_pdf(docx_path: str, pdf_path: str) -> None:
        """Convert a DOCX file to PDF using the first available high-fidelity converter."""
        abs_docx = os.path.abspath(docx_path)
        abs_pdf = os.path.abspath(pdf_path)

        # 1. Try LibreOffice
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if soffice:
            logger.info("Converting DOCX to PDF via LibreOffice...")
            outdir = os.path.dirname(abs_pdf)
            cmd = [
                soffice,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                outdir,
                abs_docx,
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            basename = os.path.splitext(os.path.basename(abs_docx))[0]
            generated_pdf = os.path.join(outdir, f"{basename}.pdf")
            if os.path.exists(generated_pdf) and generated_pdf != abs_pdf:
                if os.path.exists(abs_pdf):
                    os.remove(abs_pdf)
                os.rename(generated_pdf, abs_pdf)
            return

        # 2. Try macOS Apple Pages
        if sys.platform == "darwin":
            try:
                res = subprocess.run(
                    ["osascript", "-e", 'id of application "Pages"'],
                    capture_output=True,
                    text=True,
                )
                if res.returncode == 0 and "com.apple.Pages" in res.stdout:
                    logger.info("Converting DOCX to PDF via Apple Pages...")
                    applescript = f'''
                    tell application "Pages"
                        set theDoc to open POSIX file "{abs_docx}"
                        export theDoc to POSIX file "{abs_pdf}" as PDF
                        close theDoc saving no
                    end tell
                    '''
                    subprocess.run(
                        ["osascript", "-e", applescript],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    return
            except Exception as e:
                logger.debug("Pages conversion failed: %s", e)

        # 3. Try docx2pdf / Microsoft Word
        try:
            import docx2pdf

            logger.info("Converting DOCX to PDF via Microsoft Word (docx2pdf)...")
            docx2pdf.convert(abs_docx, abs_pdf)
            return
        except Exception as e:
            logger.debug("docx2pdf conversion failed: %s", e)

        raise RuntimeError("No available DOCX to PDF converter could perform the task.")
