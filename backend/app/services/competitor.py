import httpx
import asyncio
from app.config import settings
from app.core.cache import redis_cache
from typing import Dict, Any, List
import logging
import hashlib

logger = logging.getLogger(__name__)

class CompetitorService:
    def __init__(self):
        self.tavily_key = settings.tavily_api_key
        self.base_url = "https://api.tavily.com"
        self.timeout = 30.0
        self.cache_ttl = 86400 * 3  # 3 days cache for competitor data
    
    def _get_cache_key(self, company_name: str) -> str:
        """Generate cache key for competitor analysis"""
        name_hash = hashlib.md5(company_name.lower().encode()).hexdigest()
        return f"tavily:competitors:{name_hash}:{company_name.lower().replace(' ', '_')}"
    
    async def find_competitors(self, company_name: str) -> Dict[str, Any]:
        """Identify and analyze competitors using Tavily search with Redis caching"""
        logger.info(f"Analyzing competitors for: {company_name}")
        
        # Check cache first
        cache_key = self._get_cache_key(company_name)
        cached_result = await redis_cache.get(cache_key)
        
        if cached_result:
            logger.info(f"✓ Cache HIT for competitors of {company_name}")
            return cached_result
        
        logger.info(f"Cache MISS for competitors - calling Tavily API")
        
        if not self.tavily_key:
            raise Exception("Tavily API key not configured")
        
        try:
            # Search for competitor information
            query = f"{company_name} competitors alternatives comparison market analysis"
            search_results = await self._search_tavily(query)
            
            # Parse results to extract competitor information
            parsed_data = self._parse_competitors(company_name, search_results)
            
            # Cache the result for 3 days
            await redis_cache.set(cache_key, parsed_data, ttl=self.cache_ttl)
            logger.info(f"✓ Cached competitor data for {company_name} (TTL: 3 days)")
            
            return parsed_data
        
        except Exception as e:
            logger.error(f"Error finding competitors: {e}")
            raise
    
    async def _search_tavily(self, query: str) -> Dict[str, Any]:
        """Search using Tavily API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/search",
                json={
                    "api_key": self.tavily_key,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": 10,
                    "include_answer": True,
                    "include_raw_content": False
                }
            )
            
            response.raise_for_status()
            return response.json()
    
    def _parse_competitors(self, company_name: str, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse search results to extract competitor information"""
        results = search_results.get("results", [])
        answer = search_results.get("answer", "")
        
        # Extract competitor names from results (simplified)
        competitors = []
        seen_names = set()
        
        # Basic extraction - in production, use NLP
        for result in results[:4]:
            title = result.get("title", "")
            content = result.get("content", "")
            
            # Simple heuristic: look for company names in title
            if "vs" in title.lower() or "alternative" in title.lower():
                # Extract potential competitor name
                words = title.split()
                for word in words:
                    if word not in seen_names and word != company_name and len(word) > 3:
                        seen_names.add(word)
                        competitors.append({
                            "name": word,
                            "slug": word.lower().replace(" ", "-"),
                            "relationship": "direct",
                            "strengths": ["Market presence"],
                            "weaknesses": ["Unknown"],
                            "market_overlap_percent": 50.0
                        })
                        if len(competitors) >= 4:
                            break
        
        return {
            "competitors": competitors,
            "market_position": f"Analysis based on search results for {company_name}",
            "market_share_percent": None,
            "niche": "Technology sector",
            "differentiation": ["Innovation", "Technology"],
            "target_market": ["Businesses", "Enterprises"],
            "search_summary": answer[:500] if answer else "Competitor analysis completed"
        }
