"""Excel column-index utility.

Converts 1-based numeric column indices to Excel-style column letters
(A, B, …, Z, AA, AB, …).  Used by :mod:`office_chart_renderer`.
"""

from __future__ import annotations

__all__ = ["index_to_column"]


def index_to_column(index: int) -> str:
    """Convert a 1-based column index to an Excel column letter.

    Args:
        index: Column number (1 = A, 2 = B, …, 27 = AA).

    Returns:
        The corresponding Excel column letter(s).

    Raises:
        ValueError: If *index* is less than 1.

    Examples:
        >>> index_to_column(1)
        'A'
        >>> index_to_column(26)
        'Z'
        >>> index_to_column(27)
        'AA'
    """
    if index < 1:
        raise ValueError(f"Column index must be >= 1, got {index}")

    result = ""
    while index > 0:
        index -= 1
        result = chr(65 + (index % 26)) + result
        index //= 26
    return result
