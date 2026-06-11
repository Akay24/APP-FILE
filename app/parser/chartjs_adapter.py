"""
Chart.js format adapter.

Converts Chart.js payloads to internal Chart model.
Validates data integrity and chart configuration.
"""
from typing import Dict, Any, List
from app.models.chart import Chart, Series


class ChartJsAdapter:
    """Converts Chart.js format to internal Chart model."""

    # Supported Chart.js types mapping to internal types
    SUPPORTED_TYPES = {
        "bar": "bar",
        "line": "line",
        "pie": "pie",
        "doughnut": "pie",
        "area": "area",
    }

    @staticmethod
    def adapt(chartjs_payload: Dict[str, Any]) -> Chart:
        """
        Convert Chart.js payload to Chart model.

        Args:
            chartjs_payload: Chart.js config dict with:
                - chartId: unique chart identifier
                - chartConfig: Chart.js configuration object

        Returns:
            Chart: Internal Chart model instance

        Raises:
            ValueError: If payload is invalid or missing required fields
            KeyError: If chart type not supported
        """
        # Validate required fields
        if not isinstance(chartjs_payload, dict):
            raise ValueError("Payload must be a dictionary")

        chart_id = chartjs_payload.get("chartId")
        if not chart_id:
            raise ValueError("chartId is required")

        chart_config = chartjs_payload.get("chartConfig")
        if not chart_config:
            raise ValueError("chartConfig is required")

        # Extract chart type
        chart_type = chart_config.get("type")
        if not chart_type:
            raise ValueError("chartConfig.type is required")

        if chart_type not in ChartJsAdapter.SUPPORTED_TYPES:
            raise ValueError(
                f"Chart type '{chart_type}' not supported. "
                f"Supported: {list(ChartJsAdapter.SUPPORTED_TYPES.keys())}"
            )

        # Extract data section
        data = chart_config.get("data", {})
        if not data:
            raise ValueError("chartConfig.data is required")

        # Extract categories (labels)
        categories = data.get("labels", [])
        if not categories:
            raise ValueError("chartConfig.data.labels is required (empty)")

        if not isinstance(categories, list):
            raise ValueError("chartConfig.data.labels must be a list")

        # Validate categories are strings
        categories = [str(cat) for cat in categories]

        # Extract datasets (series)
        datasets = data.get("datasets", [])
        if not datasets:
            raise ValueError("chartConfig.data.datasets is required (empty)")

        series_list = ChartJsAdapter._extract_series(datasets, len(categories))

        # Extract optional fields
        title = chart_config.get("options", {}).get("plugins", {}).get("title", {}).get("text", "")

        return Chart(
            chart_id=chart_id,
            chart_type=ChartJsAdapter.SUPPORTED_TYPES[chart_type],
            title=title,
            categories=categories,
            series=series_list,
        )

    @staticmethod
    def _extract_series(datasets: List[Dict[str, Any]], category_count: int) -> List[Series]:
        """
        Extract series from Chart.js datasets.

        Args:
            datasets: List of dataset objects
            category_count: Number of categories for validation

        Returns:
            List[Series]: Series objects

        Raises:
            ValueError: If dataset is invalid
        """
        series_list = []

        for idx, dataset in enumerate(datasets):
            if not isinstance(dataset, dict):
                raise ValueError(f"Dataset {idx} must be a dictionary")

            label = dataset.get("label")
            if not label:
                raise ValueError(f"Dataset {idx} missing 'label' field")

            values = dataset.get("data", [])
            if not values:
                raise ValueError(f"Dataset {idx} ('{label}') has empty data")

            if len(values) != category_count:
                raise ValueError(
                    f"Dataset {idx} ('{label}') has {len(values)} values "
                    f"but {category_count} categories provided"
                )

            # Convert all values to float, handle nulls
            try:
                values = [float(v) if v is not None else 0 for v in values]
            except (TypeError, ValueError):
                raise ValueError(f"Dataset {idx} ('{label}') contains non-numeric values")

            series_list.append(Series(name=str(label), values=values))

        return series_list
