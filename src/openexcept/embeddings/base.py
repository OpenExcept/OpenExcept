from abc import ABC, abstractmethod
from ..core import ExceptionEvent
import typing as t

class VectorEmbedding(ABC):
    @abstractmethod
    def embed(self, exception: ExceptionEvent) -> t.List[float]:
        pass