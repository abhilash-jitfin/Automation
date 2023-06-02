from abc import ABC, abstractmethod

from halo import Halo

from ..files.csv import CsvFile
from ..files.excel import ExcelFile
from ..utils.settings import load_settings
from .abstract_task import BaseTask


class FileSplitTask(BaseTask):
    """Task to split a file into chunks."""

    description = "split a file into smaller chunks"

    FILE_CLASSES = {
        'csv': CsvFile,
        'xlsx': ExcelFile
        # Add other file types here
    }

    def __init__(self) -> None:
        """Initialize the task."""
        self.file = None
        self.settings = load_settings()

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        filepath = input("Enter the file path: ")
        extension = filepath.split('.')[-1].lower()

        if extension not in self.FILE_CLASSES:
            raise ValueError(f"Unsupported file type: {extension}")

        self.file = self.FILE_CLASSES[extension](filepath)
        self.output_dir = input("Enter the output directory: ")
        self.chunk_size = int(input("Enter the chunk size: "))

    def execute(self) -> None:
        """Execute the task."""
        spinner = Halo(text="Splitting File", spinner="dots")
        spinner.start()
        try:
            self.file.split(self.output_dir, self.chunk_size)
        except Exception as e:
            spinner.fail(f"Failed to split the file. Error: {e}")
        spinner.succeed("File splitting completed.")
