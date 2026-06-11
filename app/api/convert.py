from flask import Blueprint, jsonify, request
from app.renderers.office_chart_renderer import OfficeChartRenderer
from app.models.chart import Chart, Series
from app.services.conversion_service import ConversionService
from app.parser.chartjs_adapter import ChartJsAdapter

convert_bp = Blueprint(
    "convert",
    __name__
)


@convert_bp.route(
    "/convert/docx",
    methods=["POST"]
)
def convert_docx():
    """
    Convert HTML + charts to DOCX.

    Supports both legacy format and new Chart.js format.

    Legacy format:
    {
        "html": "...",
        "charts": [{"chart_id": "...", "chart_type": "bar", ...}]
    }

    New Chart.js format:
    {
        "html": "...",
        "chartjs_payloads": [{"chartId": "...", "chartConfig": {...}}]
    }
    """
    try:
        payload = request.get_json()

        html = payload.get("html")
        if not html:
            return jsonify({
                "success": False,
                "message": "html is required"
            }), 400

        # Support both legacy format and new Chart.js format
        charts_data = {}

        # Legacy format: direct chart objects
        if "charts" in payload:
            for chart in payload.get("charts", []):
                chart_id = chart.get("chart_id")
                if chart_id:
                    charts_data[chart_id] = chart

        # New format: Chart.js payloads
        if "chartjs_payloads" in payload:
            for chartjs_payload in payload.get("chartjs_payloads", []):
                try:
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
                except ValueError as e:
                    return jsonify({
                        "success": False,
                        "message": f"Invalid Chart.js payload: {str(e)}"
                    }), 400

        output_path = "output.docx"

        ConversionService.html_to_docx(
            html,
            output_path,
            charts_data
        )

        return jsonify({
            "success": True,
            "file": output_path
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Conversion error: {str(e)}"
        }), 500


@convert_bp.route("/convert/docx/chartjs", methods=["POST"])
def convert_docx_chartjs():
    """
    Convert HTML + Chart.js charts to DOCX.

    Request format:
    {
        "html": "<html>...</html>",
        "chartjs_payloads": [
            {
                "chartId": "topCountries",
                "chartConfig": {
                    "type": "bar",
                    "data": {
                        "labels": ["USA", "Germany"],
                        "datasets": [
                            {
                                "label": "2024",
                                "data": [30, 20]
                            }
                        ]
                    }
                }
            }
        ]
    }
    """
    try:
        payload = request.get_json()

        html = payload.get("html")
        if not html:
            return jsonify({
                "success": False,
                "message": "html is required"
            }), 400

        chartjs_payloads = payload.get("chartjs_payloads", [])
        if not chartjs_payloads:
            return jsonify({
                "success": False,
                "message": "chartjs_payloads is required"
            }), 400

        # Adapt Chart.js payloads to internal format
        charts_data = {}
        try:
            for chartjs_payload in chartjs_payloads:
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
        except ValueError as e:
            return jsonify({
                "success": False,
                "message": f"Invalid Chart.js payload: {str(e)}"
            }), 400

        output_path = "output.docx"
        ConversionService.html_to_docx(html, output_path, charts_data)

        return jsonify({
            "success": True,
            "file": output_path
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Conversion error: {str(e)}"
        }), 500


@convert_bp.route("/test-excel")
def test_excel():

    chart = Chart(
        chart_id="topCountries",
        chart_type="bar",
        title="Top Countries",
        categories=["USA", "Germany"],
        series=[
            Series(
                name="Count",
                values=[30, 20]
            )
        ]
    )

    OfficeChartRenderer.create_workbook(
        chart,
        "test.xlsx"
    )

    return {
        "success": True
    }