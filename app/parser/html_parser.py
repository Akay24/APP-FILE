from bs4 import BeautifulSoup

from app.models.document import Document, Paragraph
from app.parser.table_parser import TableParser
from app.parser.chart_parser import ChartParser


class HtmlParser:

    @staticmethod
    def parse(html: str, charts_data: dict = None) -> Document:
        soup = BeautifulSoup(html, "html.parser")

        document = Document()

        body = soup.body if soup.body is not None else soup

        for element in body.children:

            if getattr(element, "name", None) is None:
                continue

            # Headings
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:

                document.elements.append(
                    Paragraph(
                        text=element.get_text(strip=True),
                        tag=element.name
                    )
                )

            # Paragraphs
            elif element.name == "p":

                document.elements.append(
                    Paragraph(
                        text=element.get_text(strip=True),
                        tag="p"
                    )
                )

            # Tables
            elif element.name == "table":

                document.elements.append(
                    TableParser.parse(element)
                )

            # Charts
            elif (
                element.name == "div"
                and element.get("data-chart-id")
            ):

                chart = ChartParser.parse(
                    element,
                    charts_data
                )

                document.elements.append(chart)

        return document