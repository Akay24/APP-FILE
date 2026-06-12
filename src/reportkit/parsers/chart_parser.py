"""Chart parser.

Extracts chart configuration from HTML ``<div>`` elements bearing
``data-chart-*`` attributes and merges with optional server-side chart data.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from bs4 import Tag

from reportkit.exceptions import ParsingError
from reportkit.models.chart import Chart, Series

__all__ = ["ChartParser"]

logger = logging.getLogger(__name__)


class ChartParser:
    """Parses chart ``<div>`` tags into :class:`Chart` models."""

    @staticmethod
    def parse(
        chart_tag: Tag,
        charts_data: dict[str, dict[str, Any]] | None = None,
    ) -> Chart:
        """Build a :class:`Chart` from an HTML element and optional payload data.

        The element must carry at minimum a ``data-chart-id`` attribute.
        Additional configuration can come from ``data-chart-config`` (inline
        JSON) or the *charts_data* dict keyed by chart ID.

        Args:
            chart_tag: A ``<div>`` tag with ``data-chart-*`` attributes.
            charts_data: Optional mapping of chart IDs to configuration dicts,
                typically provided in the request payload.

        Returns:
            A fully populated :class:`Chart` model.

        Raises:
            ParsingError: If inline ``data-chart-config`` contains invalid JSON.
        """
        chart_id = str(chart_tag.get("data-chart-id", ""))
        chart_type = str(chart_tag.get("data-chart-type", "bar"))
        title = str(chart_tag.get("data-chart-title", ""))

        config: dict[str, Any] = {}
        config_attr = chart_tag.get("data-chart-config")
        if config_attr:
            try:
                config = json.loads(str(config_attr))
            except (json.JSONDecodeError, TypeError) as exc:
                logger.warning(
                    "Invalid data-chart-config JSON on chart '%s': %s",
                    chart_id,
                    exc,
                )
                raise ParsingError(
                    f"Invalid JSON in data-chart-config for chart '{chart_id}'"
                ) from exc

        # Server-side chart data takes precedence over inline attributes
        if charts_data and chart_id in charts_data:
            chart_info = charts_data[chart_id]
            chart_type = chart_info.get("chart_type", chart_type)
            title = chart_info.get("title", title)
            config = chart_info

        categories: list[str] = config.get("categories", [])

        series: list[Series] = [
            Series(name=item["name"], values=item["values"])
            for item in config.get("series", [])
        ]

        return Chart(
            chart_id=chart_id,
            chart_type=chart_type,
            title=title,
            categories=categories,
            series=series,
        )
