import httpx
import asyncio
import json
from app.config import settings
from app.core.cache import redis_cache
from typing import Dict, Any, List
import logging
import hashlib

logger = logging.getLogger(__name__)

class CompetitorService:
    def __init__(self):
        self.tavily_key = settings.tavily_api_key
        self.openai_key = settings.openai_api_key
        self.base_url = "https://api.tavily.com"
        self.timeout = 30.0
        self.cache_ttl = 86400 * 3  # 3 days cache for competitor data

    def _get_cache_key(self, company_name: str) -> str:
        name_hash = hashlib.md5(company_name.lower().encode()).hexdigest()
        return f"tavily:competitors:{name_hash}:{company_name.lower().replace(' ', '_')}"

    async def find_competitors(self, company_name: str) -> Dict[str, Any]:
        """Identify competitors using Tavily search + OpenAI extraction with Redis caching"""
        logger.info(f"Analyzing competitors for: {company_name}")

        cache_key = self._get_cache_key(company_name)
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            logger.info(f"✓ Cache HIT for competitors of {company_name}")
            return cached_result

        logger.info(f"Cache MISS for competitors - calling Tavily API")

        if not self.tavily_key:
            raise Exception("Tavily API key not configured")

        try:
            query = f"{company_name} competitors alternatives comparison market analysis"
            search_results = await self._search_tavily(query)
            parsed_data = await self._parse_competitors(company_name, search_results)

            await redis_cache.set(cache_key, parsed_data, ttl=self.cache_ttl)
            logger.info(f"✓ Cached competitor data for {company_name} (TTL: 3 days)")

            return parsed_data

        except Exception as e:
            logger.error(f"Error finding competitors: {e}")
            raise

    async def _search_tavily(self, query: str) -> Dict[str, Any]:
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

    async def _parse_competitors(self, company_name: str, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract competitor data using OpenAI on Tavily results."""
        answer = search_results.get("answer", "")
        results = search_results.get("results", [])

        # Build context for OpenAI
        context_parts = []
        if answer:
            context_parts.append(f"Summary: {answer}")
        for r in results[:5]:
            title   = r.get("title", "")
            content = r.get("content", "")[:400]
            if title:
                context_parts.append(f"Title: {title}")
            if content:
                context_parts.append(f"Excerpt: {content}")
        context = "\n\n".join(context_parts)

        competitors = await self._extract_competitors_with_openai(company_name, context)

        # Also extract market context from OpenAI
        market_info = await self._extract_market_info_with_openai(company_name, context)

        return {
            "competitors": competitors,
            "market_position": market_info.get("market_position", f"{company_name} competes in the technology sector"),
            "market_share_percent": market_info.get("market_share_percent"),
            "niche": market_info.get("niche", "Technology"),
            "differentiation": market_info.get("differentiation", []),
            "target_market": market_info.get("target_market", []),
            "search_summary": answer[:500] if answer else "",
        }

    async def _extract_competitors_with_openai(self, company_name: str, context: str) -> List[Dict[str, Any]]:
        """Use OpenAI to extract real competitor companies from Tavily text."""
        if not self.openai_key:
            return []

        prompt = f"""Based on this research about {company_name}'s competitive landscape:

{context}

Extract the top 5-6 real competitor companies. Return a JSON array with exactly this structure:
[
  {{
    "name": "Actual Company Name",
    "slug": "actual-company-name",
    "relationship": "direct",
    "strengths": ["key strength 1", "key strength 2"],
    "weaknesses": ["key weakness 1"],
    "market_overlap_percent": 75.0
  }}
]

Rules:
- Only include real, named companies (no generic words like "Alternatives" or "Solutions")
- relationship must be "direct" or "indirect"
- market_overlap_percent is a float 0-100
- Return ONLY the JSON array, no explanation"""

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
                            {"role": "system", "content": "You extract structured competitor data from research text. Return only valid JSON arrays containing real company names."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 900
                    }
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]

                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                return json.loads(content)

        except Exception as e:
            logger.warning(f"OpenAI competitor extraction failed: {e}")
            return []

    async def _extract_market_info_with_openai(self, company_name: str, context: str) -> Dict[str, Any]:
        """Use OpenAI to extract market positioning info."""
        if not self.openai_key:
            return {}

        prompt = f"""Based on this research about {company_name}:

{context[:1500]}

Return a JSON object with:
{{
  "market_position": "1-2 sentence description of {company_name}'s market position",
  "niche": "primary market niche (e.g. 'Fintech / Payment Processing')",
  "differentiation": ["key differentiator 1", "key differentiator 2", "key differentiator 3"],
  "target_market": ["target segment 1", "target segment 2"]
}}

Return ONLY the JSON object."""

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
                            {"role": "system", "content": "You extract market positioning data from research text. Return only valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 400
                    }
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]

                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                return json.loads(content)

        except Exception as e:
            logger.warning(f"OpenAI market info extraction failed: {e}")
            return {}
