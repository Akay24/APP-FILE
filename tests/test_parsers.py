"""Tests for HTML, table, and chart parsers."""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from reportkit.models.chart import Chart
from reportkit.models.document import Paragraph
from reportkit.models.table import Table
from reportkit.parsers.chart_parser import ChartParser
from reportkit.parsers.html_parser import HtmlParser
from reportkit.parsers.table_parser import TableParser


def _find_tag(html: str, name: str) -> Tag:
    """Parse HTML and find a tag by name, asserting it exists."""
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find(name)
    assert isinstance(tag, Tag), f"Expected <{name}> tag in: {html}"
    return tag


class TestTableParser:
    """Tests for TableParser."""

    def test_parse_table_with_headers(self) -> None:
        html = (
            "<table>"
            "<tr><th>Name</th><th>Value</th></tr>"
            "<tr><td>A</td><td>10</td></tr>"
            "</table>"
        )
        table = TableParser.parse(_find_tag(html, "table"))

        assert table.headers == ["Name", "Value"]
        assert table.rows == [["A", "10"]]

    def test_parse_table_without_headers(self) -> None:
        html = (
            "<table>"
            "<tr><td>X</td><td>Y</td></tr>"
            "<tr><td>1</td><td>2</td></tr>"
            "</table>"
        )
        table = TableParser.parse(_find_tag(html, "table"))

        assert table.headers == []
        assert len(table.rows) == 2

    def test_parse_empty_table(self) -> None:
        table = TableParser.parse(_find_tag("<table></table>", "table"))

        assert table.headers == []
        assert table.rows == []

    def test_parse_table_strips_whitespace(self) -> None:
        html = "<table><tr><th>  Name  </th></tr><tr><td>  Alice  </td></tr></table>"
        table = TableParser.parse(_find_tag(html, "table"))

        assert table.headers == ["Name"]
        assert table.rows == [["Alice"]]


class TestChartParser:
    """Tests for ChartParser."""

    def test_parse_chart_from_attributes(self) -> None:
        html = '<div data-chart-id="c1" data-chart-type="pie" data-chart-title="My Pie"></div>'
        chart = ChartParser.parse(_find_tag(html, "div"))

        assert chart.chart_id == "c1"
        assert chart.chart_type == "pie"
        assert chart.title == "My Pie"

    def test_parse_chart_with_data(self) -> None:
        html = '<div data-chart-id="c2" data-chart-type="bar"></div>'

        charts_data = {
            "c2": {
                "chart_type": "line",
                "title": "Override Title",
                "categories": ["A", "B"],
                "series": [{"name": "S1", "values": [1, 2]}],
            }
        }
        chart = ChartParser.parse(_find_tag(html, "div"), charts_data)

        assert chart.chart_type == "line"
        assert chart.title == "Override Title"
        assert chart.categories == ["A", "B"]
        assert len(chart.series) == 1

    def test_parse_chart_defaults(self) -> None:
        html = '<div data-chart-id="c3"></div>'
        chart = ChartParser.parse(_find_tag(html, "div"))

        assert chart.chart_id == "c3"
        assert chart.chart_type == "bar"  # default
        assert chart.title == ""
        assert chart.categories == []
        assert chart.series == []


class TestHtmlParser:
    """Tests for HtmlParser."""

    def test_parse_heading(self) -> None:
        doc = HtmlParser.parse("<h1>Title</h1>")
        assert len(doc.elements) == 1
        assert isinstance(doc.elements[0], Paragraph)
        assert doc.elements[0].text == "Title"
        assert doc.elements[0].tag == "h1"

    def test_parse_paragraph(self) -> None:
        doc = HtmlParser.parse("<p>Hello world</p>")
        assert len(doc.elements) == 1
        elem = doc.elements[0]
        assert isinstance(elem, Paragraph)
        assert elem.tag == "p"
        assert elem.text == "Hello world"

    def test_parse_table(self) -> None:
        html = "<table><tr><th>Col</th></tr><tr><td>Val</td></tr></table>"
        doc = HtmlParser.parse(html)
        assert len(doc.elements) == 1
        assert isinstance(doc.elements[0], Table)

    def test_parse_chart_div(self) -> None:
        html = '<div data-chart-id="c1" data-chart-type="bar"></div>'
        doc = HtmlParser.parse(html)
        assert len(doc.elements) == 1
        assert isinstance(doc.elements[0], Chart)

    def test_parse_mixed_content(self, sample_html: str) -> None:
        doc = HtmlParser.parse(sample_html)
        assert len(doc.elements) == 3
        assert isinstance(doc.elements[0], Paragraph)  # h1
        assert isinstance(doc.elements[1], Paragraph)  # p
        assert isinstance(doc.elements[2], Table)

    def test_parse_empty_html(self) -> None:
        doc = HtmlParser.parse("")
        assert doc.elements == []

    def test_parse_all_heading_levels(self) -> None:
        html = "".join(f"<h{i}>H{i}</h{i}>" for i in range(1, 7))
        doc = HtmlParser.parse(html)
        assert len(doc.elements) == 6
        for i, elem in enumerate(doc.elements, start=1):
            assert isinstance(elem, Paragraph)
            assert elem.tag == f"h{i}"

    def test_skips_unsupported_elements(self) -> None:
        html = "<h1>Title</h1><span>Ignored</span><p>Kept</p>"
        doc = HtmlParser.parse(html)
        assert len(doc.elements) == 2  # span is skipped

    def test_parse_with_body_tag(self) -> None:
        html = "<html><body><h1>Inside Body</h1></body></html>"
        doc = HtmlParser.parse(html)
        assert len(doc.elements) == 1
        elem = doc.elements[0]
        assert isinstance(elem, Paragraph)
        assert elem.text == "Inside Body"
