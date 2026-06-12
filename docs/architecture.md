# Architecture

## System Overview

html2docx-converter transforms HTML content into native Microsoft Word (.docx) and PDF documents. The system follows a **parse → model → render** pipeline architecture.

## Data Flow

```
HTTP Request / Library Call
        │
        ▼
  ┌─────────────┐
  │  HtmlParser  │ ← Parses HTML via BeautifulSoup
  │  ChartParser │ ← Extracts chart div attributes
  │  TableParser │ ← Extracts table structure
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  Document    │ ← Intermediate representation
  │  (elements)  │   Contains: Paragraph, Table, Chart
  └──────┬──────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│  DOCX  │ │  PDF   │
│Renderer│ │Renderer│
└───┬────┘ └───┬────┘
    │          │
    ▼          ▼
  .docx      .pdf
```

## Module Responsibilities

### Models (`html2docx.models`)

Pure data classes with no behavior:

- **`Chart`** / **`Series`**: Chart definition with categories and data series
- **`Table`**: Structured headers + rows
- **`Document`** / **`Paragraph`**: Ordered element container

### Parsers (`html2docx.parsers`)

Stateless parsers that convert HTML into models:

- **`HtmlParser`**: Top-level dispatcher — walks HTML children and delegates
- **`TableParser`**: Converts `<table>` tags to `Table` models
- **`ChartParser`**: Converts `<div data-chart-*>` to `Chart` models
- **`ChartJsAdapter`**: Converts Chart.js configs to `Chart` models

### Renderers (`html2docx.renderers`)

Convert models to output formats:

- **`DocxRenderer`**: Uses python-docx for structure, python-pptx for chart XML generation, and OXmlPatcher for injection
- **`PdfRenderer`**: Uses ReportLab for document layout and matplotlib for chart images

### Services (`html2docx.services`)

Orchestration layer:

- **`ConversionService`**: Ties parsing and rendering together
- **`OXmlPatcher`**: Low-level ZIP/XML manipulation for DOCX chart injection

### API (`html2docx.api`)

Optional Flask REST layer:

- **`routes.py`**: Blueprint factory with `/convert/docx` and `/convert/pdf` endpoints

## Chart Injection (DOCX)

Native Office charts in DOCX are achieved through a multi-step process:

1. A temporary PPTX is created using python-pptx with the chart
2. The chart XML, relationships, and embedded Excel workbook are extracted from the PPTX ZIP
3. These are injected into the DOCX ZIP via OXmlPatcher
4. Document.xml is patched to replace placeholder text with drawing XML references

This produces charts that are **editable in Microsoft Word** — not static images.

## Chart Rendering (PDF)

PDF charts are rendered using matplotlib:

1. A matplotlib Figure is created for each chart type (bar, line, pie, area)
2. The figure is saved to an in-memory PNG buffer at 150 DPI
3. ReportLab embeds the image in the PDF document flow
