from abc import ABC, abstractmethod


class BaseFile(ABC):
    """Abstract base class for file types."""

    def __init__(self, filepath: str) -> None:
        """Initialize the BaseFile with its filepath."""
        self.filepath = filepath

    @abstractmethod
    def split(self, output_dir: str, chunk_size: int) -> None:
        """Split the file into chunks."""
        pass
