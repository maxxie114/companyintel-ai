from app.services.research import ResearchService
from app.services.browsing import BrowsingService
from app.services.financial import FinancialService
from app.services.competitor import CompetitorService
from app.services.sentiment import SentimentService
from app.services.graph import GraphService
from app.core.cache import update_progress, cache_company
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
        """Main orchestration logic"""
        company_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting analysis for {company_name} (session: {self.session_id})")
            
            # Stage 1: Research company (0.0 - 0.2)
            await self._update_progress(0.0, "researching_company", "Researching company overview...")
            overview_data = await self.research.get_company_overview(company_name)
            overview = CompanyOverview(**overview_data)
            
            # Stage 2: Extract APIs (0.2 - 0.4)
            await self._update_progress(0.2, "extracting_apis", "Extracting API documentation...")
            apis_data = await self.browsing.extract_api_docs(overview_data.get("website", ""))
            apis = ProductsAPIs(**apis_data)
            
            # Stage 3: Analyze competitors (0.4 - 0.6)
            await self._update_progress(0.4, "analyzing_competitors", "Analyzing competitors...")
            competitors_data = await self.competitor.find_competitors(company_name)
            competitors = MarketIntelligence(**competitors_data)
            
            # Stage 4: Gather financials (0.6 - 0.7)
            await self._update_progress(0.6, "gathering_financials", "Gathering financial data...")
            financials_data = await self.financial.get_financial_data(company_name)
            financials = Financials(**financials_data)
            
            # Stage 5: Analyze team (0.7 - 0.8)
            await self._update_progress(0.7, "analyzing_team", "Analyzing team & culture...")
            team_data = self._get_mock_team_data(company_name)
            team = TeamCulture(**team_data)
            
            # Stage 6: Process news (0.8 - 0.9)
            await self._update_progress(0.8, "processing_news", "Processing news & sentiment...")
            news_data = await self.sentiment.analyze_news(company_name)
            news = NewsSentiment(**news_data)
            
            # Stage 7: Build graph (0.9 - 1.0)
            await self._update_progress(0.9, "building_graph", "Building knowledge graph...")
            await self.graph.build_knowledge_graph(
                company_id,
                overview_data,
                apis_data,
                competitors_data,
                financials_data,
                team_data,
                news_data
            )
            
            # Complete
            await self._update_progress(1.0, "completed", "Analysis complete!")
            
            # Build complete response
            company_data = CompanyData(
                overview=overview,
                products_apis=apis,
                market_intelligence=competitors,
                financials=financials,
                team_culture=team,
                news_sentiment=news
            )
            
            metadata = CompanyMetadata(
                sources_count=45,
                confidence_score=0.92,
                last_updated=datetime.utcnow().isoformat()
            )
            
            result = {
                "id": company_id,
                "company_name": company_name,
                "slug": overview.slug,
                "analyzed_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "data": company_data.model_dump(),
                "metadata": metadata.model_dump()
            }
            
            # Cache results by company_id, slug, and session_id
            await cache_company(company_id, result)
            await cache_company(overview.slug, result)  # Also cache by slug
            await cache_company(self.session_id, result)  # Also cache by session_id for frontend
            
            logger.info(f"✓ Analysis complete for {company_name}")
            
        except Exception as e:
            logger.error(f"Error analyzing {company_name}: {e}", exc_info=True)
            await self._update_progress(0, "error", f"Error: {str(e)}")
    
    async def _update_progress(self, progress: float, stage: str, message: str = ""):
        """Update progress in Redis"""
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
