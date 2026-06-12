# API Reference

## Top-Level Functions

### `convert_html_to_docx(html, output_path, charts_data=None)`

Convert HTML to a Microsoft Word (.docx) file.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `html` | `str` | Raw HTML string |
| `output_path` | `str` | Output file path |
| `charts_data` | `dict \| None` | Chart data keyed by chart ID |

**Returns:** `str` — the output path.

**Raises:** `ConversionError` on failure.

---

### `convert_html_to_pdf(html, output_path, charts_data=None)`

Convert HTML to a PDF file.

Same parameters and behavior as `convert_html_to_docx`.

---

### `convert(html, output_path, output_format, charts_data=None)`

Convert HTML to either DOCX or PDF.

**Additional Parameter:**

| Parameter | Type | Description |
|---|---|---|
| `output_format` | `OutputFormat` | `OutputFormat.DOCX` or `OutputFormat.PDF` |

---

## Models

### `Chart`

```python
@dataclass
class Chart:
    chart_id: str = ""
    chart_type: str = "bar"    # "bar", "line", "pie", "area"
    title: str = ""
    categories: list[str]
    series: list[Series]
```

### `Series`

```python
@dataclass(frozen=True)
class Series:
    name: str
    values: list[float]
```

### `Table`

```python
@dataclass
class Table:
    headers: list[str]
    rows: list[list[str]]
```

### `Document`

```python
@dataclass
class Document:
    elements: list[Paragraph | Table | Chart]
```

### `Paragraph`

```python
@dataclass(frozen=True)
class Paragraph:
    text: str
    tag: str = "p"   # "p", "h1"–"h6"
```

---

## ChartJsAdapter

### `ChartJsAdapter.adapt(chartjs_payload) -> Chart`

Converts a Chart.js configuration dict to a `Chart` model.

**Expected payload:**

```json
{
    "chartId": "uniqueId",
    "chartConfig": {
        "type": "bar",
        "data": {
            "labels": ["A", "B"],
            "datasets": [
                {"label": "Series 1", "data": [10, 20]}
            ]
        }
    }
}
```

**Supported types:** `bar`, `line`, `pie`, `doughnut`, `area`

---

## Exceptions

| Exception | Base | Description |
|---|---|---|
| `ReportKitError` | `Exception` | Base for all reportkit errors |
| `ConversionError` | `ReportKitError` | Pipeline failure |
| `ValidationError` | `ReportKitError` | Input validation failure |
| `ParsingError` | `ReportKitError` | HTML/chart parsing failure |
| `RenderingError` | `ReportKitError` | Rendering failure |

---

## REST API

### `POST /convert/docx`

Convert HTML to DOCX. Returns the file as a download.

### `POST /convert/pdf`

Convert HTML to PDF. Returns the file as a download.

**Request Body (both endpoints):**

```json
{
    "html": "<h1>Title</h1>",
    "charts": [...],
    "chartjs_payloads": [...]
}
```

**Response:** Binary file download on success, JSON error on failure.
