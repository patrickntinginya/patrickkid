"""
Elasticsearch Configuration
"""
from elasticsearch import Elasticsearch
import os
import logging

logger = logging.getLogger(__name__)

class ElasticsearchClient:
    """Elasticsearch client wrapper"""
    
    def __init__(self):
        self.host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.index_prefix = os.getenv("ELASTICSEARCH_INDEX_PREFIX", "shambani")
        self.client = None
        self.connect()
    
    def connect(self):
        """Connect to Elasticsearch"""
        try:
            self.client = Elasticsearch(
                [f"http://{self.host}:{self.port}"],
                request_timeout=30
            )
            if self.client.info():
                logger.info("✅ Connected to Elasticsearch")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Elasticsearch: {e}")
            raise
    
    def index_document(self, index: str, doc_id: str, body: dict) -> bool:
        """Index a document"""
        try:
            full_index = f"{self.index_prefix}-{index}"
            self.client.index(index=full_index, id=doc_id, body=body)
            return True
        except Exception as e:
            logger.error(f"Elasticsearch index error: {e}")
            return False
    
    def search(self, index: str, query: dict, size: int = 10) -> list:
        """Search documents"""
        try:
            full_index = f"{self.index_prefix}-{index}"
            response = self.client.search(index=full_index, body=query, size=size)
            hits = response.get("hits", {}).get("hits", [])
            return [hit["_source"] for hit in hits]
        except Exception as e:
            logger.error(f"Elasticsearch search error: {e}")
            return []
    
    def close(self):
        """Close connection"""
        if self.client:
            self.client.close()
            logger.info("✅ Elasticsearch connection closed")

# Global Elasticsearch instance
es_client = ElasticsearchClient()