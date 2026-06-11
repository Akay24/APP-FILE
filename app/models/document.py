from dataclasses import dataclass, field
from typing import List

# Import unified Chart model
from app.models.chart import Chart, Series


@dataclass
class Paragraph:
    text: str
    tag: str = "p"


@dataclass
class Table:
    headers: list
    rows: list


# Re-export Chart from chart.py for backward compatibility
__all__ = [
    "Paragraph",
    "Table",
    "Chart",
    "Document"
]


@dataclass
class Document:
    elements: List = field(default_factory=list)