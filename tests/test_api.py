"""Tests for the Flask API routes."""

from __future__ import annotations

import json
from collections.abc import Generator
from typing import Any

import pytest
from flask.testing import FlaskClient

from reportkit.app import create_app


@pytest.fixture()
def client() -> Generator[FlaskClient, None, None]:
    """Create a Flask test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestConvertDocxEndpoint:
    """Tests for POST /convert/docx."""

    def test_convert_simple_html(self, client: FlaskClient) -> None:
        response = client.post(
            "/convert/docx",
            data=json.dumps({"html": "<h1>Hello</h1>"}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_convert_with_table(self, client: FlaskClient) -> None:
        html = "<table><tr><th>A</th></tr><tr><td>1</td></tr></table>"
        response = client.post(
            "/convert/docx",
            data=json.dumps({"html": html}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_convert_with_charts(
        self, client: FlaskClient, full_payload: dict[str, Any]
    ) -> None:
        response = client.post(
            "/convert/docx",
            data=json.dumps(full_payload),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_missing_html_returns_400(self, client: FlaskClient) -> None:
        response = client.post(
            "/convert/docx",
            data=json.dumps({"charts": []}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_empty_body_returns_400(self, client: FlaskClient) -> None:
        response = client.post(
            "/convert/docx",
            data="not json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_html_not_string_returns_400(self, client: FlaskClient) -> None:
        response = client.post(
            "/convert/docx",
            data=json.dumps({"html": 12345}),
            content_type="application/json",
        )
        assert response.status_code == 400


class TestConvertPdfEndpoint:
    """Tests for POST /convert/pdf."""

    def test_convert_simple_html(self, client: FlaskClient) -> None:
        response = client.post(
            "/convert/pdf",
            data=json.dumps({"html": "<h1>Hello PDF</h1>"}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_convert_with_table(self, client: FlaskClient) -> None:
        html = "<table><tr><th>X</th></tr><tr><td>1</td></tr></table>"
        response = client.post(
            "/convert/pdf",
            data=json.dumps({"html": html}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_missing_html_returns_400(self, client: FlaskClient) -> None:
        response = client.post(
            "/convert/pdf",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400


class TestChartJsPayloads:
    """Tests for Chart.js payload handling in API."""

    def test_valid_chartjs_payload(self, client: FlaskClient) -> None:
        payload = {
            "html": '<h1>Test</h1><div data-chart-id="c1" data-chart-type="bar"></div>',
            "chartjs_payloads": [
                {
                    "chartId": "c1",
                    "chartConfig": {
                        "type": "bar",
                        "data": {
                            "labels": ["A", "B"],
                            "datasets": [{"label": "S", "data": [10, 20]}],
                        },
                    },
                }
            ],
        }
        response = client.post(
            "/convert/docx",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_invalid_chartjs_payload_returns_400(self, client: FlaskClient) -> None:
        payload = {
            "html": "<h1>Test</h1>",
            "chartjs_payloads": [
                {"chartId": "c1"}  # missing chartConfig
            ],
        }
        response = client.post(
            "/convert/docx",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400
