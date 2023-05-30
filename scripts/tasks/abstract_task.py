from abc import ABC, abstractmethod


class BaseTask(ABC):
    description = "Base task"
    
    @abstractmethod
    def get_params(self) -> None:
        raise NotImplementedError("Sub class should implement this function.")

    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError("Sub class should implement this function.")
