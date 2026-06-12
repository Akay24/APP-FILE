# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-11

### Added

- HTML-to-DOCX conversion with native Office charts
- HTML-to-PDF conversion with matplotlib chart rendering
- Chart.js payload adapter for frontend integration
- Support for bar, line, pie, doughnut, and area chart types
- HTML parsing for headings (h1–h6), paragraphs, tables, and chart divs
- Flask API with `/convert/docx` and `/convert/pdf` endpoints
- Comprehensive test suite with >80% coverage
- Full type annotations (mypy strict compatible)
- Production-grade pyproject.toml packaging
- CI/CD via GitHub Actions
