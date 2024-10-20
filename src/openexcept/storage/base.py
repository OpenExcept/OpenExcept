from abc import ABC, abstractmethod
import typing as t
from datetime import datetime, timedelta

class VectorStorage(ABC):
    @abstractmethod
    def store_vector(self, vector: t.List[float], metadata: dict) -> str:
        pass

    @abstractmethod
    def find_similar(self, vector: t.List[float], threshold: float) -> t.List[tuple[str, float]]:
        pass

    @abstractmethod
    def increment_occurrence(self, group_id: str, timestamp: datetime):
        pass

    @abstractmethod
    def get_top_exceptions(self, limit: int, time_range: timedelta) -> t.List[dict]:
        pass