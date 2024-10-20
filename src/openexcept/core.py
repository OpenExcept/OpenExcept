from datetime import datetime, timedelta
import typing as t
from abc import ABC, abstractmethod

class ExceptionEvent:
    def __init__(self, message: str, type: str, timestamp: datetime = None, stack_trace: str = "", context: dict = None):
        self.message = message
        self.type = type
        self.timestamp = timestamp or datetime.now()
        self.stack_trace = stack_trace
        self.context = context or {}

class GroupingResult:
    def __init__(self, group_id: str, confidence: float, similar_groups: t.List[str] = None, is_new_group: bool = False):
        self.group_id = group_id
        self.confidence = confidence
        self.similar_groups = similar_groups or []
        self.is_new_group = is_new_group

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

class VectorEmbedding(ABC):
    @abstractmethod
    def embed(self, exception: ExceptionEvent) -> t.List[float]:
        pass

class ExceptionGrouper:
    def __init__(self, storage: VectorStorage, embedding: VectorEmbedding, similarity_threshold: float):
        self.storage = storage
        self.embedding = embedding
        self.similarity_threshold = similarity_threshold

    def process(self, event: ExceptionEvent) -> GroupingResult:
        vector = self.embedding.embed(event)
        similar = self.storage.find_similar(vector, self.similarity_threshold)

        if similar:
            group_id, confidence = similar[0]
            self.storage.increment_occurrence(group_id, event.timestamp)
            return GroupingResult(
                group_id=group_id,
                confidence=confidence,
                similar_groups=[g for g, _ in similar[1:]],
                is_new_group=False
            )

        group_id = self.storage.store_vector(vector, {
            "first_seen": event.timestamp.isoformat(),
            "type": event.type,
            "example_message": event.message
        })

        return GroupingResult(
            group_id=group_id,
            confidence=1.0,
            is_new_group=True
        )

    def get_top_exceptions(self, limit: int = 10, days: int = 1) -> t.List[dict]:
        return self.storage.get_top_exceptions(limit, timedelta(days=days))
