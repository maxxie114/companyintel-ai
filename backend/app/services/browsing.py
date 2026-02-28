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
        self.tavily_key = settings.tavily_api_key
        self.base_url = "https://api.yutori.com/v1"
        self.timeout = 60.0
        self.cache_ttl = 86400 * 7  # 7 days cache for browsing results

    def _get_cache_key(self, website: str) -> str:
        url_hash = hashlib.md5(website.lower().encode()).hexdigest()
        return f"yutori:browsing:{url_hash}:{website.replace('https://', '').replace('http://', '')[:50]}"

    async def _find_docs_url_with_tavily(self, company_name: str, website: str) -> str:
        """Ask Tavily for the real developer/API docs URL rather than guessing paths."""
        if not self.tavily_key:
            return website
        domain = website.replace("https://", "").replace("http://", "").rstrip("/")
        base = domain.split(".")[-2] if "." in domain else domain
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_key,
                        "query": f"{company_name} developer API documentation official docs",
                        "search_depth": "basic",
                        "max_results": 5,
                        "include_answer": False,
                    }
                )
                r.raise_for_status()
                results = r.json().get("results", [])

            dev_keywords = ["developer", "developers", "docs", "documentation", "api", "platform", "dev"]
            # Prefer a URL that matches the company domain AND looks like a dev portal
            for res in results:
                url = res.get("url", "").lower()
                if base in url and any(k in url for k in dev_keywords):
                    found = res["url"].rstrip("/")
                    logger.info(f"✓ Tavily found docs URL for {company_name}: {found}")
                    return found
            # Fallback: any result that matches company domain
            for res in results:
                if base in res.get("url", "").lower():
                    found = res["url"].rstrip("/")
                    logger.info(f"Tavily fallback docs URL for {company_name}: {found}")
                    return found
        except Exception as e:
            logger.warning(f"Tavily docs search failed for {company_name}: {e}")
        return website

    async def extract_api_docs(self, website: str, company_name: str = "") -> Dict[str, Any]:
        """Find real docs URL via Tavily, then use Yutori Browsing to extract content."""
        logger.info(f"Extracting API docs for {company_name or website}")

        cache_key = self._get_cache_key(website)
        cached_result = await redis_cache.get(cache_key)

        if cached_result:
            if cached_result.get("raw_content") and not cached_result.get("products") and not cached_result.get("apis"):
                logger.info(f"Cache HIT for {website} but stale — re-parsing with OpenAI")
                reparsed = await self._parse_api_docs(website, {"result": cached_result["raw_content"]})
                await redis_cache.set(cache_key, reparsed, ttl=self.cache_ttl)
                return reparsed
            logger.info(f"✓ Cache HIT for {website}")
            return cached_result

        if not self.api_key:
            raise Exception("Yutori API key not configured")

        try:
            # Step 1: Tavily finds the correct docs URL (no blind path guessing)
            docs_url = await self._find_docs_url_with_tavily(company_name or website, website)
            logger.info(f"Sending Yutori to: {docs_url}")

            # Step 2: One targeted Yutori browse
            try:
                result = await self._browse_page(docs_url)
                if result:
                    parsed_data = await self._parse_api_docs(docs_url, result)
                    await redis_cache.set(cache_key, parsed_data, ttl=self.cache_ttl)
                    logger.info(f"✓ Cached browsing results for {website} (TTL: 7 days)")
                    return parsed_data
            except Exception as e:
                logger.warning(f"Yutori browse failed for {docs_url}: {e}")

            return {
                "products": [], "apis": [], "documentation_quality": 0.0,
                "sdk_languages": [], "pricing": [],
                "note": "API documentation extraction failed"
            }

        except Exception as e:
            logger.error(f"Error extracting API docs: {e}")
            return {
                "products": [], "apis": [], "documentation_quality": 0.0,
                "sdk_languages": [], "pricing": [],
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
    
    def _normalize_apis(self, apis: list) -> list:
        """Convert OpenAI api groups (name + endpoints[]) to APIEndpoint format (path/method/category)."""
        result = []
        for api in apis:
            name = api.get("name", "API")
            desc = api.get("description", "")
            auth = api.get("auth_required", True)
            endpoints = api.get("endpoints", [])
            if endpoints:
                for ep in endpoints:
                    # ep is like "GET /services" or just "/services"
                    parts = str(ep).split(None, 1)
                    if len(parts) == 2 and parts[0].isupper():
                        method, path = parts[0], parts[1]
                    else:
                        method, path = "GET", str(ep)
                    result.append({
                        "path": path,
                        "method": method,
                        "description": desc,
                        "category": name,
                        "authentication_required": auth,
                    })
            else:
                result.append({
                    "path": f"/{name.lower().replace(' ', '-')}",
                    "method": "GET",
                    "description": desc,
                    "category": name,
                    "authentication_required": auth,
                })
        return result

    def _normalize_pricing(self, pricing: list) -> list:
        """Ensure pricing items match PricingTier (name, price, features, target_audience)."""
        result = []
        for tier in pricing:
            result.append({
                "name": tier.get("name") or tier.get("tier") or "Plan",
                "price": tier.get("price", "Contact us"),
                "features": tier.get("features", []),
                "target_audience": tier.get("target_audience", ""),
            })
        return result

    def _normalize_products(self, products: list) -> list:
        """Ensure product items match Product (name, description, category)."""
        result = []
        for p in products:
            result.append({
                "name": p.get("name", "Product"),
                "description": p.get("description", ""),
                "category": p.get("category", "Product"),
                "launch_date": p.get("launch_date"),
            })
        return result

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
                # Normalize to match Pydantic models
                parsed["apis"] = self._normalize_apis(parsed.get("apis", []))
                parsed["pricing"] = self._normalize_pricing(parsed.get("pricing", []))
                parsed["products"] = self._normalize_products(parsed.get("products", []))
                logger.info(f"✓ OpenAI extracted API docs: {len(parsed.get('products', []))} products, {len(parsed.get('apis', []))} API endpoints, langs={parsed.get('sdk_languages', [])}")
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
