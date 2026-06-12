"""Flask API routes for HTML-to-document conversion.

Provides REST endpoints for converting HTML (with optional charts)
to DOCX and PDF formats.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from flask import Blueprint, jsonify, request, send_file

from html2docx.exceptions import Html2DocxError, ValidationError
from html2docx.parsers.chartjs_adapter import ChartJsAdapter
from html2docx.services.conversion import ConversionService, OutputFormat

__all__ = ["create_blueprint"]

logger = logging.getLogger(__name__)


def create_blueprint() -> Blueprint:
    """Create and return the conversion API blueprint.

    Returns:
        A Flask :class:`Blueprint` with conversion routes registered.
    """
    bp = Blueprint("convert", __name__)

    @bp.route("/convert/docx", methods=["POST"])
    def convert_docx() -> tuple[Any, int]:
        """Convert HTML + charts to DOCX.

        Supports both legacy format and Chart.js format.

        Returns the generated file as a download.
        """
        return _handle_conversion(OutputFormat.DOCX)

    @bp.route("/convert/pdf", methods=["POST"])
    def convert_pdf() -> tuple[Any, int]:
        """Convert HTML + charts to PDF.

        Supports both legacy format and Chart.js format.

        Returns the generated file as a download.
        """
        return _handle_conversion(OutputFormat.PDF)

    def _handle_conversion(output_format: OutputFormat) -> tuple[Any, int]:
        """Unified conversion handler for both DOCX and PDF.

        Args:
            output_format: Target output format.

        Returns:
            Tuple of (response, status_code).
        """
        output_path: str | None = None

        try:
            payload = request.get_json(silent=True)
            if payload is None:
                return (
                    jsonify({
                        "success": False,
                        "message": "Request body must be valid JSON",
                    }),
                    400,
                )

            html = payload.get("html")
            if not html or not isinstance(html, str):
                return (
                    jsonify({
                        "success": False,
                        "message": "Field 'html' is required and must be a string",
                    }),
                    400,
                )

            # --- Build charts_data from payload ---
            charts_data = _extract_charts_data(payload)

            # --- Generate output to a unique temp file ---
            output_path = ConversionService.create_temp_output(
                output_format.value
            )

            ConversionService.convert(
                html=html,
                output_path=output_path,
                output_format=output_format,
                charts_data=charts_data,
            )

            return send_file(
                output_path,
                as_attachment=True,
                download_name=f"output.{output_format.value}",
            ), 200

        except ValidationError as exc:
            logger.warning("Validation error: %s", exc)
            return (
                jsonify({
                    "success": False,
                    "message": str(exc),
                }),
                400,
            )
        except Html2DocxError as exc:
            logger.error("Conversion error: %s", exc)
            return (
                jsonify({
                    "success": False,
                    "message": "Conversion failed. Check server logs for details.",
                }),
                500,
            )
        except Exception:
            logger.exception("Unexpected error during conversion")
            return (
                jsonify({
                    "success": False,
                    "message": "Internal server error",
                }),
                500,
            )
        finally:
            # Clean up temp file after response is sent
            # Note: send_file reads the file before this runs
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    logger.warning(
                        "Failed to clean up temp file: %s", output_path
                    )

    return bp


def _extract_charts_data(
    payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Extract chart data from both legacy and Chart.js payload formats.

    Args:
        payload: The request JSON body.

    Returns:
        A dict mapping chart IDs to chart configuration dicts.

    Raises:
        ValidationError: If a Chart.js payload is malformed.
    """
    charts_data: dict[str, dict[str, Any]] = {}

    # Legacy format: direct chart objects
    for chart in payload.get("charts", []):
        chart_id = chart.get("chart_id")
        if chart_id:
            charts_data[chart_id] = chart

    # Chart.js format
    for chartjs_payload in payload.get("chartjs_payloads", []):
        chart_model = ChartJsAdapter.adapt(chartjs_payload)
        charts_data[chart_model.chart_id] = {
            "chart_id": chart_model.chart_id,
            "chart_type": chart_model.chart_type,
            "title": chart_model.title,
            "categories": chart_model.categories,
            "series": [
                {"name": s.name, "values": s.values}
                for s in chart_model.series
            ],
        }

    return charts_data
