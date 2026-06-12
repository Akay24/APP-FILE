"""Basic usage example for reportkit.

Demonstrates converting HTML with tables and charts to both DOCX and PDF.
"""

from reportkit import convert_html_to_docx, convert_html_to_pdf

# ── HTML content with a table and chart placeholder ──────────────────────
html = """
<h1>Quarterly Financial Report</h1>
<p>This report summarizes our financial performance over the first three quarters.</p>

<table>
  <thead>
    <tr>
      <th>Quarter</th>
      <th>Revenue ($M)</th>
      <th>Expenses ($M)</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Q1</td><td>120</td><td>80</td></tr>
    <tr><td>Q2</td><td>150</td><td>95</td></tr>
    <tr><td>Q3</td><td>180</td><td>110</td></tr>
  </tbody>
</table>

<h2>Revenue Trend</h2>
<div data-chart-id="revenueGrowth"
     data-chart-type="bar"
     data-chart-title="Quarterly Revenue Trend"></div>

<h2>Revenue Distribution</h2>
<div data-chart-id="revenueShare"
     data-chart-type="pie"
     data-chart-title="Revenue Distribution by Quarter"></div>
"""

# ── Chart data ───────────────────────────────────────────────────────────
charts = {
    "revenueGrowth": {
        "chart_id": "revenueGrowth",
        "chart_type": "bar",
        "title": "Quarterly Revenue Trend",
        "categories": ["Q1", "Q2", "Q3"],
        "series": [
            {"name": "Revenue ($M)", "values": [120, 150, 180]},
        ],
    },
    "revenueShare": {
        "chart_id": "revenueShare",
        "chart_type": "pie",
        "title": "Revenue Distribution by Quarter",
        "categories": ["Q1", "Q2", "Q3"],
        "series": [
            {"name": "Revenue ($M)", "values": [120, 150, 180]},
        ],
    },
}

# ── Generate both outputs ────────────────────────────────────────────────
if __name__ == "__main__":
    docx_path = convert_html_to_docx(html, "report.docx", charts_data=charts)
    print(f"✅ DOCX generated: {docx_path}")

    pdf_path = convert_html_to_pdf(html, "report.pdf", charts_data=charts)
    print(f"✅ PDF generated: {pdf_path}")
