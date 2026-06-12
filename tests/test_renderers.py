"""Tests for DOCX and PDF renderers, and the conversion service."""

from __future__ import annotations

import os

from html2docx.models.chart import Chart, Series
from html2docx.models.document import Document, Paragraph
from html2docx.models.table import Table
from html2docx.renderers.docx_renderer import DocxRenderer
from html2docx.renderers.pdf_renderer import PdfRenderer
from html2docx.services.conversion import ConversionService, OutputFormat


class TestDocxRenderer:
    """Tests for DocxRenderer."""

    def test_render_empty_document(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "empty.docx")
        doc = Document()
        DocxRenderer.render(doc, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_render_paragraphs(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "paragraphs.docx")
        doc = Document(
            elements=[
                Paragraph(text="Title", tag="h1"),
                Paragraph(text="Subtitle", tag="h2"),
                Paragraph(text="Body text", tag="p"),
            ]
        )
        DocxRenderer.render(doc, path)
        assert os.path.exists(path)

    def test_render_table(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "table.docx")
        doc = Document(
            elements=[
                Table(
                    headers=["Name", "Value"],
                    rows=[["A", "1"], ["B", "2"]],
                ),
            ]
        )
        DocxRenderer.render(doc, path)
        assert os.path.exists(path)

    def test_render_with_charts(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "chart.docx")
        doc = Document(
            elements=[
                Paragraph(text="Chart Report", tag="h1"),
                Chart(
                    chart_id="test",
                    chart_type="bar",
                    title="Test Chart",
                    categories=["Q1", "Q2"],
                    series=[Series(name="Rev", values=[100.0, 200.0])],
                ),
            ]
        )
        DocxRenderer.render(doc, path)
        assert os.path.exists(path)
        # Chart injection makes the file larger
        assert os.path.getsize(path) > 5000


class TestPdfRenderer:
    """Tests for PdfRenderer."""

    def test_render_empty_document(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "empty.pdf")
        doc = Document()
        PdfRenderer.render(doc, path)
        assert os.path.exists(path)

    def test_render_paragraphs(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "paragraphs.pdf")
        doc = Document(
            elements=[
                Paragraph(text="Title", tag="h1"),
                Paragraph(text="Body", tag="p"),
            ]
        )
        PdfRenderer.render(doc, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_render_table(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "table.pdf")
        doc = Document(
            elements=[
                Table(
                    headers=["Col1", "Col2"],
                    rows=[["A", "B"]],
                ),
            ]
        )
        PdfRenderer.render(doc, path)
        assert os.path.exists(path)

    def test_render_bar_chart(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "bar.pdf")
        doc = Document(
            elements=[
                Chart(
                    chart_id="bar1",
                    chart_type="bar",
                    title="Bar Chart",
                    categories=["A", "B", "C"],
                    series=[Series(name="S1", values=[10.0, 20.0, 30.0])],
                ),
            ]
        )
        PdfRenderer.render(doc, path)
        assert os.path.exists(path)

    def test_render_pie_chart(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "pie.pdf")
        doc = Document(
            elements=[
                Chart(
                    chart_id="pie1",
                    chart_type="pie",
                    title="Pie Chart",
                    categories=["X", "Y"],
                    series=[Series(name="S1", values=[60.0, 40.0])],
                ),
            ]
        )
        PdfRenderer.render(doc, path)
        assert os.path.exists(path)

    def test_render_line_chart(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "line.pdf")
        doc = Document(
            elements=[
                Chart(
                    chart_id="line1",
                    chart_type="line",
                    title="Line Chart",
                    categories=["Jan", "Feb", "Mar"],
                    series=[Series(name="Trend", values=[5.0, 15.0, 10.0])],
                ),
            ]
        )
        PdfRenderer.render(doc, path)
        assert os.path.exists(path)

    def test_render_full_document(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "full.pdf")
        doc = Document(
            elements=[
                Paragraph(text="Report", tag="h1"),
                Paragraph(text="Introduction paragraph.", tag="p"),
                Table(
                    headers=["Metric", "Value"],
                    rows=[["Revenue", "$100M"], ["Profit", "$20M"]],
                ),
                Chart(
                    chart_id="overview",
                    chart_type="bar",
                    title="Overview",
                    categories=["Q1", "Q2"],
                    series=[Series(name="Rev", values=[100.0, 150.0])],
                ),
            ]
        )
        PdfRenderer.render(doc, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 1000


class TestConversionService:
    """Tests for the ConversionService."""

    def test_html_to_docx(self, tmp_path: object, sample_html: str) -> None:
        path = os.path.join(str(tmp_path), "out.docx")
        result = ConversionService.html_to_docx(sample_html, path)
        assert result == path
        assert os.path.exists(path)

    def test_html_to_pdf(self, tmp_path: object, sample_html: str) -> None:
        path = os.path.join(str(tmp_path), "out.pdf")
        result = ConversionService.html_to_pdf(sample_html, path)
        assert result == path
        assert os.path.exists(path)

    def test_convert_docx_format(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "out.docx")
        ConversionService.convert(
            html="<h1>Test</h1>",
            output_path=path,
            output_format=OutputFormat.DOCX,
        )
        assert os.path.exists(path)

    def test_convert_pdf_format(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "out.pdf")
        ConversionService.convert(
            html="<h1>Test</h1>",
            output_path=path,
            output_format=OutputFormat.PDF,
        )
        assert os.path.exists(path)

    def test_convert_with_charts(
        self,
        tmp_path: object,
        sample_html_with_chart: str,
        sample_charts_data: dict,
    ) -> None:
        path = os.path.join(str(tmp_path), "charts.docx")
        ConversionService.html_to_docx(
            sample_html_with_chart, path, sample_charts_data
        )
        assert os.path.exists(path)

    def test_create_temp_output(self) -> None:
        path = ConversionService.create_temp_output("docx")
        try:
            assert path.endswith(".docx")
            assert os.path.exists(path)
        finally:
            os.remove(path)

    def test_create_temp_output_pdf(self) -> None:
        path = ConversionService.create_temp_output("pdf")
        try:
            assert path.endswith(".pdf")
            assert os.path.exists(path)
        finally:
            os.remove(path)
