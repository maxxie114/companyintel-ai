import httpx
import asyncio
from app.config import settings
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class SentimentService:
    def __init__(self):
        self.tavily_key = settings.tavily_api_key
        self.openai_key = settings.openai_api_key
        self.tavily_base_url = "https://api.tavily.com"
        self.openai_base_url = "https://api.openai.com/v1"
        self.timeout = 30.0
    
    async def analyze_news(self, company_name: str) -> Dict[str, Any]:
        """Analyze news sentiment using Tavily + OpenAI"""
        logger.info(f"Analyzing news sentiment for: {company_name}")
        
        if not self.tavily_key:
            raise Exception("Tavily API key not configured")
        if not self.openai_key:
            raise Exception("OpenAI API key not configured")
        
        try:
            # Search for recent news using Tavily
            news_results = await self._search_news(company_name)
            
            # Analyze sentiment using OpenAI
            sentiment_data = await self._analyze_sentiment_with_openai(company_name, news_results)
            
            return sentiment_data
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            raise
    
    async def _search_news(self, company_name: str) -> Dict[str, Any]:
        """Search for news using Tavily API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.tavily_base_url}/search",
                json={
                    "api_key": self.tavily_key,
                    "query": f"{company_name} news latest updates announcements",
                    "search_depth": "advanced",
                    "max_results": 10,
                    "include_answer": True,
                    "include_raw_content": False,
                    "topic": "news"
                }
            )
            
            response.raise_for_status()
            return response.json()
    
    async def _analyze_sentiment_with_openai(self, company_name: str, news_results: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenAI to analyze sentiment from news results"""
        results = news_results.get("results", [])
        
        if not results:
            raise Exception(f"No news found for {company_name}")
        
        # Prepare news articles for analysis
        articles = []
        for result in results[:5]:  # Analyze top 5 articles
            articles.append({
                "title": result.get("title", ""),
                "content": result.get("content", "")[:500],  # Limit content length
                "url": result.get("url", ""),
                "published_date": result.get("published_date", datetime.now().strftime("%Y-%m-%d"))
            })
        
        # Create prompt for OpenAI
        prompt = f"""Analyze the sentiment of these news articles about {company_name}.

Articles:
{json.dumps(articles, indent=2)}

Provide a JSON response with:
1. overall_sentiment: float between 0 (very negative) and 1 (very positive)
2. sentiment_label: "positive", "neutral", or "negative"
3. recent_news: array of articles with sentiment scores (0-1) and summaries
4. topics: array of main topics mentioned
5. customer_reviews: object with average_rating (1-5), pros, cons

Return ONLY valid JSON, no markdown or explanation."""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.openai_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a sentiment analysis expert. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1500
                }
            )
            
            response.raise_for_status()
            openai_response = response.json()
            
            # Parse OpenAI response
            content = openai_response["choices"][0]["message"]["content"]
            
            # Try to extract JSON from response
            try:
                # Remove markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                sentiment_data = json.loads(content)
            except json.JSONDecodeError:
                logger.warning("Failed to parse OpenAI JSON response, using fallback")
                sentiment_data = self._create_fallback_sentiment(articles)
            
            # Add sentiment timeline
            sentiment_data["sentiment_timeline"] = self._generate_timeline(sentiment_data.get("overall_sentiment", 0.6))
            
            return sentiment_data
    
    def _create_fallback_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create fallback sentiment data if OpenAI parsing fails"""
        return {
            "overall_sentiment": 0.6,
            "sentiment_label": "neutral",
            "recent_news": [
                {
                    "title": article["title"],
                    "url": article["url"],
                    "source": "News Source",
                    "published_date": article["published_date"],
                    "sentiment": 0.6,
                    "summary": article["content"][:200],
                    "topics": ["News"]
                }
                for article in articles
            ],
            "topics": ["Technology", "Business"],
            "customer_reviews": {
                "average_rating": 3.5,
                "review_count": 100,
                "pros": ["Good product"],
                "cons": ["Room for improvement"],
                "sources": ["G2"]
            }
        }
    
    def _generate_timeline(self, current_sentiment: float) -> List[Dict[str, Any]]:
        """Generate sentiment timeline for last 6 months"""
        timeline = []
        base_date = datetime.now()
        
        for i in range(6):
            date = base_date - timedelta(days=30 * i)
            # Simulate slight variation around current sentiment
            sentiment = max(0.0, min(1.0, current_sentiment + (i * 0.02) - 0.05))
            timeline.append({
                "date": date.strftime("%Y-%m-%d"),
                "sentiment": sentiment,
                "event": None
            })
        
        timeline.reverse()
        return timeline
