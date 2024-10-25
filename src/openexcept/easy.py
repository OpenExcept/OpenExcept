import os
from pathlib import Path
import yaml
from typing import List, Dict, Optional, Any
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
            config_path = os.path.join(os.path.dirname(__file__), 'configs', 'config_local_fs.yaml')
        
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

    def group_exception(self, message: str, type_name: str = "Unknown", timestamp: datetime = datetime.now()) -> str:
        # TODO fix this
        if hasattr(self, 'grouper'):
            event = ExceptionEvent(
                message=message,
                type=type_name,
                timestamp=timestamp,
            )
            result = self.grouper.process(event)
            return result.group_id
        else:
            data = {
                "message": message,
                "type": type_name,
                "timestamp": timestamp,
                "similarity_threshold": self.config['embedding']['similarity_threshold']
            }
            result = self._make_request("process", method="POST", data=data)
            return result["group_id"]

    def get_top_exception_groups(self, limit: int, start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]:
        if hasattr(self, 'grouper'):
            return self.grouper.get_top_exception_groups(limit, start_time, end_time)
        else:
            data = {
                "limit": limit,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None
            }
            return self._make_request("top_exceptions", method="POST", data=data)

    def get_exception_events(self, group_id: str, start_time: datetime = None, end_time: datetime = None) -> List[ExceptionEvent]:
        if hasattr(self, 'grouper'):
            return self.grouper.get_exception_events(group_id, start_time, end_time)
        else:
            # Placeholder for cloud implementation
            data = {
                "group_id": group_id,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None
            }
            result = self._make_request("get_exception_events", method="POST", data=data)
            # Convert response to ExceptionEvent objects
            return [ExceptionEvent(
                id=evt['id'],
                message=evt['message'],
                type=evt['type'],
                timestamp=datetime.fromisoformat(evt['timestamp']),
                stack_trace=evt.get('stack_trace', ''),
                context=evt.get('context', {})
            ) for evt in result.get("events", [])]

    @staticmethod
    def setup_exception_hook(config_path: Optional[str] = None) -> 'OpenExcept':
        import sys
        import traceback
        
        grouper = OpenExcept(config_path=config_path)
        
        def exception_hook(exc_type, exc_value, exc_traceback):
            group_id = grouper.group_exception(
                message=str(exc_value),
                type_name=exc_type.__name__,
                stack_trace="".join(traceback.format_tb(exc_traceback))
            )
            print(f"Exception in group {group_id}: {exc_value}")
        
        sys.excepthook = exception_hook

        return grouper
