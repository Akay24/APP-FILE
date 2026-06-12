"""Custom exceptions for html2docx.

All public exceptions inherit from Html2DocxError to allow
broad exception catching when desired.
"""

__all__ = [
    "ConversionError",
    "Html2DocxError",
    "ParsingError",
    "RenderingError",
    "ValidationError",
]


class Html2DocxError(Exception):
    """Base exception for all html2docx errors."""


class ConversionError(Html2DocxError):
    """Raised when the overall conversion pipeline fails."""


class ValidationError(Html2DocxError):
    """Raised when input data fails validation."""


class ParsingError(Html2DocxError):
    """Raised when HTML or chart data cannot be parsed."""


class RenderingError(Html2DocxError):
    """Raised when document rendering fails."""
