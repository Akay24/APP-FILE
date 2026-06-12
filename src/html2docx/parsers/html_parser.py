"""HTML-to-Document parser.

Walks the top-level children of an HTML fragment and converts recognised
elements (headings, paragraphs, tables, chart divs) into a :class:`Document`.
"""

from __future__ import annotations

import logging
from typing import Any

from bs4 import BeautifulSoup, Tag

from html2docx.models.document import Document, Paragraph
from html2docx.parsers.chart_parser import ChartParser
from html2docx.parsers.table_parser import TableParser

__all__ = ["HtmlParser"]

logger = logging.getLogger(__name__)

_HEADING_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})


class HtmlParser:
    """Parses an HTML string into a :class:`Document` model."""

    @staticmethod
    def parse(
        html: str,
        charts_data: dict[str, dict[str, Any]] | None = None,
    ) -> Document:
        """Parse HTML content into a structured :class:`Document`.

        Supported HTML elements:
        - ``<h1>``-``<h6>`` -> :class:`Paragraph` with appropriate tag
        - ``<p>`` → :class:`Paragraph`
        - ``<table>`` → :class:`Table`
        - ``<div data-chart-id="...">`` → :class:`Chart`

        Args:
            html: Raw HTML string to parse.
            charts_data: Optional chart data dict keyed by chart ID,
                used to supplement chart elements found in the HTML.

        Returns:
            A :class:`Document` containing the parsed elements in order.
        """
        soup = BeautifulSoup(html, "html.parser")

        document = Document()
        body = soup.body if soup.body is not None else soup

        for element in body.children:
            if not isinstance(element, Tag):
                continue

            tag_name = element.name
            if tag_name is None:
                continue

            if tag_name in _HEADING_TAGS:
                document.elements.append(
                    Paragraph(
                        text=element.get_text(strip=True),
                        tag=tag_name,
                    )
                )

            elif tag_name == "p":
                document.elements.append(
                    Paragraph(
                        text=element.get_text(strip=True),
                        tag="p",
                    )
                )

            elif tag_name == "table":
                document.elements.append(TableParser.parse(element))

            elif tag_name == "div" and element.get("data-chart-id"):
                chart = ChartParser.parse(element, charts_data)
                document.elements.append(chart)

            else:
                logger.debug("Skipping unsupported element: <%s>", tag_name)

        return document
