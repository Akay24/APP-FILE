"""Document model — the intermediate representation between parsing and rendering.

An HTML document is parsed into a Document containing an ordered list of
Paragraph, Table, and Chart elements. Renderers consume this model to
produce DOCX or PDF output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

from reportkit.models.chart import Chart
from reportkit.models.table import Table

__all__ = ["Document", "DocumentElement", "Paragraph"]

#: Union type for all elements that can appear in a Document.
DocumentElement = Union["Paragraph", Table, Chart]


@dataclass(frozen=True, slots=True)
class Paragraph:
    """A text block or heading.

    Attributes:
        text: The plain-text content.
        tag: The originating HTML tag ("p", "h1"-"h6").
    """

    text: str
    tag: str = "p"


@dataclass(slots=True)
class Document:
    """Ordered collection of document elements.

    Attributes:
        elements: Paragraphs, tables, and charts in document order.
    """

    elements: list[DocumentElement] = field(default_factory=list)
