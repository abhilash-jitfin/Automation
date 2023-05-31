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
        for i, chunk in enumerate(pd.read_csv(self.filepath, chunksize=chunk_size)):
            base_name = f'chunk{chunk_number}.csv'
            if i == 0:
                chunk.to_csv(os.path.join(output_dir, base_name), index=False)
                column_names = chunk.columns  # Extract column headings from the first chunk
            else:
                chunk.to_csv(os.path.join(output_dir, base_name), index=False, header=False)

            # Append column headings to each split file
            if i > 0:
                with open(os.path.join(output_dir, base_name), 'r+') as file:
                    content = file.read()
                    file.seek(0, 0)
                    file.write(','.join(column_names) + '\n' + content)

            chunk_number += 1
