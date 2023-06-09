import os
from typing import List, Optional

import pandas as pd
from openpyxl import load_workbook

from .base import BaseFile


class ExcelFile(BaseFile):
    """Class representing an Excel file."""

    def split(self, output_dir: str, chunk_size: int) -> None:
        """Split the Excel file into chunks."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        workbook = load_workbook(self.file_path)
        sheet = workbook.active
        total_rows = sheet.max_row
        headings = [cell.value for cell in sheet[1]]

        for i in range(2, total_rows, chunk_size):
            data = sheet[i: i + chunk_size]
            df = pd.DataFrame(([cell.value for cell in row] for row in data), columns=headings)
            df.to_excel(
                os.path.join(output_dir, f'chunk{i//chunk_size + 1}.xlsx'), index=False
            )

    def read(self, sheet: Optional[str] = None, columns_to_read: Optional[List[str]] = None) -> pd.DataFrame:
        df = pd.read_excel(self.file_path, sheet_name=sheet if sheet is not None else 0,
                           usecols=columns_to_read)
        return df
