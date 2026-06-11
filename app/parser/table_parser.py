from bs4 import Tag

from app.models.table import Table


class TableParser:

    @staticmethod
    def parse(table_tag: Tag) -> Table:
        rows = table_tag.find_all("tr")

        if not rows:
            return Table()

        headers = []

        first_row_headers = rows[0].find_all("th")

        if first_row_headers:
            headers = [
                cell.get_text(strip=True)
                for cell in first_row_headers
            ]
            data_rows = rows[1:]
        else:
            data_rows = rows

        parsed_rows = []

        for row in data_rows:
            cells = row.find_all(["td", "th"])

            parsed_rows.append([
                cell.get_text(strip=True)
                for cell in cells
            ])

        return Table(
            headers=headers,
            rows=parsed_rows
        )