"""
OpenXML patching for chart injection.

Handles all XML manipulation for injecting charts into DOCX files.
Provides clean API for chart injection without low-level XML details.
"""
import zipfile
import os
import re
from typing import List, Dict, Any


class OXmlPatcher:
    """Patches DOCX files with Office charts and workbooks."""

    @staticmethod
    def inject_charts(
        docx_path: str,
        chart_files: List[Dict[str, Any]]
    ) -> None:
        """
        Inject charts and workbooks into DOCX.

        Args:
            docx_path: Path to DOCX file
            chart_files: List of chart data dicts with:
                - idx: Chart index (1-based)
                - chart_id: Unique chart identifier
                - xml: Chart XML bytes
                - xlsx: Excel workbook bytes
                - rels: Chart relationships XML bytes

        Raises:
            FileNotFoundError: If DOCX not found
            ValueError: If chart data invalid
        """
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"DOCX not found: {docx_path}")

        if not chart_files:
            return

        temp_docx = docx_path + ".tmp"

        try:
            with zipfile.ZipFile(docx_path, "r") as zin:
                with zipfile.ZipFile(temp_docx, "w") as zout:
                    for item in zin.infolist():
                        data = zin.read(item.filename)

                        if item.filename == "word/document.xml":
                            data = OXmlPatcher._update_document_xml(
                                data, chart_files
                            )
                        elif item.filename == "word/_rels/document.xml.rels":
                            data = OXmlPatcher._update_relationships(
                                data, chart_files
                            )
                        elif item.filename == "[Content_Types].xml":
                            data = OXmlPatcher._update_content_types(
                                data, chart_files
                            )

                        zout.writestr(item, data)

                    # Write chart files
                    for chart in chart_files:
                        idx = chart["idx"]
                        workbook_name = f"Microsoft_Excel_Sheet{idx}.xlsx"

                        zout.writestr(
                            f"word/charts/chart{idx}.xml",
                            chart["xml"]
                        )
                        zout.writestr(
                            f"word/embeddings/{workbook_name}",
                            chart["xlsx"]
                        )

                        # Update and write relationships
                        rels_content = chart["rels"].decode("utf-8")
                        rels_content = re.sub(
                            r'Target="\.\./embeddings/Microsoft_Excel_.*\.xlsx"',
                            f'Target="../embeddings/{workbook_name}"',
                            rels_content,
                        )
                        zout.writestr(
                            f"word/charts/_rels/chart{idx}.xml.rels",
                            rels_content.encode("utf-8"),
                        )

        finally:
            if os.path.exists(docx_path):
                os.remove(docx_path)
            os.rename(temp_docx, docx_path)

    @staticmethod
    def _update_document_xml(
        xml_data: bytes,
        chart_files: List[Dict[str, Any]]
    ) -> bytes:
        """
        Update document.xml with chart drawing references.

        Replaces chart placeholders with Office drawing XML.

        Args:
            xml_data: Original document.xml bytes
            chart_files: Chart data

        Returns:
            bytes: Updated XML
        """
        content = xml_data.decode("utf-8")

        for chart in chart_files:
            chart_id = chart["chart_id"]
            idx = chart["idx"]

            placeholder = f"CHART_PLACEHOLDER_{chart_id}"

            drawing_xml = OXmlPatcher._create_drawing_xml(idx)

            pattern = rf"<w:r\b[^>]*>(?:(?!</w:r>).)*?{re.escape(placeholder)}.*?</w:r>"
            if re.search(pattern, content):
                content = re.sub(pattern, drawing_xml, content)
            else:
                content = content.replace(placeholder, drawing_xml)

        return content.encode("utf-8")

    @staticmethod
    def _update_relationships(
        xml_data: bytes,
        chart_files: List[Dict[str, Any]]
    ) -> bytes:
        """
        Update document.xml.rels with chart relationships.

        Args:
            xml_data: Original relationships XML bytes
            chart_files: Chart data

        Returns:
            bytes: Updated XML
        """
        content = xml_data.decode("utf-8")

        rel_tags = []
        for chart in chart_files:
            idx = chart["idx"]
            rel_tags.append(
                f'<Relationship Id="rIdChart{idx}" '
                f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart" '
                f'Target="charts/chart{idx}.xml"/>'
            )

        all_rels = "".join(rel_tags)
        content = content.replace("</Relationships>", f"{all_rels}</Relationships>")

        return content.encode("utf-8")

    @staticmethod
    def _update_content_types(
        xml_data: bytes,
        chart_files: List[Dict[str, Any]]
    ) -> bytes:
        """
        Update [Content_Types].xml with chart and workbook types.

        Args:
            xml_data: Original content types XML bytes
            chart_files: Chart data

        Returns:
            bytes: Updated XML
        """
        content = xml_data.decode("utf-8")

        # Ensure xlsx default type
        if 'Extension="xlsx"' not in content:
            default_xlsx = (
                '<Default Extension="xlsx" '
                'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"/>'
            )
            content = content.replace("</Types>", f"{default_xlsx}</Types>")

        # Add chart overrides
        overrides = []
        for chart in chart_files:
            idx = chart["idx"]
            overrides.append(
                f'<Override PartName="/word/charts/chart{idx}.xml" '
                f'ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"/>'
            )

        all_overrides = "".join(overrides)
        content = content.replace("</Types>", f"{all_overrides}</Types>")

        return content.encode("utf-8")

    @staticmethod
    def _create_drawing_xml(chart_idx: int) -> str:
        """
        Create Office drawing XML for chart reference.

        Args:
            chart_idx: Chart index (1-based)

        Returns:
            str: Drawing XML snippet
        """
        return (
            f'<w:r>'
            f'<w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="5486400" cy="3657600"/>'
            f'<wp:docPr id="{100 + chart_idx}" name="Chart {chart_idx}"/>'
            f'<wp:cNvGraphicFramePr>'
            f'<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
            f'</wp:cNvGraphicFramePr>'
            f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            f'<c:chart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
            f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            f'r:id="rIdChart{chart_idx}"/>'
            f'</a:graphicData>'
            f'</a:graphic>'
            f'</wp:inline>'
            f'</w:drawing>'
            f'</w:r>'
        )


# Legacy compatibility
class OpenXmlPatcher:
    """Deprecated: Use OXmlPatcher instead."""

    @staticmethod
    def inspect(docx_path):
        """Inspect DOCX for charts and embeddings."""
        with zipfile.ZipFile(docx_path) as z:
            for name in z.namelist():
                if "chart" in name:
                    print(name)
                if "embedding" in name:
                    print(name)