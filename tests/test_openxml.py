"""Tests for the OpenXML patcher and Excel utilities."""

from __future__ import annotations

import os

import pytest

from html2docx.exceptions import RenderingError, ValidationError
from html2docx.models.chart import Chart, Series
from html2docx.renderers._excel_utils import index_to_column
from html2docx.renderers.office_chart_renderer import OfficeChartRenderer
from html2docx.services.openxml_patcher import OXmlPatcher


class TestIndexToColumn:
    """Tests for the Excel column index→letter converter."""

    def test_single_letters(self) -> None:
        assert index_to_column(1) == "A"
        assert index_to_column(2) == "B"
        assert index_to_column(26) == "Z"

    def test_double_letters(self) -> None:
        assert index_to_column(27) == "AA"
        assert index_to_column(28) == "AB"
        assert index_to_column(52) == "AZ"
        assert index_to_column(53) == "BA"

    def test_triple_letters(self) -> None:
        assert index_to_column(703) == "AAA"

    def test_invalid_index(self) -> None:
        with pytest.raises(ValueError, match="must be >= 1"):
            index_to_column(0)
        with pytest.raises(ValueError, match="must be >= 1"):
            index_to_column(-1)


class TestOfficeChartRenderer:
    """Tests for OfficeChartRenderer workbook generation."""

    def _make_chart(self, **kwargs) -> Chart:
        defaults = {
            "chart_id": "test",
            "chart_type": "bar",
            "title": "Test",
            "categories": ["A", "B"],
            "series": [Series(name="S1", values=[10.0, 20.0])],
        }
        defaults.update(kwargs)
        return Chart(**defaults)

    def test_create_workbook(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "chart.xlsx")
        chart = self._make_chart()
        result = OfficeChartRenderer.create_workbook(chart, path)

        assert result == path
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_create_workbook_multiple_series(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "multi.xlsx")
        chart = self._make_chart(
            series=[
                Series(name="S1", values=[10.0, 20.0]),
                Series(name="S2", values=[30.0, 40.0]),
            ]
        )
        OfficeChartRenderer.create_workbook(chart, path)
        assert os.path.exists(path)

    def test_validate_missing_chart_id(self) -> None:
        chart = self._make_chart(chart_id="")
        with pytest.raises(ValidationError, match="Chart ID"):
            OfficeChartRenderer.create_workbook(chart, "x.xlsx")

    def test_validate_no_categories(self) -> None:
        chart = self._make_chart(categories=[])
        with pytest.raises(ValidationError, match="no categories"):
            OfficeChartRenderer.create_workbook(chart, "x.xlsx")

    def test_validate_no_series(self) -> None:
        chart = self._make_chart(series=[])
        with pytest.raises(ValidationError, match="no series"):
            OfficeChartRenderer.create_workbook(chart, "x.xlsx")

    def test_validate_mismatched_lengths(self) -> None:
        chart = self._make_chart(
            categories=["A", "B", "C"],
            series=[Series(name="S", values=[1.0, 2.0])],  # only 2 values
        )
        with pytest.raises(ValidationError, match="values"):
            OfficeChartRenderer.create_workbook(chart, "x.xlsx")


class TestOXmlPatcher:
    """Tests for OXmlPatcher."""

    def test_inject_charts_file_not_found(self) -> None:
        with pytest.raises(RenderingError, match="not found"):
            OXmlPatcher.inject_charts("/nonexistent/file.docx", [{"idx": 1}])

    def test_inject_charts_empty_list(self, tmp_path: object) -> None:
        """Empty chart_files should be a no-op."""
        path = os.path.join(str(tmp_path), "test.docx")
        # Create a minimal docx first
        from html2docx.models.document import Document
        from html2docx.renderers.docx_renderer import DocxRenderer

        DocxRenderer.render(Document(), path)
        original_size = os.path.getsize(path)

        OXmlPatcher.inject_charts(path, [])
        assert os.path.getsize(path) == original_size

    def test_update_content_types_adds_xlsx(self) -> None:
        xml = b'<?xml version="1.0"?><Types></Types>'
        result = OXmlPatcher._update_content_types(
            xml, [{"idx": 1, "chart_id": "c1"}]
        )
        content = result.decode("utf-8")
        assert 'Extension="xlsx"' in content
        assert "chart1.xml" in content

    def test_update_relationships(self) -> None:
        xml = b'<?xml version="1.0"?><Relationships></Relationships>'
        result = OXmlPatcher._update_relationships(
            xml, [{"idx": 1, "chart_id": "c1"}]
        )
        content = result.decode("utf-8")
        assert "rIdChart1" in content
        assert "charts/chart1.xml" in content

    def test_create_drawing_xml(self) -> None:
        xml = OXmlPatcher._create_drawing_xml(1)
        assert "rIdChart1" in xml
        assert "Chart 1" in xml
        assert '<wp:extent cx="5486400"' in xml
