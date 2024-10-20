from sentence_transformers import SentenceTransformer
from .base import VectorEmbedding
from ..core import ExceptionEvent
import typing as t

class SentenceTransformerEmbedding(VectorEmbedding):
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, exception: ExceptionEvent) -> t.List[float]:
        text = f"{exception.type}: {exception.message}"
        return self.model.encode([text])[0].tolist()

    def get_vector_size(self) -> int:
        return self.model.get_sentence_embedding_dimension()
