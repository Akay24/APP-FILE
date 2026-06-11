import json

from bs4 import Tag

from app.models.chart import Chart, Series


class ChartParser:

    @staticmethod
    def parse(chart_tag: Tag, charts_data: dict = None) -> Chart:

        chart_id = chart_tag.get("data-chart-id", "")
        chart_type = chart_tag.get("data-chart-type", "bar")
        title = chart_tag.get("data-chart-title", "")

        config = {}
        config_attr = chart_tag.get("data-chart-config")
        if config_attr:
            try:
                config = json.loads(config_attr)
            except Exception:
                pass

        if charts_data and chart_id in charts_data:
            chart_info = charts_data[chart_id]
            chart_type = chart_info.get("chart_type", chart_type)
            title = chart_info.get("title", title)
            config = chart_info

        categories = config.get("categories", [])

        series = [
            Series(
                name=item["name"],
                values=item["values"]
            )
            for item in config.get("series", [])
        ]

        return Chart(
            chart_id=chart_id,
            chart_type=chart_type,
            title=title,
            categories=categories,
            series=series
        )