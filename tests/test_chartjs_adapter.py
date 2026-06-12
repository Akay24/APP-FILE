"""Tests for ChartJsAdapter."""

from __future__ import annotations

from typing import Any

import pytest

from reportkit.exceptions import ValidationError
from reportkit.parsers.chartjs_adapter import ChartJsAdapter


class TestChartJsAdapter:
    """Tests for ChartJsAdapter.adapt()."""

    def test_adapt_valid_bar_chart(self, sample_chartjs_payload: dict[str, Any]) -> None:
        chart = ChartJsAdapter.adapt(sample_chartjs_payload)

        assert chart.chart_id == "jsChart"
        assert chart.chart_type == "bar"
        assert chart.title == "JS Chart Title"
        assert chart.categories == ["A", "B", "C"]
        assert len(chart.series) == 1
        assert chart.series[0].name == "Series 1"
        assert chart.series[0].values == [10.0, 20.0, 30.0]

    def test_adapt_pie_chart(self) -> None:
        payload = {
            "chartId": "pie1",
            "chartConfig": {
                "type": "pie",
                "data": {
                    "labels": ["A", "B"],
                    "datasets": [{"label": "Data", "data": [60, 40]}],
                },
            },
        }
        chart = ChartJsAdapter.adapt(payload)
        assert chart.chart_type == "pie"

    def test_adapt_doughnut_maps_to_pie(self) -> None:
        payload = {
            "chartId": "d1",
            "chartConfig": {
                "type": "doughnut",
                "data": {
                    "labels": ["X", "Y"],
                    "datasets": [{"label": "D", "data": [50, 50]}],
                },
            },
        }
        chart = ChartJsAdapter.adapt(payload)
        assert chart.chart_type == "pie"

    def test_adapt_line_chart(self) -> None:
        payload = {
            "chartId": "line1",
            "chartConfig": {
                "type": "line",
                "data": {
                    "labels": ["Jan", "Feb"],
                    "datasets": [{"label": "Trend", "data": [10, 20]}],
                },
            },
        }
        chart = ChartJsAdapter.adapt(payload)
        assert chart.chart_type == "line"

    def test_adapt_multiple_series(self) -> None:
        payload = {
            "chartId": "multi",
            "chartConfig": {
                "type": "bar",
                "data": {
                    "labels": ["A", "B"],
                    "datasets": [
                        {"label": "S1", "data": [1, 2]},
                        {"label": "S2", "data": [3, 4]},
                    ],
                },
            },
        }
        chart = ChartJsAdapter.adapt(payload)
        assert len(chart.series) == 2

    def test_adapt_null_values_become_zero(self) -> None:
        payload = {
            "chartId": "nulls",
            "chartConfig": {
                "type": "bar",
                "data": {
                    "labels": ["A", "B"],
                    "datasets": [{"label": "S", "data": [None, 5]}],
                },
            },
        }
        chart = ChartJsAdapter.adapt(payload)
        assert chart.series[0].values == [0.0, 5.0]

    def test_adapt_no_title(self) -> None:
        payload = {
            "chartId": "notitle",
            "chartConfig": {
                "type": "bar",
                "data": {
                    "labels": ["A"],
                    "datasets": [{"label": "S", "data": [1]}],
                },
            },
        }
        chart = ChartJsAdapter.adapt(payload)
        assert chart.title == ""

    # --- Error cases ---

    def test_error_not_dict(self) -> None:
        with pytest.raises(ValidationError, match="dictionary"):
            ChartJsAdapter.adapt("not a dict")  # type: ignore[arg-type]

    def test_error_missing_chart_id(self) -> None:
        with pytest.raises(ValidationError, match="chartId"):
            ChartJsAdapter.adapt({"chartConfig": {"type": "bar"}})

    def test_error_missing_chart_config(self) -> None:
        with pytest.raises(ValidationError, match="chartConfig"):
            ChartJsAdapter.adapt({"chartId": "x"})

    def test_error_missing_type(self) -> None:
        with pytest.raises(ValidationError, match="type"):
            ChartJsAdapter.adapt({
                "chartId": "x",
                "chartConfig": {"data": {"labels": ["A"], "datasets": []}},
            })

    def test_error_unsupported_type(self) -> None:
        with pytest.raises(ValidationError, match="not supported"):
            ChartJsAdapter.adapt({
                "chartId": "x",
                "chartConfig": {
                    "type": "radar",
                    "data": {
                        "labels": ["A"],
                        "datasets": [{"label": "S", "data": [1]}],
                    },
                },
            })

    def test_error_empty_labels(self) -> None:
        with pytest.raises(ValidationError, match="labels"):
            ChartJsAdapter.adapt({
                "chartId": "x",
                "chartConfig": {
                    "type": "bar",
                    "data": {
                        "labels": [],
                        "datasets": [{"label": "S", "data": []}],
                    },
                },
            })

    def test_error_empty_datasets(self) -> None:
        with pytest.raises(ValidationError, match="datasets"):
            ChartJsAdapter.adapt({
                "chartId": "x",
                "chartConfig": {
                    "type": "bar",
                    "data": {"labels": ["A"], "datasets": []},
                },
            })

    def test_error_mismatched_data_count(self) -> None:
        with pytest.raises(ValidationError, match="values"):
            ChartJsAdapter.adapt({
                "chartId": "x",
                "chartConfig": {
                    "type": "bar",
                    "data": {
                        "labels": ["A", "B"],
                        "datasets": [{"label": "S", "data": [1]}],
                    },
                },
            })

    def test_error_missing_dataset_label(self) -> None:
        with pytest.raises(ValidationError, match="label"):
            ChartJsAdapter.adapt({
                "chartId": "x",
                "chartConfig": {
                    "type": "bar",
                    "data": {
                        "labels": ["A"],
                        "datasets": [{"data": [1]}],
                    },
                },
            })

    def test_error_non_numeric_data(self) -> None:
        with pytest.raises(ValidationError, match="non-numeric"):
            ChartJsAdapter.adapt({
                "chartId": "x",
                "chartConfig": {
                    "type": "bar",
                    "data": {
                        "labels": ["A"],
                        "datasets": [{"label": "S", "data": ["abc"]}],
                    },
                },
            })
