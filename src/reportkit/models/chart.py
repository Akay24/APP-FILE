"""Chart data models.

Represents chart data extracted from HTML or Chart.js payloads,
used as the internal representation for rendering into DOCX/PDF.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["Chart", "Series"]


@dataclass(frozen=True, slots=True)
class Series:
    """A single data series within a chart.

    Attributes:
        name: Human-readable series label (e.g. "Revenue ($M)").
        values: Numeric data points, one per category.
    """

    name: str
    values: list[float] = field(default_factory=list)


@dataclass(slots=True)
class Chart:
    """Chart definition with categories and data series.

    Attributes:
        chart_id: Unique identifier matching the HTML data-chart-id attribute.
        chart_type: One of "bar", "line", "pie", "area".
        title: Display title for the chart.
        categories: Category labels for the X-axis.
        series: One or more data series to plot.
    """

    chart_id: str = ""
    chart_type: str = "bar"
    title: str = ""
    categories: list[str] = field(default_factory=list)
    series: list[Series] = field(default_factory=list)
