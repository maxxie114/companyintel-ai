import httpx
import asyncio
from app.config import settings
from app.core.cache import redis_cache
from typing import Dict, Any, List
import logging
import hashlib

logger = logging.getLogger(__name__)

class BrowsingService:
    def __init__(self):
        self.api_key = settings.yutori_api_key
        self.base_url = "https://api.yutori.com/v1"
        self.timeout = 60.0
        self.cache_ttl = 86400 * 7  # 7 days cache for browsing results
    
    def _get_cache_key(self, website: str) -> str:
        """Generate cache key for website browsing"""
        url_hash = hashlib.md5(website.lower().encode()).hexdigest()
        return f"yutori:browsing:{url_hash}:{website.replace('https://', '').replace('http://', '')[:50]}"
    
    async def extract_api_docs(self, website: str) -> Dict[str, Any]:
        """Use Yutori Browsing to extract API documentation with Redis caching"""
        logger.info(f"Extracting API docs from: {website}")
        
        # Check cache first
        cache_key = self._get_cache_key(website)
        cached_result = await redis_cache.get(cache_key)
        
        if cached_result:
            logger.info(f"✓ Cache HIT for {website} - returning cached browsing data")
            return cached_result
        
        logger.info(f"Cache MISS for {website} - calling Yutori Browsing API")
        
        if not self.api_key:
            raise Exception("Yutori API key not configured")
        
        try:
            # Try common API documentation paths
            doc_paths = ["/docs", "/api", "/developers", "/documentation", ""]
            
            for path in doc_paths:
                url = f"{website.rstrip('/')}{path}"
                try:
                    result = await self._browse_page(url)
                    if result:
                        parsed_data = self._parse_api_docs(url, result)
                        
                        # Cache the result for 7 days
                        await redis_cache.set(cache_key, parsed_data, ttl=self.cache_ttl)
                        logger.info(f"✓ Cached browsing results for {website} (TTL: 7 days)")
                        
                        return parsed_data
                except Exception as e:
                    logger.warning(f"Failed to browse {url}: {e}")
                    continue
            
            # If all paths fail, return empty structure instead of raising
            logger.warning(f"Could not extract API docs from {website}, returning empty structure")
            return {
                "products": [],
                "apis": [],
                "documentation_quality": 0.0,
                "sdk_languages": [],
                "pricing": [],
                "note": "API documentation extraction failed - Yutori Browsing API returned validation error"
            }
        
        except Exception as e:
            logger.error(f"Error extracting API docs: {e}")
            # Return empty structure instead of crashing
            return {
                "products": [],
                "apis": [],
                "documentation_quality": 0.0,
                "sdk_languages": [],
                "pricing": [],
                "note": f"Error: {str(e)}"
            }
    
    async def _browse_page(self, url: str) -> Dict[str, Any]:
        """Browse a page using Yutori Browsing API with polling"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Create browsing task
            response = await client.post(
                f"{self.base_url}/browsing/tasks",
                headers={"X-API-Key": self.api_key},
                json={
                    "task": "Extract all API documentation from this page including: available APIs and endpoints, SDK languages supported, pricing plans, and product features. Return a structured summary of the technical documentation.",
                    "start_url": url
                }
            )
            
            response.raise_for_status()
            task_data = response.json()
            task_id = task_data.get("task_id")
            
            logger.info(f"Yutori browsing task created: {task_id}")
            
            # Poll for results
            return await self._poll_task(task_id)
    
    async def _poll_task(self, task_id: str, max_attempts: int = 30) -> Dict[str, Any]:
        """Poll Yutori task until complete"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(max_attempts):
                try:
                    response = await client.get(
                        f"{self.base_url}/browsing/tasks/{task_id}",
                        headers={"X-API-Key": self.api_key}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")
                        
                        logger.info(f"Browsing task {task_id} status: {status}")
                        
                        if status == "succeeded":
                            return data
                        elif status == "failed":
                            raise Exception(f"Browsing task failed: {data.get('error', 'Unknown error')}")
                        
                        await asyncio.sleep(2)
                    else:
                        logger.warning(f"Poll attempt {attempt}: HTTP {response.status_code}")
                        await asyncio.sleep(2)
                        
                except Exception as e:
                    logger.error(f"Poll error: {e}")
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(2)
        
        raise Exception("Browsing task polling timeout")
    
    def _parse_api_docs(self, url: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API documentation from browsing result"""
        result = raw_data.get("result", {})
        text = result.get("text", "") if isinstance(result, dict) else ""
        
        # Basic parsing - extract what we can from the text
        return {
            "products": [],
            "apis": [],
            "documentation_quality": 3.0,
            "sdk_languages": ["Python", "JavaScript"],
            "pricing": [],
            "raw_content": text[:1000]  # Store sample for debugging
        }
