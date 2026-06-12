"""
Redis Client Configuration
"""
import redis
import os
import logging
import json
from typing import Any, Optional

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client wrapper with connection pooling"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.ttl = int(os.getenv("REDIS_CACHE_TTL", "3600"))
        self.client = None
        self.connect()
    
    def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            self.client.ping()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair"""
        try:
            ttl = ttl or self.ttl
            if isinstance(value, dict):
                value = json.dumps(value)
            self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        try:
            value = self.client.get(key)
            if value and value.startswith('{'):
                return json.loads(value)
            return value
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False
    
    def ping(self) -> bool:
        """Ping Redis"""
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False
    
    def close(self):
        """Close connection"""
        if self.client:
            self.client.close()
            logger.info("✅ Redis connection closed")

# Global Redis instance
redis_client = RedisClient()