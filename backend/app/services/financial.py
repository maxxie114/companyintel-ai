import httpx
from app.config import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class FinancialService:
    def __init__(self):
        self.alpha_vantage_key = settings.alpha_vantage_api_key
        self.timeout = 30.0
    
    async def get_financial_data(self, company_name: str) -> Dict[str, Any]:
        """Get financial data from multiple sources"""
        logger.info(f"Gathering financial data for: {company_name}")
        
        # For MVP, use mock data
        return self._get_mock_financials(company_name)
    
    def _get_mock_financials(self, company_name: str) -> Dict[str, Any]:
        """Return mock financial data"""
        slug = company_name.lower().replace(" ", "-")
        
        mock_data = {
            "stripe": {
                "status": "private",
                "stock_symbol": None,
                "stock_price": None,
                "market_cap": None,
                "last_funding_round": {
                    "round": "Series I",
                    "amount": 600000000,
                    "date": "2023-03-14",
                    "investors": ["Sequoia Capital", "Andreessen Horowitz", "General Catalyst"],
                    "valuation": 50000000000
                },
                "total_funding": 2200000000,
                "valuation": 50000000000,
                "revenue_estimate": 14000000000,
                "revenue_growth_yoy": 50.0,
                "profitability_status": "profitable",
                "burn_rate": None
            },
            "openai": {
                "status": "private",
                "stock_symbol": None,
                "stock_price": None,
                "market_cap": None,
                "last_funding_round": {
                    "round": "Series C",
                    "amount": 10000000000,
                    "date": "2023-01-23",
                    "investors": ["Microsoft", "Sequoia Capital", "Andreessen Horowitz"],
                    "valuation": 29000000000
                },
                "total_funding": 11300000000,
                "valuation": 29000000000,
                "revenue_estimate": 1600000000,
                "revenue_growth_yoy": 200.0,
                "profitability_status": "burning",
                "burn_rate": "$500M/year"
            }
        }
        
        return mock_data.get(slug, {
            "status": "private",
            "stock_symbol": None,
            "stock_price": None,
            "market_cap": None,
            "last_funding_round": {
                "round": "Series A",
                "amount": 10000000,
                "date": "2023-01-01",
                "investors": ["Venture Capital Firm"],
                "valuation": 50000000
            },
            "total_funding": 15000000,
            "valuation": 50000000,
            "revenue_estimate": 5000000,
            "revenue_growth_yoy": 100.0,
            "profitability_status": "break-even",
            "burn_rate": None
        })
