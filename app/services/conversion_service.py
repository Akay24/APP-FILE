from app.parser.html_parser import HtmlParser
from app.renderers.docx_renderer import DocxRenderer


class ConversionService:

    @staticmethod
    def html_to_docx(
        html: str,
        output_path: str,
        charts_data: dict = None
    ):

        document = HtmlParser.parse(html, charts_data)

        DocxRenderer.render(
            document,
            output_path
        )

        return output_path