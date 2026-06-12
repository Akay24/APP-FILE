# reportkit

> Convert HTML content with tables and charts to production-quality DOCX and PDF documents with native editable charts.

[![CI](https://github.com/Akay24/reportkit/actions/workflows/ci.yml/badge.svg)](https://github.com/Akay24/reportkit/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

**reportkit** transforms HTML content — including headings, paragraphs, tables, and interactive charts — into native Microsoft Word (.docx) and PDF documents.

Charts are injected as **native Office charts** in DOCX (editable in Word) and as **high-quality matplotlib renders** in PDF.

### Key Features

- 📄 **Dual output**: Generate both DOCX and PDF from the same HTML
- 📊 **Native Office charts**: Bar, line, pie, doughnut, and area charts — **editable in Word**
- 📋 **HTML table support**: Full header/row parsing with styled output
- 🔌 **Chart.js integration**: Pass Chart.js configs directly from your frontend
- 🌐 **REST API**: Optional Flask-based API for service deployment
- 📦 **Library-first**: Use as a Python library or as a web service
- 🔒 **Production-ready**: Type-safe, tested, with proper error handling

## Installation

### Library only (no web server)

```bash
pip install reportkit
```

### With Flask API

```bash
pip install reportkit[api]
```

### Development

```bash
git clone https://github.com/Akay24/reportkit.git
cd reportkit
pip install -e ".[dev]"
```

## Quick Start

### As a Python Library

```python
from reportkit import convert_html_to_docx, convert_html_to_pdf

html = """
<h1>Quarterly Report</h1>
<p>Performance summary for Q1-Q3.</p>
<table>
  <thead>
    <tr><th>Quarter</th><th>Revenue</th></tr>
  </thead>
  <tbody>
    <tr><td>Q1</td><td>$120M</td></tr>
    <tr><td>Q2</td><td>$150M</td></tr>
  </tbody>
</table>
"""

# Generate DOCX (charts are editable in Word!)
convert_html_to_docx(html, "report.docx")

# Generate PDF
convert_html_to_pdf(html, "report.pdf")
```

### With Charts

```python
from reportkit import convert_html_to_docx

html = """
<h1>Sales Report</h1>
<div data-chart-id="sales" data-chart-type="bar" data-chart-title="Sales by Region"></div>
"""

charts = {
    "sales": {
        "chart_id": "sales",
        "chart_type": "bar",
        "title": "Sales by Region",
        "categories": ["North", "South", "East", "West"],
        "series": [
            {"name": "2025", "values": [120, 90, 150, 80]},
            {"name": "2026", "values": [140, 110, 170, 95]},
        ],
    }
}

convert_html_to_docx(html, "sales_report.docx", charts_data=charts)
```

### With Chart.js Payloads

```python
from reportkit import ChartJsAdapter, convert_html_to_docx

# Adapt a Chart.js config from your frontend
chart = ChartJsAdapter.adapt({
    "chartId": "revenue",
    "chartConfig": {
        "type": "bar",
        "data": {
            "labels": ["Q1", "Q2", "Q3"],
            "datasets": [
                {"label": "Revenue", "data": [120, 150, 180]}
            ]
        }
    }
})

print(chart.chart_id)    # "revenue"
print(chart.chart_type)  # "bar"
```

### As a REST API

```bash
# Start the server
REPORTKIT_DEBUG=1 python -m reportkit.app
```

```bash
# Convert to DOCX
curl -X POST http://localhost:5000/convert/docx \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Hello World</h1>"}' \
  --output report.docx

# Convert to PDF
curl -X POST http://localhost:5000/convert/pdf \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Hello World</h1>"}' \
  --output report.pdf
```

## API Reference

### Top-Level Functions

| Function | Description |
|---|---|
| `convert_html_to_docx(html, path, charts_data=None)` | Convert HTML to DOCX (editable charts) |
| `convert_html_to_pdf(html, path, charts_data=None)` | Convert HTML to PDF |
| `convert(html, path, format, charts_data=None)` | Convert to any format |

### Models

| Class | Description |
|---|---|
| `Chart` | Chart with categories and series |
| `Series` | A single data series (name + values) |
| `Document` | Ordered collection of elements |
| `Paragraph` | Text block or heading |
| `Table` | Structured table (headers + rows) |

### REST Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/convert/docx` | Convert HTML to DOCX (returns file) |
| POST | `/convert/pdf` | Convert HTML to PDF (returns file) |

### Request Body

```json
{
  "html": "<h1>Title</h1><p>Content</p>",
  "charts": [
    {
      "chart_id": "myChart",
      "chart_type": "bar",
      "title": "My Chart",
      "categories": ["A", "B"],
      "series": [{"name": "Data", "values": [10, 20]}]
    }
  ]
}
```

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `REPORTKIT_DEBUG` | `false` | Enable debug mode |
| `REPORTKIT_MAX_CONTENT_MB` | `16` | Max request body size (MB) |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=reportkit --cov-report=term-missing

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Build package
python -m build
```

## Project Structure

```
reportkit/
├── src/reportkit/
│   ├── __init__.py          # Public API
│   ├── app.py               # Flask factory
│   ├── exceptions.py        # Custom exceptions
│   ├── api/                 # REST endpoints
│   ├── models/              # Data models
│   ├── parsers/             # HTML & chart parsers
│   ├── renderers/           # DOCX & PDF renderers
│   └── services/            # Conversion orchestration
├── tests/                   # Test suite
├── pyproject.toml           # Package configuration
└── README.md
```

## License

MIT — see [LICENSE](LICENSE) for details.
