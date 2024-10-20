from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from datetime import datetime, timedelta
import typing as t
from .base import VectorStorage
from typing import List, Dict, Any

class QdrantVectorStorage(VectorStorage):
    def __init__(self, path: str = None, url: str = None, collection: str = "exceptions", size: int = 384):
        if url:
            self.client = QdrantClient(url=url)
        else:
            self.client = QdrantClient(path=path)
        self.collection = collection
        self.vector_size = size
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        if self.collection not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.COSINE),
            )
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name="last_seen",
                field_schema=models.PayloadSchemaType.DATETIME
            )
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name="count",
                field_schema=models.PayloadSchemaType.INTEGER
            )

    def store_vector(self, vector: t.List[float], metadata: dict) -> str:
        point_id = self.client.count(collection_name=self.collection).count
        self.client.upsert(
            collection_name=self.collection,
            points=[PointStruct(
                id=point_id,
                vector=vector,
                payload={**metadata, "count": 1, "last_seen_timestamp": datetime.now().timestamp()}
            )]
        )
        return str(point_id)

    def find_similar(self, vector: t.List[float], threshold: float, limit: int = 5) -> t.List[tuple[str, float]]:
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=limit,
            score_threshold=threshold
        )
        return [(str(hit.id), hit.score) for hit in results]

    def increment_occurrence(self, group_id: str, timestamp: datetime):
        self.client.set_payload(
            collection_name=self.collection,
            payload={
                "count": self.client.retrieve(
                    collection_name=self.collection,
                    ids=[int(group_id)]
                )[0].payload["count"] + 1,
                "last_seen_timestamp": timestamp.timestamp()
            },
            points=[int(group_id)]
        )

    def get_top_exceptions(self, limit: int, time_range: timedelta) -> List[Dict[str, Any]]:
        current_time = datetime.now()
        start_time = current_time - time_range
        results, offset = self.client.scroll(
            collection_name=self.collection,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="last_seen_timestamp",
                        range=models.Range(
                            gte=start_time.timestamp(),
                            lte=current_time.timestamp()
                        )
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
            with_vectors=False,
            order_by=models.OrderBy(
                key="count",
                direction=models.Direction.DESC
            )
        )

        return [
            {
                "group_id": str(point.id),
                "count": point.payload["count"],
                "metadata": {k: v for k, v in point.payload.items() if k not in ["count", "last_seen_timestamp"]}
            }
            for point in results
        ]

