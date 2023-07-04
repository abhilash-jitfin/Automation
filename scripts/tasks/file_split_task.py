import os

from halo import Halo

from ..files.csv import CsvFile
from ..files.excel import ExcelFile
from ..utils.files import create_directory_if_not_exists, is_valid_directory_path
from ..utils.settings import load_settings
from ..utils.terminal import get_clean_input
from .abstract_task import BaseTask


class FileSplitTask(BaseTask):
    """Task to split a file into chunks."""

    description = "split a file into smaller chunks"

    FILE_CLASSES = {
        "csv": CsvFile,
        "xlsx": ExcelFile
        # Add other file types here
    }

    def __init__(self) -> None:
        """Initialize the task."""
        self.file = None
        self.settings = load_settings()

    def get_params(self) -> None:
        """Get parameters for the task from the user."""
        while True:
            file_path = get_clean_input("Enter the file path: ")
            extension = file_path.split(".")[-1].lower()
            if extension not in self.FILE_CLASSES:
                print(f"Unsupported file type: {extension}")
                continue
            break

        self.file = self.FILE_CLASSES[extension](file_path)
        self.output_dir = os.path.splitext(self.file.file_path)[0]
        create_directory_if_not_exists(self.output_dir)

        while True:
            try:
                self.chunk_size = get_clean_input("Enter the chunk size: ", int)
                break
            except Exception as e:
                print(str(e))
        print("\n")

    def execute(self) -> None:
        """Execute the task."""
        # spinner = Halo(text="Splitting File", spinner="dots")
        # spinner.start()
        try:
            self.file.split(self.output_dir, self.chunk_size)
        except Exception as e:
            print(f"Failed to split the file. Error: {e}")
            # spinner.fail(f"Failed to split the file. Error: {e}")
        # spinner.succeed("File splitting completed.")
        print("\nFile splitting completed.")
