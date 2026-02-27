import httpx
import asyncio
import json
from app.config import settings
from app.models import CompanyOverview
from app.core.cache import redis_cache
import logging
from typing import Dict, Any, Optional
import hashlib

logger = logging.getLogger(__name__)

class ResearchService:
    def __init__(self):
        self.api_key = settings.yutori_api_key
        self.base_url = "https://api.yutori.com/v1"
        self.timeout = 30.0  # Short timeout for quick checks
        self.cache_ttl = 86400 * 7  # 7 days cache for research results
    
    def _get_cache_key(self, company_name: str) -> str:
        """Generate cache key for company research"""
        name_hash = hashlib.md5(company_name.lower().encode()).hexdigest()
        return f"yutori:research:{name_hash}:{company_name.lower().replace(' ', '_')}"
    
    def _get_task_key(self, company_name: str) -> str:
        """Generate key for storing task ID"""
        name_hash = hashlib.md5(company_name.lower().encode()).hexdigest()
        return f"yutori:task:{name_hash}:{company_name.lower().replace(' ', '_')}"
    
    async def get_quick_overview(self, company_name: str) -> Dict[str, Any]:
        """
        Fast company overview:
        1. Check cache - may already have Yutori-quality data from a previous background run
        2. Use Tavily for instant results (~2s) so the user never waits
        3. Start Yutori deep research in background to enrich cache for next time
        """
        logger.info(f"Getting quick overview for: {company_name}")

        # Step 1: Check cache (could be Yutori-enriched from a previous background run)
        cache_key = self._get_cache_key(company_name)
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            logger.info(f"✓ Cache HIT for {company_name} - returning cached research")
            return cached_result

        # Step 2: Tavily instant search for immediate results
        logger.info(f"Cache MISS - using Tavily for quick overview of {company_name}")
        overview_data = await self._quick_tavily_search(company_name)

        # Step 3: Start Yutori deep research in background if not already running
        if self.api_key:
            task_key = self._get_task_key(company_name)
            existing_task_id = await redis_cache.get(task_key)
            if not existing_task_id:
                try:
                    task_id = await self._create_task(company_name)
                    await redis_cache.set(task_key, task_id, ttl=3600)
                    asyncio.create_task(
                        self._background_poll_and_cache(task_id, company_name, cache_key, task_key)
                    )
                    logger.info(f"✓ Yutori deep research started in background for {company_name}")
                except Exception as e:
                    logger.warning(f"Could not start Yutori background research: {e}")
            else:
                logger.info(f"Yutori research already running for {company_name} (task: {existing_task_id})")

        return overview_data

    async def _quick_tavily_search(self, company_name: str) -> Dict[str, Any]:
        """Use Tavily to get an instant company overview"""
        tavily_key = settings.tavily_api_key
        if not tavily_key:
            return self._empty_overview(company_name)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": tavily_key,
                        "query": f"{company_name} company overview founded headquarters employees industry website",
                        "search_depth": "advanced",
                        "max_results": 5,
                        "include_answer": True,
                    }
                )
                response.raise_for_status()
                data = response.json()

            answer = data.get("answer", "")
            results = data.get("results", [])
            slug = company_name.lower().replace(" ", "-")

            # Try to find the company's official website from results
            website = ""
            for r in results:
                url = r.get("url", "")
                try:
                    domain = url.split("/")[2]
                except IndexError:
                    continue
                if company_name.lower().replace(" ", "") in domain.lower().replace("-", "").replace(".", ""):
                    website = f"https://{domain}"
                    break
            if not website:
                website = f"https://{slug}.com"

            domain = website.replace("https://", "").replace("http://", "").split("/")[0]

            logger.info(f"✓ Tavily quick overview complete for {company_name}")
            return {
                "name": company_name,
                "slug": slug,
                "description": answer[:500] if answer else f"{company_name} company information",
                "founded_year": None,
                "headquarters": "",
                "employee_count": "",
                "website": website,
                "logo_url": f"https://logo.clearbit.com/{domain}",
                "industry": ["Technology"],
                "mission": "",
                "status": "private",
            }

        except Exception as e:
            logger.error(f"Tavily quick search failed for {company_name}: {e}")
            return self._empty_overview(company_name)

    def _empty_overview(self, company_name: str) -> Dict[str, Any]:
        """Minimal fallback when all lookups fail"""
        slug = company_name.lower().replace(" ", "-")
        return {
            "name": company_name,
            "slug": slug,
            "description": f"{company_name} - analysis in progress",
            "founded_year": None,
            "headquarters": "",
            "employee_count": "",
            "website": f"https://{slug}.com",
            "logo_url": f"https://logo.clearbit.com/{slug}.com",
            "industry": ["Technology"],
            "mission": "",
            "status": "private",
        }
    
    async def _create_task(self, company_name: str) -> str:
        """Create a new Yutori research task"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/research/tasks",
                headers={"X-API-Key": self.api_key},
                json={
                    "query": f"Comprehensive overview of {company_name}: "
                             f"description, founding year, headquarters, "
                             f"employee count, mission, industry, website, status (public/private)"
                }
            )
            
            response.raise_for_status()
            task_data = response.json()
            task_id = task_data.get("task_id")
            
            logger.info(f"Yutori task created: {task_id}")
            return task_id
    
    async def _check_task_once(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Check task status once (non-blocking)"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/research/tasks/{task_id}",
                    headers={"X-API-Key": self.api_key}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    
                    logger.info(f"Task {task_id} status: {status}")
                    
                    if status == "succeeded":
                        return data
                    elif status == "failed":
                        error_msg = data.get('error', data.get('message', 'Unknown error'))
                        raise Exception(f"Task failed: {error_msg}")
                    else:
                        # Still running/queued
                        return None
        except Exception as e:
            logger.error(f"Error checking task: {e}")
            return None
    
    async def _background_poll_and_cache(
        self, 
        task_id: str, 
        company_name: str, 
        cache_key: str, 
        task_key: str
    ):
        """
        Poll task in background until complete, then cache result.
        This runs independently and doesn't block the main request.
        """
        try:
            logger.info(f"🔄 Background polling started for {company_name} (task: {task_id})")
            
            max_attempts = 300  # 10 minutes (300 * 2 seconds)
            
            async with httpx.AsyncClient(timeout=600.0) as client:
                for attempt in range(max_attempts):
                    try:
                        response = await client.get(
                            f"{self.base_url}/research/tasks/{task_id}",
                            headers={"X-API-Key": self.api_key}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            status = data.get("status")
                            
                            if attempt % 30 == 0:  # Log every minute
                                logger.info(f"Background poll: {company_name} - {status} ({attempt}/{max_attempts})")
                            
                            if status == "succeeded":
                                # Parse and cache
                                parsed_data = await self._parse_overview(company_name, data)
                                await redis_cache.set(cache_key, parsed_data, ttl=self.cache_ttl)
                                await redis_cache.delete(task_key)
                                
                                logger.info(f"✅ Background poll complete: {company_name} cached successfully!")
                                return
                            
                            elif status == "failed":
                                error_msg = data.get('error', 'Unknown error')
                                logger.error(f"❌ Background poll failed: {company_name} - {error_msg}")
                                await redis_cache.delete(task_key)
                                return
                        
                        # Still running, wait 2 seconds
                        await asyncio.sleep(2)
                    
                    except Exception as e:
                        logger.error(f"Background poll error (attempt {attempt}): {e}")
                        await asyncio.sleep(2)
                
                # Timeout
                logger.warning(f"⏱️ Background poll timeout for {company_name} after 10 minutes")
                await redis_cache.delete(task_key)
        
        except Exception as e:
            logger.error(f"Background polling crashed for {company_name}: {e}")
            await redis_cache.delete(task_key)
    
    async def _parse_overview(self, company_name: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pass Yutori raw content to OpenAI for structured JSON extraction."""
        result = raw_data.get("result", "")
        content = result.get("content", "") if isinstance(result, dict) else str(result)

        slug = company_name.lower().replace(" ", "-")
        fallback = {
            "name": company_name,
            "slug": slug,
            "description": content[:400] if content else f"{company_name} company",
            "founded_year": None,
            "headquarters": "",
            "employee_count": "",
            "website": f"https://{slug}.com",
            "logo_url": f"https://logo.clearbit.com/{slug}.com",
            "industry": ["Technology"],
            "mission": "",
            "status": "private",
        }

        if not content or not settings.openai_api_key:
            return fallback

        prompt = f"""Extract structured company information from this research content about {company_name}.

Content:
{content[:3000]}

Return a JSON object with EXACTLY these fields:
{{
  "name": "{company_name}",
  "slug": "{slug}",
  "description": "2-3 sentence company description",
  "founded_year": 2010,
  "headquarters": "City, State/Country",
  "employee_count": "1,000+",
  "website": "https://example.com",
  "logo_url": "https://logo.clearbit.com/example.com",
  "industry": ["Primary Industry", "Sub-industry"],
  "mission": "Company mission statement",
  "status": "private or public"
}}

Rules:
- founded_year must be an integer or null
- status must be exactly "public" or "private"
- website must be a valid https URL
- Return ONLY the JSON object, no explanation"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You extract structured company data from research text. Return only valid JSON objects."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 600
                    }
                )
                response.raise_for_status()
                text = response.json()["choices"][0]["message"]["content"]

                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()

                parsed = json.loads(text)
                # Ensure required fields are present, fill from fallback if missing
                for key, val in fallback.items():
                    if key not in parsed or parsed[key] is None:
                        parsed[key] = val
                logger.info(f"✓ OpenAI parsed overview for {company_name}: founded={parsed.get('founded_year')} hq={parsed.get('headquarters')}")
                return parsed

        except Exception as e:
            logger.warning(f"OpenAI overview parsing failed for {company_name}: {e}")
            return fallback
