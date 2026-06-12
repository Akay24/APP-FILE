"""HTML table parser.

Extracts structured table data from BeautifulSoup <table> elements.
"""

from __future__ import annotations

from bs4 import Tag

from reportkit.models.table import Table

__all__ = ["TableParser"]


class TableParser:
    """Parses an HTML ``<table>`` tag into a :class:`Table` model."""

    @staticmethod
    def parse(table_tag: Tag) -> Table:
        """Extract headers and row data from an HTML table element.

        Args:
            table_tag: A BeautifulSoup ``<table>`` :class:`Tag`.

        Returns:
            A :class:`Table` with *headers* from ``<th>`` elements in the
            first row and *rows* from subsequent ``<td>``/``<th>`` cells.
        """
        rows = table_tag.find_all("tr")

        if not rows:
            return Table()

        headers: list[str] = []
        first_row_headers = rows[0].find_all("th")

        if first_row_headers:
            headers = [cell.get_text(strip=True) for cell in first_row_headers]
            data_rows = rows[1:]
        else:
            data_rows = rows

        parsed_rows: list[list[str]] = [
            [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
            for row in data_rows
        ]

        return Table(headers=headers, rows=parsed_rows)
