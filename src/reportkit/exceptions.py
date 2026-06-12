"""Custom exceptions for reportkit.

All public exceptions inherit from ReportKitError to allow
broad exception catching when desired.
"""

__all__ = [
    "ConversionError",
    "ParsingError",
    "RenderingError",
    "ReportKitError",
    "ValidationError",
]


class ReportKitError(Exception):
    """Base exception for all reportkit errors."""


class ConversionError(ReportKitError):
    """Raised when the overall conversion pipeline fails."""


class ValidationError(ReportKitError):
    """Raised when input data fails validation."""


class ParsingError(ReportKitError):
    """Raised when HTML or chart data cannot be parsed."""


class RenderingError(ReportKitError):
    """Raised when document rendering fails."""
