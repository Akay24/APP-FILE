"""HTML and chart data parsers."""

from reportkit.parsers.chart_parser import ChartParser
from reportkit.parsers.chartjs_adapter import ChartJsAdapter
from reportkit.parsers.html_parser import HtmlParser
from reportkit.parsers.table_parser import TableParser

__all__ = [
    "ChartJsAdapter",
    "ChartParser",
    "HtmlParser",
    "TableParser",
]
