import httpx
import asyncio
import json
from app.config import settings
from app.core.cache import redis_cache
from typing import Dict, Any, List
import logging
import hashlib

logger = logging.getLogger(__name__)

class BrowsingService:
    def __init__(self):
        self.api_key = settings.yutori_api_key
        self.openai_key = settings.openai_api_key
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
            # Re-parse stale cache entries that have raw_content but empty structured fields
            if cached_result.get("raw_content") and not cached_result.get("products") and not cached_result.get("apis"):
                logger.info(f"Cache HIT for {website} but stale (no products/apis) — re-parsing with OpenAI")
                reparsed = await self._parse_api_docs(website, {"result": cached_result["raw_content"]})
                await redis_cache.set(cache_key, reparsed, ttl=self.cache_ttl)
                return reparsed
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
                        parsed_data = await self._parse_api_docs(url, result)
                        
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
    
    async def _poll_task(self, task_id: str, max_attempts: int = 90, poll_interval: int = 10) -> Dict[str, Any]:
        """Poll Yutori task until complete. Browsing tasks take 5-10 min so poll every 10s."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(max_attempts):
                await asyncio.sleep(poll_interval)
                try:
                    response = await client.get(
                        f"{self.base_url}/browsing/tasks/{task_id}",
                        headers={"X-API-Key": self.api_key}
                    )

                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")

                        if attempt % 6 == 0:  # log every minute
                            logger.info(f"Browsing task {task_id} status: {status} ({attempt * poll_interval}s elapsed)")

                        if status == "succeeded":
                            logger.info(f"✅ Browsing task {task_id} completed after {attempt * poll_interval}s")
                            return data
                        elif status == "failed":
                            raise Exception(f"Browsing task failed: {data.get('error', 'Unknown error')}")

                    else:
                        logger.warning(f"Poll attempt {attempt}: HTTP {response.status_code}")

                except Exception as e:
                    logger.error(f"Poll error: {e}")
                    if attempt == max_attempts - 1:
                        raise

        raise Exception("Browsing task polling timeout")
    
    async def _parse_api_docs(self, url: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API documentation from browsing result using OpenAI for structured extraction."""
        result = raw_data.get("result", "")
        # Yutori returns result as a plain string or occasionally a dict
        if isinstance(result, dict):
            text = result.get("content") or result.get("text") or str(result)
        else:
            text = str(result) if result else ""

        raw_content = text[:3000]

        if not raw_content.strip() or not self.openai_key:
            return {
                "products": [],
                "apis": [],
                "documentation_quality": 2.0,
                "sdk_languages": [],
                "pricing": [],
                "raw_content": raw_content,
            }

        prompt = f"""Based on this API documentation content from {url}:

{raw_content}

Extract structured information and return ONLY a JSON object with this exact schema:
{{
  "products": [
    {{"name": "Product Name", "description": "What it does", "category": "API/SDK/Tool"}}
  ],
  "apis": [
    {{"name": "API Name", "description": "What it does", "endpoints": ["GET /endpoint"], "auth_required": true}}
  ],
  "sdk_languages": ["Python", "JavaScript", "Go"],
  "pricing": [
    {{"tier": "Free", "price": "$0/month", "features": ["feature 1", "feature 2"]}}
  ],
  "documentation_quality": 4.5
}}

Rules:
- products: list of major product offerings (APIs, SDKs, tools)
- apis: list of API categories/groups with example endpoints if visible
- sdk_languages: programming languages with official client libraries
- pricing: pricing tiers if visible on the page
- documentation_quality: float 1-5 rating based on how comprehensive the docs appear
- Return ONLY the JSON object, no explanation"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You extract structured API documentation data from raw text. Return only valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 1200
                    }
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]

                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                parsed = json.loads(content)
                parsed["raw_content"] = raw_content
                logger.info(f"✓ OpenAI extracted API docs: {len(parsed.get('products', []))} products, {len(parsed.get('apis', []))} APIs, langs={parsed.get('sdk_languages', [])}")
                return parsed

        except Exception as e:
            logger.warning(f"OpenAI API docs extraction failed: {e}")
            return {
                "products": [],
                "apis": [],
                "documentation_quality": 2.5,
                "sdk_languages": [],
                "pricing": [],
                "raw_content": raw_content,
            }
