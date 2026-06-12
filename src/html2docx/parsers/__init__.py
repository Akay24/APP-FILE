"""HTML and chart data parsers."""

from html2docx.parsers.chart_parser import ChartParser
from html2docx.parsers.chartjs_adapter import ChartJsAdapter
from html2docx.parsers.html_parser import HtmlParser
from html2docx.parsers.table_parser import TableParser

__all__ = [
    "ChartJsAdapter",
    "ChartParser",
    "HtmlParser",
    "TableParser",
]
