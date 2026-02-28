from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request Models
class AnalyzeOptions(BaseModel):
    include_apis: bool = True
    include_financials: bool = True
    include_competitors: bool = True
    include_team: bool = True
    include_news: bool = True
    include_graph: bool = True

class AnalyzeRequest(BaseModel):
    company_name: str
    options: AnalyzeOptions = AnalyzeOptions()

# Response Models
class AnalyzeResponse(BaseModel):
    session_id: str
    status: str = "processing"
    estimated_time_seconds: int = 30
    websocket_url: str

class CompanyOverview(BaseModel):
    name: str
    slug: str
    description: str
    founded_year: Optional[int] = None
    headquarters: str = ""
    employee_count: str = ""
    website: str = ""
    logo_url: str = ""
    industry: List[str] = []
    mission: str = ""
    status: str = "private"

class Product(BaseModel):
    name: str
    description: str = ""
    category: str
    launch_date: Optional[str] = None

    @field_validator('name', 'description', 'category', mode='before')
    @classmethod
    def coerce_none_str(cls, v):
        return v if v is not None else ""

class APIEndpoint(BaseModel):
    path: str
    method: str
    description: str = ""
    category: str
    authentication_required: bool = True

    @field_validator('path', 'method', 'description', 'category', mode='before')
    @classmethod
    def coerce_none_str(cls, v):
        return v if v is not None else ""

class PricingTier(BaseModel):
    name: str
    price: str = ""
    features: List[str] = []
    target_audience: str = ""

    @field_validator('name', 'price', 'target_audience', mode='before')
    @classmethod
    def coerce_none_str(cls, v):
        return v if v is not None else ""

    @field_validator('features', mode='before')
    @classmethod
    def coerce_none_list(cls, v):
        return v if v is not None else []

class ProductsAPIs(BaseModel):
    products: List[Product] = []
    apis: List[APIEndpoint] = []
    documentation_quality: float = 0.0
    sdk_languages: List[str] = []
    pricing: List[PricingTier] = []

class Competitor(BaseModel):
    name: str
    slug: str
    relationship: str = "direct"
    strengths: List[str] = []
    weaknesses: List[str] = []
    market_overlap_percent: float = 0.0

class MarketIntelligence(BaseModel):
    competitors: List[Competitor] = []
    market_position: str = ""
    market_share_percent: Optional[float] = None
    niche: str = ""
    differentiation: List[str] = []
    target_market: List[str] = []

class FundingRound(BaseModel):
    round: str
    amount: float
    date: str
    investors: List[str]
    valuation: float

class Financials(BaseModel):
    status: str = "private"
    stock_symbol: Optional[str] = None
    stock_price: Optional[float] = None
    market_cap: Optional[float] = None
    last_funding_round: Optional[FundingRound] = None
    total_funding: Optional[float] = None
    valuation: Optional[float] = None
    revenue_estimate: Optional[float] = None
    revenue_growth_yoy: Optional[float] = None
    profitability_status: str = "unknown"
    burn_rate: Optional[str] = None

class Leader(BaseModel):
    name: str
    title: str
    background: str = ""
    linkedin_url: Optional[str] = None
    photo_url: Optional[str] = None

class TeamCulture(BaseModel):
    leadership: List[Leader] = []
    tech_stack: List[str] = []
    culture_signals: List[str] = []
    work_model: str = "hybrid"
    open_positions_count: int = 0
    hiring_focus: List[str] = []

class NewsArticle(BaseModel):
    title: str
    url: str
    source: str
    published_date: str
    sentiment: float
    summary: str
    topics: List[str] = []

class SentimentPoint(BaseModel):
    date: str
    sentiment: float
    event: Optional[str] = None

class ReviewSummary(BaseModel):
    average_rating: float
    review_count: int
    pros: List[str]
    cons: List[str]
    sources: List[str]

class NewsSentiment(BaseModel):
    overall_sentiment: float = 0.0
    sentiment_label: str = "neutral"
    recent_news: List[NewsArticle] = []
    sentiment_timeline: List[SentimentPoint] = []
    topics: List[str] = []
    customer_reviews: Optional[ReviewSummary] = None

class CompanyData(BaseModel):
    overview: CompanyOverview
    products_apis: ProductsAPIs
    market_intelligence: MarketIntelligence
    financials: Financials
    team_culture: TeamCulture
    news_sentiment: NewsSentiment

class CompanyMetadata(BaseModel):
    sources_count: int
    confidence_score: float
    last_updated: str

class CompanyResponse(BaseModel):
    id: str
    company_name: str
    slug: str
    analyzed_at: str
    status: str
    data: CompanyData
    metadata: CompanyMetadata

class GraphNode(BaseModel):
    id: str
    label: str
    properties: Dict[str, Any]
    x: Optional[float] = None
    y: Optional[float] = None

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    properties: Dict[str, Any] = {}

class GraphMetadata(BaseModel):
    node_count: int
    edge_count: int
    generated_at: str

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: GraphMetadata

class ProgressMessage(BaseModel):
    type: str
    session_id: str
    stage: str
    progress: float
    message: str
    timestamp: str

class CompanyListItem(BaseModel):
    id: str
    name: str
    slug: str
    logo_url: str
    analyzed_at: str
    status: str

class CompanyListResponse(BaseModel):
    companies: List[CompanyListItem]
    total: int
    limit: int
    offset: int

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    version: str
    timestamp: str
