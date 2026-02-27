import redis.asyncio as redis
from app.config import settings
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        self.client = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.client.ping()
            logger.info("✓ Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with retry on connection error"""
        if not self.client:
            return None
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except (redis.ConnectionError, ConnectionResetError) as e:
            logger.warning(f"Redis connection error, reconnecting: {e}")
            try:
                await self.connect()  # Reconnect
                value = await self.client.get(key)
                if value:
                    return json.loads(value)
            except Exception as retry_error:
                logger.error(f"Redis retry failed: {retry_error}")
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache with retry on connection error"""
        if not self.client:
            return
        try:
            ttl = ttl or settings.cache_ttl_seconds
            await self.client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
        except (redis.ConnectionError, ConnectionResetError) as e:
            logger.warning(f"Redis connection error, reconnecting: {e}")
            try:
                await self.connect()  # Reconnect
                ttl = ttl or settings.cache_ttl_seconds
                await self.client.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str)
                )
            except Exception as retry_error:
                logger.error(f"Redis retry failed: {retry_error}")
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.client:
            return
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

# Global instance
redis_cache = RedisCache()

async def init_redis():
    """Initialize Redis connection"""
    await redis_cache.connect()

async def close_redis():
    """Close Redis connection"""
    await redis_cache.close()

async def get_cached_company(company_id: str) -> Optional[dict]:
    """Get cached company data"""
    return await redis_cache.get(f"company:{company_id}")

async def cache_company(company_id: str, data: dict):
    """Cache company data"""
    await redis_cache.set(f"company:{company_id}", data)

async def get_progress_updates(session_id: str) -> Optional[dict]:
    """Get progress updates for a session"""
    return await redis_cache.get(f"progress:{session_id}")

async def update_progress(session_id: str, progress_data: dict):
    """Update progress for a session"""
    await redis_cache.set(f"progress:{session_id}", progress_data, ttl=300)  # 5 min TTL

async def delete_progress(session_id: str):
    """Delete progress data"""
    await redis_cache.delete(f"progress:{session_id}")
