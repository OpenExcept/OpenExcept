import os
from pathlib import Path
import yaml
from typing import List, Dict, Optional
from datetime import datetime
from .core import ExceptionGrouper, ExceptionEvent
from .storage.qdrant import QdrantVectorStorage
# Do not remove these imports as they are used by the embedding classes
from .embeddings.sentence_transformers import SentenceTransformerEmbedding
from .embeddings.openai_embedding import OpenAIEmbedding
import requests

class OpenExcept:
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        
        if 'local_path' in self.config['storage'] or 'local_url' in self.config['storage']:
            self._setup_local()
        else:
            self._setup_cloud()
    
    def _load_config(self, config_path: str = None):
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), 'configs', 'config.yaml')
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _setup_cloud(self):
        self.url = self.config['storage']['url']
        self.headers = {"Content-Type": "application/json"}
        if 'api_key' in self.config['storage']:
            self.headers["Authorization"] = f"Bearer {self.config['storage']['api_key']}"

    def _setup_local(self):
        embedding_config = self.config['embedding']
        embedding_class = globals()[embedding_config['class']]
        embedding = embedding_class(**embedding_config.get('kwargs', {}))
        
        # Determine the embedding vector size automatically
        embedding_vector_size = embedding.get_vector_size()
        
        storage_config = self.config['storage']
        if 'local_url' in storage_config:
            storage = QdrantVectorStorage(
                url=storage_config['local_url'],
                size=embedding_vector_size
            )
        else:
            storage_path = os.path.expanduser(storage_config['local_path'])
            Path(storage_path).mkdir(parents=True, exist_ok=True)
            storage = QdrantVectorStorage(
                path=storage_path,
                size=embedding_vector_size
            )
        
        self.grouper = ExceptionGrouper(
            storage=storage,
            embedding=embedding,
            similarity_threshold=embedding_config['similarity_threshold']
        )

    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        url = f"{self.url}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def group_exception(self, message: str, type_name: str = None, **context) -> str:
        if hasattr(self, 'grouper'):
            event = ExceptionEvent(
                message=message,
                type=type_name or "Unknown",
                context=context
            )
            result = self.grouper.process(event)
            return result.group_id
        else:
            data = {
                "message": message,
                "type": type_name or "Unknown",
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "similarity_threshold": self.config['embedding']['similarity_threshold']
            }
            result = self._make_request("process", method="POST", data=data)
            return result["group_id"]

    def get_top_exceptions(self, limit: int = 10, days: int = 1) -> List[Dict]:
        if hasattr(self, 'grouper'):
            return self.grouper.get_top_exceptions(limit, days)
        else:
            return self._make_request("top_exceptions", data={"limit": limit, "days": days})

    @classmethod
    def setup_exception_hook(cls, **kwargs):
        import sys
        import traceback
        
        grouper = cls(**kwargs)
        
        def exception_hook(exc_type, exc_value, exc_traceback):
            group_id = grouper.group_exception(
                message=str(exc_value),
                type_name=exc_type.__name__,
                stack_trace="".join(traceback.format_tb(exc_traceback))
            )
            print(f"Exception in group {group_id}: {exc_value}")
        
        sys.excepthook = exception_hook
