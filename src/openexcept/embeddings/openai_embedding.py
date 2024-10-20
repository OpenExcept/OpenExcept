import os
from typing import List
import openai
from .base import VectorEmbedding
from ..core import ExceptionEvent

class OpenAIEmbedding(VectorEmbedding):
    def __init__(self, api_key: str = None, model: str = "text-embedding-ada-002"):
        # Use the provided api_key if available, otherwise try to get it from an environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either in the config or as an environment variable OPENAI_API_KEY")
        
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def embed(self, exception: ExceptionEvent) -> List[float]:
        text = f"{exception.type}: {exception.message}"
        response = self.client.embeddings.create(input=[text], model=self.model)
        embedding = response.data[0].embedding
        return embedding

    def get_vector_size(self) -> int:
        return 1536  # Default size for OpenAI's text-embedding-ada-002 model
