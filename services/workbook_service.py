from datetime import date, datetime

from openpyxl import load_workbook
from openpyxl.utils.cell import range_boundaries


class WorkbookService:
    def __init__(self, logger):
        self.logger = logger

    @staticmethod
    def _fmt(v):
        if v is None:
            return ""
        if isinstance(v, (date, datetime)):
            return v.strftime("%d.%m.%Y")
        return str(v)

    def read_view(self, xlsx_path: str, sheet_name: str, cell_range: str):
        wb = load_workbook(xlsx_path, data_only=True)
        if sheet_name not in wb.sheetnames:
            raise ValueError(f"Sheet '{sheet_name}' nicht gefunden")
        ws = wb[sheet_name]
        min_col, min_row, max_col, max_row = range_boundaries(cell_range)
        rows = []
        for r in range(min_row, max_row + 1):
            row = []
            for c in range(min_col, max_col + 1):
                row.append(self._fmt(ws.cell(row=r, column=c).value))
            rows.append(row)
        return {"sheet": sheet_name, "range": cell_range, "rows": rows}
