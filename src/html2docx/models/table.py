"""Table data model.

Single source of truth for table representation throughout the package.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["Table"]


@dataclass(slots=True)
class Table:
    """An HTML table parsed into structured data.

    Attributes:
        headers: Column header strings from <th> elements.
        rows: List of rows, each a list of cell strings from <td> elements.
    """

    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
