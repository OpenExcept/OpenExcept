from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from datetime import datetime, timedelta
import typing as t
from .base import VectorStorage
from ..core import ExceptionEvent
from typing import List, Dict, Any
import uuid

class QdrantVectorStorage(VectorStorage):
    def __init__(self, path: str = None, url: str = None, group_collection: str = "exception_groups", event_collection: str = "exception_events", size: int = 384):
        if url:
            self.client = QdrantClient(url=url)
        else:
            self.client = QdrantClient(path=path)
        self.group_collection = group_collection
        self.event_collection = event_collection
        self.vector_size = size
        self._ensure_collections()

    def _ensure_collections(self):
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.group_collection not in collection_names:
            self.client.create_collection(
                collection_name=self.group_collection,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.COSINE),
            )
            self.client.create_payload_index(
                collection_name=self.group_collection,
                field_name="last_seen_timestamp",
                field_schema=models.PayloadSchemaType.FLOAT
            )

        if self.event_collection not in collection_names:
            self.client.create_collection(
                collection_name=self.event_collection,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.DOT),  # Dummy vector config
            )
            self.client.create_payload_index(
                collection_name=self.event_collection,
                field_name="group_id",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            self.client.create_payload_index(
                collection_name=self.event_collection,
                field_name="timestamp",
                field_schema=models.PayloadSchemaType.FLOAT
            )

    def store_vector(self, vector: t.List[float], metadata: dict) -> str:
        group_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=self.group_collection,
            points=[PointStruct(
                id=group_id,
                vector=vector,
                payload={**metadata, "last_seen_timestamp": datetime.now().timestamp()}
            )]
        )
        return group_id

    def find_similar(self, vector: t.List[float], threshold: float, limit: int = 5) -> t.List[tuple[str, float]]:
        results = self.client.search(
            collection_name=self.group_collection,
            query_vector=vector,
            limit=limit,
            score_threshold=threshold
        )
        return [(str(hit.id), hit.score) for hit in results]

    def store_exception_event(self, group_id: str, event: ExceptionEvent, vector: t.List[float]):
        event_id = event.id
        self.client.upsert(
            collection_name=self.event_collection,
            points=[PointStruct(
                id=event_id,
                vector=vector,
                payload={
                    "group_id": group_id,
                    "message": event.message,
                    "type": event.type,
                    "timestamp": event.timestamp.timestamp(),
                    "stack_trace": event.stack_trace,
                    "context": event.context
                }
            )]
        )

    def get_exception_events(self, group_id: str, start_time: datetime = None, end_time: datetime = None) -> List[ExceptionEvent]:
        must_conditions = [
            models.FieldCondition(
                key="group_id",
                match=models.MatchValue(value=group_id)
            )
        ]

        if start_time or end_time:
            timestamp_range = {}
            if start_time:
                timestamp_range["gte"] = start_time.timestamp()
            if end_time:
                timestamp_range["lte"] = end_time.timestamp()
            must_conditions.append(
                models.FieldCondition(
                    key="timestamp",
                    range=models.Range(**timestamp_range)
                )
            )

        query_filter = models.Filter(must=must_conditions)

        events = []
        offset = None

        while True:
            scroll_results, offset = self.client.scroll(
                collection_name=self.event_collection,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
                scroll_filter=query_filter
            )
            for point in scroll_results:
                payload = point.payload
                event = ExceptionEvent(
                    id=str(point.id),
                    message=payload.get("message", ""),
                    type=payload.get("type", ""),
                    timestamp=datetime.fromtimestamp(payload.get("timestamp", datetime.now().timestamp())),
                    stack_trace=payload.get("stack_trace", ""),
                    context=payload.get("context", {})
                )
                events.append(event)
            if offset is None:
                break

        return events

    def get_top_exception_groups(self, limit: int, start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]:
        # Build the time range condition if start_time or end_time are specified
        must_conditions = []
        if start_time or end_time:
            timestamp_range = {}
            if start_time:
                timestamp_range["gte"] = start_time.timestamp()
            if end_time:
                timestamp_range["lte"] = end_time.timestamp()
            must_conditions.append(
                models.FieldCondition(
                    key="timestamp",
                    range=models.Range(**timestamp_range)
                )
            )

        # Create the query filter
        query_filter = models.Filter(must=must_conditions) if must_conditions else None

        # Initialize variables to keep track of group counts and metadata
        group_counts = {}
        group_metadata = {}

        # Initialize offset for scrolling
        offset = None

        # Scroll through all exception events matching the filter
        while True:
            scroll_results, offset = self.client.scroll(
                collection_name=self.event_collection,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
                scroll_filter=query_filter
            )
            for point in scroll_results:
                payload = point.payload
                group_id = payload.get("group_id")
                if group_id:
                    # Increment the count for this group_id
                    group_counts[group_id] = group_counts.get(group_id, 0) + 1
                    # Store the first occurrence's metadata if not already stored
                    if group_id not in group_metadata:
                        group_metadata[group_id] = {
                            "example_message": payload.get("message", ""),
                            "example_type": payload.get("type", "")
                        }
            # Exit the loop if there are no more results
            if offset is None:
                break

        # Sort the groups by occurrence count in descending order
        sorted_groups = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)

        # Prepare the top exception groups list with required metadata
        top_exception_groups = []
        for group_id, count in sorted_groups[:limit]:
            metadata = group_metadata.get(group_id, {})
            top_exception_groups.append({
                "group_id": group_id,
                "count": count,
                "metadata": metadata
            })

        return top_exception_groups
