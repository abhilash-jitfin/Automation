from abc import ABC, abstractmethod


class BaseFile(ABC):
    """Abstract base class for file types."""

    def __init__(self, file_path: str) -> None:
        """Initialize the BaseFile with its file_path."""
        self.file_path = file_path

    @abstractmethod
    def split(self, output_dir: str, chunk_size: int) -> None:
        """Split the file into chunks."""
        pass

    @abstractmethod
    def read(self):
        """Read the file."""
        pass
