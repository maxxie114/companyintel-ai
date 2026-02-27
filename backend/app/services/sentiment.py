import httpx
from app.config import settings
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SentimentService:
    def __init__(self):
        self.tavily_key = settings.tavily_api_key
        self.openai_key = settings.openai_api_key
        self.timeout = 30.0
    
    async def analyze_news(self, company_name: str) -> Dict[str, Any]:
        """Analyze news sentiment"""
        logger.info(f"Analyzing news sentiment for: {company_name}")
        
        # For MVP, use mock data
        return self._get_mock_sentiment(company_name)
    
    def _get_mock_sentiment(self, company_name: str) -> Dict[str, Any]:
        """Return mock sentiment data"""
        slug = company_name.lower().replace(" ", "-")
        
        # Generate timeline for last 6 months
        timeline = []
        base_date = datetime.now()
        for i in range(6):
            date = base_date - timedelta(days=30 * i)
            sentiment = 0.7 + (i * 0.05)  # Trending up
            timeline.append({
                "date": date.strftime("%Y-%m-%d"),
                "sentiment": min(sentiment, 1.0),
                "event": None
            })
        timeline.reverse()
        
        mock_data = {
            "stripe": {
                "overall_sentiment": 0.85,
                "sentiment_label": "positive",
                "recent_news": [
                    {
                        "title": "Stripe Expands Global Payment Infrastructure",
                        "url": "https://example.com/news1",
                        "source": "TechCrunch",
                        "published_date": "2026-02-20",
                        "sentiment": 0.9,
                        "summary": "Stripe announces expansion into 15 new markets with enhanced payment capabilities.",
                        "topics": ["Expansion", "Payments", "Growth"]
                    },
                    {
                        "title": "Stripe Reports Strong Revenue Growth",
                        "url": "https://example.com/news2",
                        "source": "Bloomberg",
                        "published_date": "2026-02-15",
                        "sentiment": 0.85,
                        "summary": "Company sees 50% year-over-year revenue growth driven by enterprise adoption.",
                        "topics": ["Revenue", "Growth", "Enterprise"]
                    },
                    {
                        "title": "Developers Praise Stripe's New API Features",
                        "url": "https://example.com/news3",
                        "source": "The Verge",
                        "published_date": "2026-02-10",
                        "sentiment": 0.8,
                        "summary": "New developer tools and API improvements receive positive feedback from community.",
                        "topics": ["API", "Developers", "Innovation"]
                    }
                ],
                "sentiment_timeline": timeline,
                "topics": ["Payments", "API", "Growth", "Innovation", "Enterprise"],
                "customer_reviews": {
                    "average_rating": 4.5,
                    "review_count": 1250,
                    "pros": ["Excellent documentation", "Easy integration", "Reliable service", "Great support"],
                    "cons": ["Pricing can be high", "Complex for simple use cases"],
                    "sources": ["G2", "Capterra", "TrustRadius"]
                }
            },
            "openai": {
                "overall_sentiment": 0.75,
                "sentiment_label": "positive",
                "recent_news": [
                    {
                        "title": "OpenAI Releases GPT-5 with Enhanced Capabilities",
                        "url": "https://example.com/news1",
                        "source": "The Verge",
                        "published_date": "2026-02-25",
                        "sentiment": 0.9,
                        "summary": "Latest model shows significant improvements in reasoning and multimodal understanding.",
                        "topics": ["AI", "GPT-5", "Innovation"]
                    },
                    {
                        "title": "OpenAI Faces Regulatory Scrutiny",
                        "url": "https://example.com/news2",
                        "source": "Reuters",
                        "published_date": "2026-02-18",
                        "sentiment": 0.4,
                        "summary": "Regulators raise concerns about AI safety and data privacy practices.",
                        "topics": ["Regulation", "Safety", "Privacy"]
                    },
                    {
                        "title": "ChatGPT Reaches 200M Weekly Users",
                        "url": "https://example.com/news3",
                        "source": "TechCrunch",
                        "published_date": "2026-02-12",
                        "sentiment": 0.85,
                        "summary": "Platform continues rapid growth with strong user engagement metrics.",
                        "topics": ["Growth", "ChatGPT", "Users"]
                    }
                ],
                "sentiment_timeline": timeline,
                "topics": ["AI", "GPT", "ChatGPT", "Innovation", "Regulation"],
                "customer_reviews": {
                    "average_rating": 4.3,
                    "review_count": 850,
                    "pros": ["Powerful capabilities", "Easy API", "Good documentation", "Fast responses"],
                    "cons": ["Occasional downtime", "Rate limits", "Cost at scale"],
                    "sources": ["G2", "Product Hunt"]
                }
            }
        }
        
        return mock_data.get(slug, {
            "overall_sentiment": 0.6,
            "sentiment_label": "neutral",
            "recent_news": [
                {
                    "title": f"{company_name} Announces New Product",
                    "url": "https://example.com/news1",
                    "source": "Tech News",
                    "published_date": datetime.now().strftime("%Y-%m-%d"),
                    "sentiment": 0.7,
                    "summary": f"{company_name} launches new product to positive reception.",
                    "topics": ["Product", "Launch"]
                }
            ],
            "sentiment_timeline": timeline,
            "topics": ["Technology", "Innovation"],
            "customer_reviews": {
                "average_rating": 3.8,
                "review_count": 100,
                "pros": ["Good product", "Responsive team"],
                "cons": ["Room for improvement"],
                "sources": ["G2"]
            }
        })
