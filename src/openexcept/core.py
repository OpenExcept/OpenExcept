from datetime import datetime, timedelta
import typing as t
from abc import ABC, abstractmethod
import uuid
from .storage.base import VectorStorage  # Import VectorStorage from base.py

class ExceptionEvent:
    def __init__(self, message: str, type: str, timestamp: datetime = None, stack_trace: str = "", context: dict = None, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.message = message
        self.type = type
        self.timestamp = timestamp or datetime.now() # in datetime object
        self.stack_trace = stack_trace
        self.context = context or {}

class GroupingResult:
    def __init__(self, group_id: str, confidence: float, similar_groups: t.List[str] = None, is_new_group: bool = False):
        self.group_id = group_id
        self.confidence = confidence
        self.similar_groups = similar_groups or []
        self.is_new_group = is_new_group

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
            is_new_group = False
        else:
            group_id = self.storage.store_vector(vector, {
                "first_seen": event.timestamp.isoformat(),
                "example_type": event.type,
                "example_message": event.message
            })
            confidence = 1.0
            is_new_group = True

        # Store the exception event with the group ID
        self.storage.store_exception_event(group_id, event, vector)

        return GroupingResult(
            group_id=group_id,
            confidence=confidence,
            similar_groups=[g for g, _ in similar[1:]] if similar else [],
            is_new_group=is_new_group
        )

    def get_exception_events(self, group_id: str, start_time: datetime = None, end_time: datetime = None) -> t.List[ExceptionEvent]:
        return self.storage.get_exception_events(group_id, start_time, end_time)
    
    def get_top_exception_groups(self, limit: int = 10, start_time: datetime = None, end_time: datetime = None) -> t.List[dict]:
        return self.storage.get_top_exception_groups(limit, start_time, end_time)
