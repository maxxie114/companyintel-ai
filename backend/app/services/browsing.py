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

    async def _gather_tavily_intelligence(self, company_name: str, website: str) -> Dict[str, Any]:
        """Run parallel Tavily searches to find docs URL, pre-research the API landscape,
        and collect content snippets — all used to make Yutori's task maximally targeted."""
        if not self.tavily_key:
            return {"docs_url": website, "context": "", "snippets": "", "answers": []}

        domain = website.replace("https://", "").replace("http://", "").rstrip("/")
        base = domain.split(".")[-2] if "." in domain else domain

        queries = [
            f"{company_name} developer API documentation official docs site:{domain}",
            f"{company_name} REST API endpoints authentication SDK programming languages",
            f"{company_name} API pricing plans developer tiers",
        ]

        async def _search(query: str) -> Dict[str, Any]:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    r = await client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": self.tavily_key,
                            "query": query,
                            "search_depth": "advanced",
                            "max_results": 5,
                            "include_answer": True,
                        }
                    )
                    r.raise_for_status()
                    return r.json()
            except Exception as e:
                logger.warning(f"Tavily search failed for '{query}': {e}")
                return {}

        # Fire all three searches in parallel
        docs_result, api_result, pricing_result = await asyncio.gather(
            _search(queries[0]),
            _search(queries[1]),
            _search(queries[2]),
        )

        # --- Find docs URL ---
        dev_keywords = ["developer", "developers", "docs", "documentation", "api", "platform", "dev", "reference"]
        docs_url = website
        for res in docs_result.get("results", []):
            url = res.get("url", "").lower()
            if base in url and any(k in url for k in dev_keywords):
                docs_url = res["url"].rstrip("/")
                logger.info(f"✓ Tavily found docs URL for {company_name}: {docs_url}")
                break
        if docs_url == website:
            for res in docs_result.get("results", []):
                if base in res.get("url", "").lower():
                    docs_url = res["url"].rstrip("/")
                    logger.info(f"Tavily fallback docs URL for {company_name}: {docs_url}")
                    break

        # --- Collect Tavily AI answers ---
        answers = []
        for result_set in [docs_result, api_result, pricing_result]:
            answer = result_set.get("answer", "")
            if answer:
                answers.append(answer)

        # --- Collect content snippets from all results ---
        snippets = []
        seen_urls = set()
        for result_set in [docs_result, api_result, pricing_result]:
            for res in result_set.get("results", [])[:3]:
                url = res.get("url", "")
                content = res.get("content", "").strip()
                if content and url not in seen_urls:
                    seen_urls.add(url)
                    snippets.append(f"[Source: {url}]\n{content}")

        snippets_text = "\n\n---\n\n".join(snippets[:8])  # up to 8 snippets

        # --- Build a structured context summary for Yutori ---
        context_parts = []
        if answers:
            context_parts.append("Web research summary:\n" + "\n".join(f"• {a}" for a in answers))
        if snippets:
            # Extract key signals from snippets to hint Yutori
            api_hints = []
            sdk_hints = []
            pricing_hints = []
            for s in snippets:
                sl = s.lower()
                if any(w in sl for w in ["endpoint", "rest api", "graphql", "webhook", "oauth"]):
                    api_hints.append(s[:300])
                if any(w in sl for w in ["python", "javascript", "node", "ruby", "go", "java", "sdk", "library"]):
                    sdk_hints.append(s[:200])
                if any(w in sl for w in ["pricing", "plan", "free", "enterprise", "per month", "per request"]):
                    pricing_hints.append(s[:200])

            if api_hints:
                context_parts.append("Known API signals:\n" + "\n".join(api_hints[:2]))
            if sdk_hints:
                context_parts.append("Known SDK signals:\n" + "\n".join(sdk_hints[:2]))
            if pricing_hints:
                context_parts.append("Known pricing signals:\n" + "\n".join(pricing_hints[:2]))

        context = "\n\n".join(context_parts)
        logger.info(
            f"✓ Tavily intelligence gathered for {company_name}: "
            f"{len(snippets)} snippets, {len(answers)} AI answers, docs_url={docs_url}"
        )

        return {
            "docs_url": docs_url,
            "context": context,
            "snippets": snippets_text,
            "answers": answers,
        }

    async def extract_api_docs(self, website: str, company_name: str = "") -> Dict[str, Any]:
        """Gather Tavily intelligence first, then send a targeted Yutori browse."""
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
            # Step 1: Tavily gathers intelligence in parallel (docs URL + API/SDK/pricing context)
            intel = await self._gather_tavily_intelligence(company_name or website, website)
            docs_url = intel["docs_url"]
            tavily_snippets = intel["snippets"]
            yutori_context = intel["context"]

            logger.info(f"Sending Yutori to: {docs_url}")

            # Step 2: One targeted Yutori browse, enriched with Tavily context
            try:
                result = await self._browse_page(docs_url, company_name=company_name, context=yutori_context)
                if result:
                    parsed_data = await self._parse_api_docs(docs_url, result, tavily_snippets=tavily_snippets)
                    await redis_cache.set(cache_key, parsed_data, ttl=self.cache_ttl)
                    logger.info(f"✓ Cached browsing results for {website} (TTL: 7 days)")
                    return parsed_data
            except Exception as e:
                logger.warning(f"Yutori browse failed for {docs_url}: {e}")

            # Step 3: Yutori failed — fall back to parsing Tavily snippets alone
            if tavily_snippets:
                logger.info(f"Falling back to Tavily snippets for {company_name}")
                fallback = await self._parse_api_docs(docs_url, {"result": tavily_snippets}, tavily_snippets="")
                if fallback.get("products") or fallback.get("apis"):
                    fallback["note"] = "Extracted from web search (Yutori unavailable)"
                    await redis_cache.set(cache_key, fallback, ttl=self.cache_ttl)
                    return fallback

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

    async def _browse_page(self, url: str, company_name: str = "", context: str = "") -> Dict[str, Any]:
        """Browse a page using Yutori Browsing API. Task prompt is enriched with Tavily pre-research."""
        context_block = f"\n\nPre-research context from web search:\n{context}\n" if context else ""

        task = f"""You are extracting complete API documentation for {company_name or url}.{context_block}
Navigate this developer documentation site and extract:
1. All API product offerings and what each does (Payments API, Video API, etc.)
2. API endpoints with HTTP methods and paths (GET /v1/charges, POST /v2/meetings, etc.)
3. Authentication methods (API key, OAuth 2.0, JWT, etc.)
4. Official SDK/client libraries and supported programming languages
5. Pricing plans — tier names, prices, included features
6. Rate limits or usage quotas if mentioned

Follow navigation links to sub-pages (API Reference, SDKs, Pricing) to find complete information.
Return a thorough structured summary of everything found."""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/browsing/tasks",
                headers={"X-API-Key": self.api_key},
                json={"task": task, "start_url": url}
            )
            response.raise_for_status()
            task_data = response.json()
            task_id = task_data.get("task_id")
            logger.info(f"Yutori browsing task created: {task_id}")
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

    async def _parse_api_docs(self, url: str, raw_data: Dict[str, Any], tavily_snippets: str = "") -> Dict[str, Any]:
        """Parse API documentation using OpenAI. Combines Yutori result + Tavily snippets for richer context."""
        result = raw_data.get("result", "")
        if isinstance(result, dict):
            text = result.get("content") or result.get("text") or str(result)
        else:
            text = str(result) if result else ""

        yutori_text = text[:4000]

        # Combine Yutori content + Tavily snippets for OpenAI
        combined_parts = []
        if yutori_text.strip():
            combined_parts.append(f"=== Browser-extracted content ===\n{yutori_text}")
        if tavily_snippets.strip():
            combined_parts.append(f"=== Web search snippets ===\n{tavily_snippets[:2000]}")
        raw_content = "\n\n".join(combined_parts)

        if not raw_content.strip() or not self.openai_key:
            return {
                "products": [],
                "apis": [],
                "documentation_quality": 2.0,
                "sdk_languages": [],
                "pricing": [],
                "raw_content": yutori_text,
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
                        "max_tokens": 1500
                    }
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]

                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                parsed = json.loads(content)
                parsed["raw_content"] = yutori_text
                parsed["apis"] = self._normalize_apis(parsed.get("apis", []))
                parsed["pricing"] = self._normalize_pricing(parsed.get("pricing", []))
                parsed["products"] = self._normalize_products(parsed.get("products", []))
                logger.info(
                    f"✓ OpenAI extracted API docs: {len(parsed.get('products', []))} products, "
                    f"{len(parsed.get('apis', []))} API endpoints, langs={parsed.get('sdk_languages', [])}"
                )
                return parsed

        except Exception as e:
            logger.warning(f"OpenAI API docs extraction failed: {e}")
            return {
                "products": [],
                "apis": [],
                "documentation_quality": 2.5,
                "sdk_languages": [],
                "pricing": [],
                "raw_content": yutori_text,
            }
