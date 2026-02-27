import httpx
import asyncio
from app.config import settings
from app.models import CompanyOverview
from app.core.cache import redis_cache
import logging
from typing import Dict, Any
import hashlib

logger = logging.getLogger(__name__)

class ResearchService:
    def __init__(self):
        self.api_key = settings.yutori_api_key
        self.base_url = "https://api.yutori.com/v1"
        self.timeout = 300.0  # 5 minutes for long-running research tasks
        self.cache_ttl = 86400 * 7  # 7 days cache for research results
    
    def _get_cache_key(self, company_name: str) -> str:
        """Generate cache key for company research"""
        # Use hash to handle special characters and normalize
        name_hash = hashlib.md5(company_name.lower().encode()).hexdigest()
        return f"yutori:research:{name_hash}:{company_name.lower().replace(' ', '_')}"
    
    async def get_company_overview(self, company_name: str) -> Dict[str, Any]:
        """Use Yutori Research API to get company overview with Redis caching"""
        logger.info(f"Researching company: {company_name}")
        
        # Check cache first
        cache_key = self._get_cache_key(company_name)
        cached_result = await redis_cache.get(cache_key)
        
        if cached_result:
            logger.info(f"✓ Cache HIT for {company_name} - returning cached research")
            return cached_result
        
        logger.info(f"Cache MISS for {company_name} - calling Yutori API (this will take 5-10 minutes)")
        
        if not self.api_key:
            raise Exception("Yutori API key not configured")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Create research task
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
                
                # Poll for results
                result = await self._poll_task(task_id)
                parsed_data = self._parse_overview(company_name, result)
                
                # Cache the result for 7 days
                await redis_cache.set(cache_key, parsed_data, ttl=self.cache_ttl)
                logger.info(f"✓ Cached research results for {company_name} (TTL: 7 days)")
                
                return parsed_data
        
        except Exception as e:
            logger.error(f"Error researching {company_name}: {e}")
            raise
    
    async def _poll_task(self, task_id: str, max_attempts: int = 150) -> Dict[str, Any]:
        """Poll Yutori task until complete (max 5 minutes)"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(max_attempts):
                try:
                    response = await client.get(
                        f"{self.base_url}/research/tasks/{task_id}",
                        headers={"X-API-Key": self.api_key}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")
                        
                        if attempt % 10 == 0:  # Log every 10th attempt
                            logger.info(f"Task {task_id} status: {status} (attempt {attempt}/{max_attempts})")
                        
                        if status == "succeeded":
                            logger.info(f"Task {task_id} completed successfully!")
                            logger.debug(f"Result data: {data}")
                            return data
                        elif status == "failed":
                            error_msg = data.get('error', data.get('message', 'Unknown error'))
                            raise Exception(f"Task failed: {error_msg}")
                        
                        # Still running, wait and retry
                        await asyncio.sleep(2)
                    else:
                        logger.warning(f"Poll attempt {attempt}: HTTP {response.status_code}")
                        await asyncio.sleep(2)
                        
                except Exception as e:
                    logger.error(f"Poll error: {e}")
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(2)
        
        raise Exception(f"Task polling timeout after {max_attempts * 2} seconds")
    
    def _parse_overview(self, company_name: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw research data into CompanyOverview format"""
        # Extract data from Yutori response
        result = raw_data.get("result", {})
        content = result.get("content", "") if isinstance(result, dict) else str(raw_data.get("content", ""))
        
        # Parse the content to extract structured information
        slug = company_name.lower().replace(" ", "-")
        
        # Basic extraction - in production, use NLP or structured parsing
        lines = content.split('\n') if content else []
        description = content[:500] if content else f"Research data for {company_name}"
        
        return {
            "name": company_name,
            "slug": slug,
            "description": description,
            "founded_year": None,
            "headquarters": "Unknown",
            "employee_count": "Unknown",
            "website": f"https://{slug}.com",
            "logo_url": f"https://logo.clearbit.com/{slug}.com",
            "industry": ["Technology"],
            "mission": f"Mission information for {company_name}",
            "status": "private"
        }
