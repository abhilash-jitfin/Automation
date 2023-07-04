import os
from datetime import datetime

import pandas as pd

from ..files.csv import CsvFile
from ..files.excel import ExcelFile
from ..utils.settings import load_settings
from .abstract_task import BaseTask


class FileCombineTask(BaseTask):
    """Task to combine files in a directory into a single file."""

    description = "Combine files in a directory into a single file"

    FILE_CLASSES = {
        "csv": CsvFile,
        "xlsx": ExcelFile
        # Add other file types here
    }

    def __init__(self) -> None:
        """Initialize the task."""
        self.input_dir = None
        self.output_file = None
        self.settings = load_settings()

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        self.input_dir = input("Enter the input directory: ")
        self.check_input_directory()
        self.set_output_file()

    def check_input_directory(self) -> None:
        """Check if the input directory is valid."""
        if not os.path.isdir(self.input_dir):
            raise ValueError("Invalid input directory.")

    def set_output_file(self) -> None:
        """Set the output file path based on the current timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.output_file = os.path.join(self.input_dir, f"output_{timestamp}.xlsx")

    def execute(self) -> None:
        """Execute the task."""
        file_paths = self.get_file_paths()
        combined_df = self.combine_files(file_paths)
        self.save_combined_file(combined_df)
        print(f"Combined files saved to {self.output_file}")

    def get_file_paths(self) -> list[str]:
        """Get the file paths of all files in the input directory."""
        file_paths = []
        for file_name in os.listdir(self.input_dir):
            file_path = os.path.join(self.input_dir, file_name)
            if os.path.isfile(file_path):
                file_paths.append(file_path)
        return file_paths

    def combine_files(self, file_paths: list[str]) -> pd.DataFrame:
        """Combine the files into a single DataFrame."""
        dfs = []
        for file_path in file_paths:
            extension = file_path.split(".")[-1].lower()
            if extension not in self.FILE_CLASSES:
                continue
            file = self.FILE_CLASSES[extension](file_path)
            df = file.read()
            dfs.append(df)
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df

    def save_combined_file(self, combined_df: pd.DataFrame) -> None:
        """Save the combined DataFrame to the output file."""
        combined_df.to_excel(self.output_file, index=False)
