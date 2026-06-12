"""Test configuration and shared fixtures."""

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture()
def sample_html() -> str:
    """Basic HTML with heading, paragraph, and table."""
    return (
        "<h1>Test Report</h1>"
        "<p>This is a test paragraph.</p>"
        "<table>"
        "<thead><tr><th>Name</th><th>Value</th></tr></thead>"
        "<tbody>"
        "<tr><td>A</td><td>10</td></tr>"
        "<tr><td>B</td><td>20</td></tr>"
        "</tbody>"
        "</table>"
    )


@pytest.fixture()
def sample_html_with_chart() -> str:
    """HTML with a chart placeholder div."""
    return (
        "<h1>Chart Report</h1>"
        '<div data-chart-id="testChart" '
        'data-chart-type="bar" '
        'data-chart-title="Test Chart"></div>'
    )


@pytest.fixture()
def sample_charts_data() -> dict[str, Any]:
    """Chart data dict matching the chart placeholder."""
    return {
        "testChart": {
            "chart_id": "testChart",
            "chart_type": "bar",
            "title": "Test Chart",
            "categories": ["Q1", "Q2", "Q3"],
            "series": [
                {"name": "Revenue", "values": [100, 150, 200]},
            ],
        }
    }


@pytest.fixture()
def sample_chartjs_payload() -> dict[str, Any]:
    """A valid Chart.js payload."""
    return {
        "chartId": "jsChart",
        "chartConfig": {
            "type": "bar",
            "data": {
                "labels": ["A", "B", "C"],
                "datasets": [
                    {"label": "Series 1", "data": [10, 20, 30]},
                ],
            },
            "options": {
                "plugins": {
                    "title": {"text": "JS Chart Title"},
                },
            },
        },
    }


@pytest.fixture()
def full_payload(sample_html_with_chart: str, sample_charts_data: dict[str, Any]) -> dict[str, Any]:
    """Complete API request payload with HTML and charts."""
    return {
        "html": sample_html_with_chart,
        "charts": list(sample_charts_data.values()),
    }
