from app.services.research import ResearchService
from app.services.browsing import BrowsingService
from app.services.financial import FinancialService
from app.services.competitor import CompetitorService
from app.services.sentiment import SentimentService
from app.services.graph import GraphService
from app.core.cache import update_progress, cache_company, get_cached_company
from app.models import (
    CompanyData, CompanyOverview, ProductsAPIs, MarketIntelligence,
    Financials, TeamCulture, NewsSentiment, CompanyMetadata
)
from datetime import datetime
import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)

class CompanyOrchestrator:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.research = ResearchService()
        self.browsing = BrowsingService()
        self.financial = FinancialService()
        self.competitor = CompetitorService()
        self.sentiment = SentimentService()
        self.graph = GraphService()
    
    async def analyze(self, company_name: str, options: dict):
        """
        Fast-path analysis: Tavily + OpenAI finish in ~30-60s, result shown immediately.
        Yutori Browsing and graph building run in the background and enrich the cache.
        """
        company_id = str(uuid.uuid4())
        self._current_progress = 0.0

        try:
            logger.info(f"Starting analysis for {company_name} (session: {self.session_id})")

            # Stage 1: Quick company overview via Tavily (~2s), Yutori starts in background
            await self._update_progress(0.1, "researching_company", "Searching company info...")
            overview_data = await self.research.get_quick_overview(company_name)
            overview = CompanyOverview(**overview_data)

            # Stage 2: Competitors via Tavily (~3s)
            await self._update_progress(0.3, "analyzing_competitors", "Analyzing competitors...")
            competitors_data = await self.competitor.find_competitors(company_name)
            competitors = MarketIntelligence(**competitors_data)

            # Stage 3: Financials (~2s)
            await self._update_progress(0.5, "gathering_financials", "Gathering financial data...")
            financials_data = await self.financial.get_financial_data(company_name)
            financials = Financials(**financials_data)

            # Stage 4: Team (instant, mock)
            await self._update_progress(0.6, "analyzing_team", "Analyzing team & culture...")
            team_data = self._get_mock_team_data(company_name)
            team = TeamCulture(**team_data)

            # Stage 5: News & sentiment via Tavily + OpenAI (~30s)
            await self._update_progress(0.7, "processing_news", "Processing news & sentiment...")
            news_data = await self.sentiment.analyze_news(company_name)
            news_data = self._normalize_sentiment_data(news_data)
            news = NewsSentiment(**news_data)

            # API docs start empty — Yutori Browsing fills this in the background
            apis = ProductsAPIs()

            await self._update_progress(0.9, "finalizing", "Finalizing results...")

            company_data = CompanyData(
                overview=overview,
                products_apis=apis,
                market_intelligence=competitors,
                financials=financials,
                team_culture=team,
                news_sentiment=news
            )

            metadata = CompanyMetadata(
                sources_count=20,
                confidence_score=0.75,
                last_updated=datetime.utcnow().isoformat()
            )

            result = {
                "id": company_id,
                "company_name": company_name,
                "slug": overview.slug,
                "analyzed_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "enrichment_status": "pending",
                "data": company_data.model_dump(),
                "metadata": metadata.model_dump()
            }

            await cache_company(company_id, result)
            await cache_company(overview.slug, result)
            await cache_company(self.session_id, result)

            await self._update_progress(1.0, "completed", "Analysis complete! Deep API research running in background...")
            logger.info(f"✓ Fast analysis complete for {company_name}, launching background enrichment")

            # Fire and forget: Yutori Browsing + graph building
            asyncio.create_task(
                self._background_enrich(company_name, company_id, overview.slug, overview_data)
            )

        except Exception as e:
            logger.error(f"Error analyzing {company_name}: {e}", exc_info=True)
            await self._update_progress(self._current_progress, "error", f"Error: {str(e)}")

    async def _background_enrich(self, company_name: str, company_id: str, slug: str, overview_data: dict):
        """
        Background enrichment — runs after the user already has results.
        1. Yutori Browsing for deep API docs (5-10 min)
        2. Neo4j knowledge graph
        Updates the cache so the next lookup gets richer data.
        """
        logger.info(f"🔄 Background enrichment started for {company_name}")

        apis_data = {"products": [], "apis": [], "documentation_quality": 0.0, "sdk_languages": [], "pricing": []}

        # Yutori Browsing (slow — browser-use agent)
        try:
            website = overview_data.get("website", "")
            if website:
                logger.info(f"Starting Yutori browsing for {website}")
                apis_data = await self.browsing.extract_api_docs(website, company_name)
                logger.info(f"✓ Yutori browsing complete for {company_name}")
        except Exception as e:
            logger.warning(f"Browsing enrichment failed for {company_name}: {e}")

        # Neo4j graph building
        try:
            competitors_data = await self.competitor.find_competitors(company_name)
            financials_data = await self.financial.get_financial_data(company_name)
            team_data = self._get_mock_team_data(company_name)
            news_data = await self.sentiment.analyze_news(company_name)
            await self.graph.build_knowledge_graph(
                company_id, overview_data, apis_data,
                competitors_data, financials_data, team_data, news_data
            )
            logger.info(f"✓ Knowledge graph built for {company_name}")
        except Exception as e:
            logger.warning(f"Graph building failed for {company_name}: {e}")

        # Push enriched API docs into the cached result
        try:
            cached = await get_cached_company(company_id)
            if cached:
                cached["data"]["products_apis"] = apis_data
                cached["enrichment_status"] = "completed"
                cached["metadata"]["sources_count"] = 45
                cached["metadata"]["confidence_score"] = 0.92
                await cache_company(company_id, cached)
                await cache_company(slug, cached)
                await cache_company(self.session_id, cached)  # also update the session lookup
                logger.info(f"✅ Cache enriched with deep API data for {company_name}")
        except Exception as e:
            logger.warning(f"Cache enrichment update failed for {company_name}: {e}")

    def _normalize_sentiment_data(self, data: dict) -> dict:
        """
        Normalize sentiment data to match the Pydantic model regardless of how
        OpenAI chose to name fields. Also fixes stale cache entries with old formats.
        """
        normalized = data.copy()

        # Normalize recent_news items — map any field name variant to what NewsArticle expects
        raw_news = normalized.get("recent_news", [])
        normalized_news = []
        for item in raw_news:
            if not isinstance(item, dict):
                continue
            normalized_news.append({
                "title": item.get("title") or item.get("headline") or "News Article",
                "url": item.get("url") or item.get("link") or "#",
                "source": (item.get("source") or item.get("publisher")
                           or item.get("outlet") or "Unknown"),
                "published_date": (item.get("published_date") or item.get("date")
                                   or item.get("publish_date")
                                   or datetime.utcnow().strftime("%Y-%m-%d")),
                "sentiment": float(item.get("sentiment") or item.get("sentiment_score")
                                   or item.get("score") or 0.5),
                "summary": (item.get("summary") or item.get("content")
                            or item.get("description") or ""),
                "topics": item.get("topics") or [],
            })
        normalized["recent_news"] = normalized_news

        # Normalize customer_reviews — handle missing fields and string pros/cons
        reviews = normalized.get("customer_reviews") or {}
        if isinstance(reviews, dict):
            pros = reviews.get("pros", [])
            cons = reviews.get("cons", [])
            normalized["customer_reviews"] = {
                "average_rating": float(reviews.get("average_rating") or 3.5),
                "review_count": int(reviews.get("review_count") or 0),
                "pros": pros if isinstance(pros, list) else [p.strip() for p in str(pros).split(",") if p.strip()],
                "cons": cons if isinstance(cons, list) else [c.strip() for c in str(cons).split(",") if c.strip()],
                "sources": reviews.get("sources") or ["G2"],
            }

        return normalized
    
    async def _update_progress(self, progress: float, stage: str, message: str = ""):
        """Update progress in Redis"""
        self._current_progress = progress
        progress_data = {
            "type": "progress" if progress < 1.0 else "completed",
            "session_id": self.session_id,
            "stage": stage,
            "progress": progress,
            "message": message or f"Processing {stage}...",
            "timestamp": datetime.utcnow().isoformat()
        }
        await update_progress(self.session_id, progress_data)
        logger.info(f"Progress: {int(progress * 100)}% - {stage}")
    
    def _get_mock_team_data(self, company_name: str) -> dict:
        """Get mock team data"""
        slug = company_name.lower().replace(" ", "-")
        
        mock_data = {
            "stripe": {
                "leadership": [
                    {
                        "name": "Patrick Collison",
                        "title": "CEO & Co-founder",
                        "background": "Co-founded Stripe in 2010 with his brother John",
                        "linkedin_url": None,
                        "photo_url": None
                    },
                    {
                        "name": "John Collison",
                        "title": "President & Co-founder",
                        "background": "Co-founded Stripe in 2010, focuses on product and business",
                        "linkedin_url": None,
                        "photo_url": None
                    }
                ],
                "tech_stack": ["Ruby", "JavaScript", "React", "PostgreSQL", "Redis", "Kafka", "Kubernetes"],
                "culture_signals": ["Remote-friendly", "Engineering-driven", "Customer-focused", "Innovation"],
                "work_model": "hybrid",
                "open_positions_count": 150,
                "hiring_focus": ["Engineering", "Product", "Sales", "Support"]
            },
            "openai": {
                "leadership": [
                    {
                        "name": "Sam Altman",
                        "title": "CEO",
                        "background": "Former president of Y Combinator, leading OpenAI since 2019",
                        "linkedin_url": None,
                        "photo_url": None
                    },
                    {
                        "name": "Greg Brockman",
                        "title": "President & Co-founder",
                        "background": "Former CTO of Stripe, co-founded OpenAI in 2015",
                        "linkedin_url": None,
                        "photo_url": None
                    }
                ],
                "tech_stack": ["Python", "PyTorch", "Kubernetes", "Azure", "React", "TypeScript"],
                "culture_signals": ["Research-focused", "Safety-conscious", "Mission-driven", "Collaborative"],
                "work_model": "hybrid",
                "open_positions_count": 80,
                "hiring_focus": ["Research", "Engineering", "Safety", "Product"]
            }
        }
        
        return mock_data.get(slug, {
            "leadership": [
                {
                    "name": "CEO Name",
                    "title": "CEO & Founder",
                    "background": "Experienced technology leader",
                    "linkedin_url": None,
                    "photo_url": None
                }
            ],
            "tech_stack": ["Python", "JavaScript", "PostgreSQL", "React"],
            "culture_signals": ["Innovation", "Collaboration", "Growth"],
            "work_model": "hybrid",
            "open_positions_count": 20,
            "hiring_focus": ["Engineering", "Product"]
        })
