"""Tests for data models (Chart, Series, Table, Document, Paragraph)."""

from __future__ import annotations

import pytest

from reportkit.models.chart import Chart, Series
from reportkit.models.document import Document, Paragraph
from reportkit.models.table import Table


class TestSeries:
    """Tests for the Series dataclass."""

    def test_create_series(self) -> None:
        s = Series(name="Revenue", values=[10.0, 20.0, 30.0])
        assert s.name == "Revenue"
        assert s.values == [10.0, 20.0, 30.0]

    def test_series_defaults(self) -> None:
        s = Series(name="Empty")
        assert s.values == []

    def test_series_is_frozen(self) -> None:
        s = Series(name="Test", values=[1.0])
        with pytest.raises(AttributeError):
            s.name = "Changed"  # type: ignore[misc]


class TestChart:
    """Tests for the Chart dataclass."""

    def test_create_chart(self) -> None:
        c = Chart(
            chart_id="test",
            chart_type="bar",
            title="Test",
            categories=["A", "B"],
            series=[Series(name="S1", values=[1.0, 2.0])],
        )
        assert c.chart_id == "test"
        assert c.chart_type == "bar"
        assert c.title == "Test"
        assert len(c.categories) == 2
        assert len(c.series) == 1

    def test_chart_defaults(self) -> None:
        c = Chart()
        assert c.chart_id == ""
        assert c.chart_type == "bar"
        assert c.title == ""
        assert c.categories == []
        assert c.series == []


class TestTable:
    """Tests for the Table dataclass."""

    def test_create_table(self) -> None:
        t = Table(headers=["Name", "Age"], rows=[["Alice", "30"]])
        assert t.headers == ["Name", "Age"]
        assert t.rows == [["Alice", "30"]]

    def test_table_defaults(self) -> None:
        t = Table()
        assert t.headers == []
        assert t.rows == []

    def test_table_multiple_rows(self) -> None:
        t = Table(
            headers=["X"],
            rows=[["1"], ["2"], ["3"]],
        )
        assert len(t.rows) == 3


class TestParagraph:
    """Tests for the Paragraph dataclass."""

    def test_create_paragraph(self) -> None:
        p = Paragraph(text="Hello", tag="p")
        assert p.text == "Hello"
        assert p.tag == "p"

    def test_paragraph_default_tag(self) -> None:
        p = Paragraph(text="Test")
        assert p.tag == "p"

    def test_heading_paragraph(self) -> None:
        p = Paragraph(text="Title", tag="h1")
        assert p.tag == "h1"

    def test_paragraph_is_frozen(self) -> None:
        p = Paragraph(text="Test")
        with pytest.raises(AttributeError):
            p.text = "Changed"  # type: ignore[misc]


class TestDocument:
    """Tests for the Document dataclass."""

    def test_empty_document(self) -> None:
        d = Document()
        assert d.elements == []

    def test_document_with_elements(self) -> None:
        d = Document(
            elements=[
                Paragraph(text="Title", tag="h1"),
                Table(headers=["A"], rows=[["1"]]),
            ]
        )
        assert len(d.elements) == 2
        assert isinstance(d.elements[0], Paragraph)
        assert isinstance(d.elements[1], Table)

    def test_document_append(self) -> None:
        d = Document()
        d.elements.append(Paragraph(text="Added"))
        assert len(d.elements) == 1
