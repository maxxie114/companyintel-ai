import httpx
import asyncio
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
    
    async def get_company_overview(self, company_name: str) -> Dict[str, Any]:
        """
        Smart caching strategy for Yutori Research:
        1. Check cache - return immediately if found
        2. Check if task exists - poll once to see if done
        3. Create new task - start background polling
        """
        logger.info(f"Researching company: {company_name}")
        
        # Step 1: Check cache first
        cache_key = self._get_cache_key(company_name)
        cached_result = await redis_cache.get(cache_key)
        
        if cached_result:
            logger.info(f"✓ Cache HIT for {company_name} - returning cached research")
            return cached_result
        
        logger.info(f"Cache MISS for {company_name}")
        
        if not self.api_key:
            raise Exception("Yutori API key not configured")
        
        # Step 2: Check if there's a pending task
        task_key = self._get_task_key(company_name)
        existing_task_id = await redis_cache.get(task_key)
        
        if existing_task_id:
            logger.info(f"Found existing task {existing_task_id} for {company_name}")
            # Check if it's done
            result = await self._check_task_once(existing_task_id)
            if result:
                # Task completed! Parse, cache, and return
                parsed_data = self._parse_overview(company_name, result)
                await redis_cache.set(cache_key, parsed_data, ttl=self.cache_ttl)
                await redis_cache.delete(task_key)  # Clear task ID
                logger.info(f"✓ Task completed and cached for {company_name}")
                return parsed_data
            else:
                # Still running
                raise Exception(
                    f"Research task still running (Task ID: {existing_task_id}). "
                    f"Yutori takes 5-10 minutes. Please try again in a few minutes."
                )
        
        # Step 3: No cache, no pending task - create new task
        try:
            task_id = await self._create_task(company_name)
            
            # Save task ID (1 hour TTL)
            await redis_cache.set(task_key, task_id, ttl=3600)
            
            # Start background polling (fire and forget)
            asyncio.create_task(
                self._background_poll_and_cache(task_id, company_name, cache_key, task_key)
            )
            
            logger.info(f"✓ Background polling started for task {task_id}")
            
            # Return error indicating task is running
            raise Exception(
                f"Research task started (Task ID: {task_id}). "
                f"Yutori takes 5-10 minutes to complete. "
                f"Please try again in a few minutes - results will be cached."
            )
        
        except Exception as e:
            logger.error(f"Error researching {company_name}: {e}")
            raise
    
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
                                parsed_data = self._parse_overview(company_name, data)
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
    
    def _parse_overview(self, company_name: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw research data into CompanyOverview format"""
        # Extract data from Yutori response
        result = raw_data.get("result", "")
        
        # Handle both string and dict results
        if isinstance(result, dict):
            content = result.get("content", "")
        else:
            content = str(result)
        
        # Parse the HTML content
        slug = company_name.lower().replace(" ", "-")
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
            "status": "private",
            "raw_content": content  # Store full content
        }
