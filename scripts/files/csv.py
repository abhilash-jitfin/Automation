import os

import pandas as pd
from .base import BaseFile


class CsvFile(BaseFile):
    """Class representing a CSV file."""

    def split(self, output_dir: str, chunk_size: int) -> None:
        """Split the CSV file into chunks."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        chunk_number = 1
        for chunk in pd.read_csv(self.filepath, chunksize=chunk_size):
            base_name = f'chunk{chunk_number}.csv'
            print(base_name)
            chunk.to_csv(os.path.join(output_dir, base_name), index=False)
            chunk_number += 1
