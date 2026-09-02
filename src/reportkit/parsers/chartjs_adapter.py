"""Chart.js format adapter.

Converts Chart.js configuration payloads (as sent by frontend charting
libraries) into the internal :class:`Chart` model used by renderers.
"""

from __future__ import annotations

import logging
from typing import Any

from reportkit.exceptions import ValidationError
from reportkit.models.chart import Chart, Series

__all__ = ["ChartJsAdapter"]

logger = logging.getLogger(__name__)

#: Chart.js type → internal chart type mapping.
_SUPPORTED_TYPES: dict[str, str] = {
    "bar": "bar",
    "line": "line",
    "pie": "pie",
    "doughnut": "pie",
    "area": "area",
}


class ChartJsAdapter:
    """Converts Chart.js payloads to internal :class:`Chart` models.

    Supported Chart.js types: ``bar``, ``line``, ``pie``, ``doughnut``,
    ``area``.  Unsupported types raise :class:`ValidationError`.
    """

    @staticmethod
    def adapt(chartjs_payload: dict[str, Any]) -> Chart:
        """Convert a single Chart.js payload dict to a :class:`Chart`.

        Expected payload structure::

            {
                "chartId": "uniqueId",
                "chartConfig": {
                    "type": "bar",
                    "data": {
                        "labels": ["A", "B"],
                        "datasets": [
                            {"label": "Series 1", "data": [10, 20]}
                        ]
                    },
                    "options": {  // optional
                        "plugins": {"title": {"text": "My Chart"}}
                    }
                }
            }

        Args:
            chartjs_payload: A dict matching the structure above.

        Returns:
            A populated :class:`Chart` model.

        Raises:
            ValidationError: If the payload is malformed or missing
                required fields.
        """
        if not isinstance(chartjs_payload, dict):
            raise ValidationError("Payload must be a dictionary")

        chart_id = chartjs_payload.get("chartId")
        if not chart_id:
            raise ValidationError("chartId is required")

        chart_config = chartjs_payload.get("chartConfig")
        if not chart_config:
            raise ValidationError("chartConfig is required")

        # --- Chart type ---
        chart_type_raw = chart_config.get("type")
        if not chart_type_raw:
            raise ValidationError("chartConfig.type is required")

        if chart_type_raw not in _SUPPORTED_TYPES:
            raise ValidationError(
                f"Chart type '{chart_type_raw}' not supported. "
                f"Supported: {list(_SUPPORTED_TYPES.keys())}"
            )

        # --- Data section ---
        data = chart_config.get("data", {})
        if not data:
            raise ValidationError("chartConfig.data is required")

        # --- Categories (labels) ---
        categories = data.get("labels", [])
        if not categories:
            raise ValidationError("chartConfig.data.labels is required (empty)")

        if not isinstance(categories, list):
            raise ValidationError("chartConfig.data.labels must be a list")

        categories = [str(cat) for cat in categories]

        # --- Datasets (series) ---
        datasets = data.get("datasets", [])
        if not datasets:
            raise ValidationError("chartConfig.data.datasets is required (empty)")

        series_list = ChartJsAdapter._extract_series(datasets, len(categories))

        # --- Optional title ---
        title: str = (
            chart_config.get("options", {})
            .get("plugins", {})
            .get("title", {})
            .get("text", "")
        )

        return Chart(
            chart_id=str(chart_id),
            chart_type=_SUPPORTED_TYPES[chart_type_raw],
            title=title,
            categories=categories,
            series=series_list,
        )

    @staticmethod
    def _extract_series(
        datasets: list[dict[str, Any]],
        category_count: int,
    ) -> list[Series]:
        """Convert Chart.js datasets to :class:`Series` objects.

        Args:
            datasets: List of Chart.js dataset dicts.
            category_count: Expected number of data points per dataset.

        Returns:
            Validated list of :class:`Series`.

        Raises:
            ValidationError: On malformed or inconsistent dataset data.
        """
        series_list: list[Series] = []

        for idx, dataset in enumerate(datasets):
            if not isinstance(dataset, dict):
                raise ValidationError(f"Dataset {idx} must be a dictionary")

            label = dataset.get("label")
            if not label:
                raise ValidationError(f"Dataset {idx} missing 'label' field")

            values = dataset.get("data", [])
            if not values:
                raise ValidationError(f"Dataset {idx} ('{label}') has empty data")

            if len(values) != category_count:
                raise ValidationError(
                    f"Dataset {idx} ('{label}') has {len(values)} values "
                    f"but {category_count} categories provided"
                )

            try:
                float_values = [float(v) if v is not None else 0.0 for v in values]
            except (TypeError, ValueError) as exc:
                raise ValidationError(
                    f"Dataset {idx} ('{label}') contains non-numeric values"
                ) from exc

            series_list.append(Series(name=str(label), values=float_values))

        return series_list
