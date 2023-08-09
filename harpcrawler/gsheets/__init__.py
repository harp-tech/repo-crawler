import gspread
import pandas as pd
import json
from typing import Optional, Dict


class HarpSpreadsheet:

    def __init__(
        self,
        spreadsheet: Optional[str] = None,
        credentials: Optional[str | Dict] = None) -> None:

        if credentials:
            if isinstance(credentials, str):
                credentials = json.loads(credentials, strict=False)
            self.gc = gspread.service_account_from_dict(credentials)
        else:
            self.gc = gspread.service_account()
        self.spreadsheet = spreadsheet
        self._sh = None
        self.current_worksheet = None

    def open_spreadsheet(self) -> gspread.Spreadsheet:
        if self._sh is None:
            self._sh = self.gc.open(self.spreadsheet)
        return self._sh

    def get_worksheet(self, title: str) -> gspread.worksheet:
        if self._sh is None:
            raise ValueError("No valid spreadsheet found. Try self.open_spreadsheet() first.")
        self.current_worksheet = self._sh.worksheet(title=title)
        return self.current_worksheet

    def add_worksheet(self, title: str) -> gspread.worksheet:
        if self._sh is None:
            raise ValueError("No valid spreadsheet found. Try self.open_spreadsheet() first.")
        self.current_worksheet = self._sh.add_worksheet(title=title, rows=100,cols=100)
        return self.current_worksheet

    def del_worksheet(self) -> None:
        if self._sh is None:
            raise ValueError("No valid spreadsheet found. Try self.open_spreadsheet() first.")
        if self.current_worksheet is None:
            raise ValueError("No valid worksheet found. Try self.add_worksheet(title) first.")
        self._sh.del_worksheet(worksheet=self.current_worksheet)
        self.current_worksheet = None

    def update_spreadsheet(self, title: str, table: pd.DataFrame) -> None:
        try:
            _ = self.get_worksheet(title=title)
        except gspread.WorksheetNotFound:
            _ = self.add_worksheet(title=title)
        self.current_worksheet.clear()
        self.current_worksheet.update([table.columns.values.tolist()] + table.values.tolist())
        self.current_worksheet.freeze(cols=1)