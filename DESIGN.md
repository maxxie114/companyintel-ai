# Complete Company Intelligence Platform - Technical Design Document

**Project Name:** CompanyIntel  
**Hackathon:** Autonomous Agents Hackathon 2026  
**Build Time:** 4 hours (MVP) + 1-2 hours (Extensions)  
**Team Structure:** 2-3 developers (Frontend + Backend)

## Hackathon Requirements Compliance

✅ **Use at least 3 sponsor tools** (MVP uses 5+):
- Yutori (Research, Browsing, Scouting APIs)
- Neo4j (Knowledge graph database)
- Tavily (Web search for news/data)
- OpenAI (Analysis and sentiment)
- Render (Deployment - 2+ features required)

✅ **Render Track Requirements** (Must use 2+ Render features):
1. **Web Service** - FastAPI backend deployment
2. **Background Workers** - Async company analysis processing
3. **Cron Jobs** - Scheduled data refresh for cached companies
4. **PostgreSQL** - Historical analysis storage
5. **Redis** - Caching layer

✅ **Yutori Track** - Uses all 3 Yutori APIs uniquely:
- Research API: Deep company intelligence gathering
- Browsing API: API documentation extraction
- Scouting API: Continuous competitor monitoring

✅ **Neo4j Track** - Advanced graph capabilities:
- Multi-entity relationship mapping
- Graph-based competitor analysis
- Visual knowledge graph exploration  

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [MVP Implementation (Hours 1-4)](#mvp-implementation)
4. [Step 2: Modulate Integration (Hour 5)](#step-2-modulate-integration)
5. [Step 3: Fastino Labs Integration (Hour 6)](#step-3-fastino-labs-integration)
6. [API Contract (CRITICAL - READ FIRST)](#api-contract)
7. [Backend Specification](#backend-specification)
8. [Frontend Specification](#frontend-specification)
9. [Data Models](#data-models)
10. [Integration Checklist](#integration-checklist)
11. [Deployment Guide](#deployment-guide)

---

## Project Overview

### What We're Building

A comprehensive company intelligence platform that provides:
- Complete company profiles with 6 data categories
- API documentation and endpoint catalog
- Competitive analysis and market positioning
- Financial metrics and funding history
- Team and culture intelligence
- News sentiment analysis
- Interactive Neo4j knowledge graph

### Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- Neo4j Aura (graph database)
- Redis (caching)
- PostgreSQL (optional, for historical data)

**Frontend:**
- React 18 with TypeScript
- Material-UI (MUI) or Chakra UI
- React Query (data fetching)
- Recharts (charts/graphs)
- React Force Graph (Neo4j visualization)

**External APIs:**
- Yutori (Research, Browsing, Scouting)
- Tavily (search)
- OpenAI (analysis)
- Alpha Vantage or Yahoo Finance (financial data)

**Deployment:**
- Render Web Service (FastAPI backend)
- Render Background Workers (async processing)
- Render Cron Jobs (scheduled updates)
- Render PostgreSQL (historical data)
- Render Redis (caching)
- Render Static Site (React frontend)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  React + TypeScript + Material-UI + React Query             │
│                                                              │
│  Components:                                                 │
│  - CompanySearch (input)                                    │
│  - Dashboard (6 tabs)                                       │
│  - KnowledgeGraph (Neo4j viz)                              │
│  - LoadingProgress (real-time updates)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
                       │ WebSocket (progress updates)
┌──────────────────────┴──────────────────────────────────────┐
│                      BACKEND (FastAPI)                       │
│                                                              │
│  Endpoints:                                                  │
│  - POST /api/analyze                                        │
│  - GET  /api/company/{id}                                   │
│  - GET  /api/graph/{id}                                     │
│  - WS   /ws/progress/{session_id}                          │
│                                                              │
│  Services:                                                   │
│  - ResearchService (Yutori Research API)                   │
│  - BrowsingService (Yutori Browsing API)                   │
│  - FinancialService (stock/funding data)                   │
│  - CompetitorService (market analysis)                     │
│  - SentimentService (news analysis)                        │
│  - GraphService (Neo4j operations)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
   │  Neo4j  │   │  Redis  │   │ Workers │
   │  Aura   │   │  Cache  │   │ (async) │
   └─────────┘   └─────────┘   └─────────┘
```

---


## API Contract (CRITICAL - READ FIRST)

### Base URL
```
Development: http://localhost:8000
Production: https://companyintel.onrender.com
```

### Authentication
```
X-API-Key: <your-api-key>  (optional for hackathon)
```

---

### 1. Analyze Company (Primary Endpoint)

**POST** `/api/analyze`

Initiates comprehensive company analysis. Returns immediately with session_id for progress tracking.

**Request Body:**
```json
{
  "company_name": "Stripe",
  "options": {
    "include_apis": true,
    "include_financials": true,
    "include_competitors": true,
    "include_team": true,
    "include_news": true,
    "include_graph": true
  }
}
```

**Response (202 Accepted):**
```json
{
  "session_id": "uuid-v4-string",
  "status": "processing",
  "estimated_time_seconds": 30,
  "websocket_url": "ws://localhost:8000/ws/progress/uuid-v4-string"
}
```

**Status Codes:**
- 202: Analysis started
- 400: Invalid request
- 429: Rate limit exceeded
- 500: Server error

---

### 2. Get Company Data

**GET** `/api/company/{company_id}`

Retrieves complete company analysis results.

**Path Parameters:**
- `company_id`: UUID or company slug (e.g., "stripe")

**Query Parameters:**
- `sections`: Comma-separated list (e.g., "overview,apis,financials")
- `format`: "json" | "summary" (default: "json")

**Response (200 OK):**
```json
{
  "id": "uuid-v4-string",
  "company_name": "Stripe",
  "slug": "stripe",
  "analyzed_at": "2026-02-27T10:30:00Z",
  "status": "completed",
  "data": {
    "overview": { /* Overview data */ },
    "products_apis": { /* API data */ },
    "market_intelligence": { /* Market data */ },
    "financials": { /* Financial data */ },
    "team_culture": { /* Team data */ },
    "news_sentiment": { /* News data */ }
  },
  "metadata": {
    "sources_count": 45,
    "confidence_score": 0.92,
    "last_updated": "2026-02-27T10:30:00Z"
  }
}
```

**Status Codes:**
- 200: Success
- 404: Company not found
- 500: Server error

---

### 3. Get Knowledge Graph

**GET** `/api/graph/{company_id}`

Returns Neo4j graph data for visualization.

**Path Parameters:**
- `company_id`: UUID or company slug

**Query Parameters:**
- `depth`: 1-3 (relationship depth, default: 2)
- `types`: Comma-separated node types to include

**Response (200 OK):**
```json
{
  "nodes": [
    {
      "id": "node-1",
      "label": "Company",
      "properties": {
        "name": "Stripe",
        "type": "company"
      }
    },
    {
      "id": "node-2",
      "label": "Product",
      "properties": {
        "name": "Stripe Payments",
        "type": "product"
      }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2",
      "label": "OFFERS",
      "properties": {
        "since": "2010"
      }
    }
  ],
  "metadata": {
    "node_count": 150,
    "edge_count": 320,
    "generated_at": "2026-02-27T10:30:00Z"
  }
}
```

---

### 4. WebSocket Progress Updates

**WS** `/ws/progress/{session_id}`

Real-time progress updates during analysis.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/progress/uuid-v4-string');
```

**Message Format:**
```json
{
  "type": "progress",
  "session_id": "uuid-v4-string",
  "stage": "researching_company",
  "progress": 0.35,
  "message": "Researching company overview...",
  "timestamp": "2026-02-27T10:30:15Z"
}
```

**Message Types:**
- `progress`: Progress update (0.0 - 1.0)
- `completed`: Analysis finished
- `error`: Error occurred
- `stage_complete`: Individual stage finished

**Stages:**
1. `researching_company` (0.0 - 0.2)
2. `extracting_apis` (0.2 - 0.4)
3. `analyzing_competitors` (0.4 - 0.6)
4. `gathering_financials` (0.6 - 0.7)
5. `analyzing_team` (0.7 - 0.8)
6. `processing_news` (0.8 - 0.9)
7. `building_graph` (0.9 - 1.0)

---

### 5. List Cached Companies

**GET** `/api/companies`

Returns list of pre-analyzed companies (for demo).

**Query Parameters:**
- `limit`: Number of results (default: 20)
- `offset`: Pagination offset (default: 0)

**Response (200 OK):**
```json
{
  "companies": [
    {
      "id": "uuid-1",
      "name": "Stripe",
      "slug": "stripe",
      "logo_url": "https://...",
      "analyzed_at": "2026-02-27T10:00:00Z",
      "status": "completed"
    }
  ],
  "total": 15,
  "limit": 20,
  "offset": 0
}
```

---

### 6. Health Check

**GET** `/api/health`

System health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "services": {
    "neo4j": "connected",
    "redis": "connected",
    "yutori": "available",
    "tavily": "available"
  },
  "version": "1.0.0",
  "timestamp": "2026-02-27T10:30:00Z"
}
```

---


## Data Models

### CompanyOverview
```typescript
interface CompanyOverview {
  name: string;
  slug: string;
  description: string;
  founded_year: number;
  headquarters: string;
  employee_count: string;  // e.g., "5000-10000"
  website: string;
  logo_url: string;
  industry: string[];
  mission: string;
  status: "public" | "private" | "acquired";
}
```

### ProductsAPIs
```typescript
interface ProductsAPIs {
  products: Product[];
  apis: APIEndpoint[];
  documentation_quality: number;  // 0-5 stars
  sdk_languages: string[];
  pricing: PricingTier[];
}

interface Product {
  name: string;
  description: string;
  category: string;
  launch_date?: string;
}

interface APIEndpoint {
  path: string;
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  description: string;
  category: string;
  authentication_required: boolean;
}

interface PricingTier {
  name: string;
  price: string;
  features: string[];
  target_audience: string;
}
```

### MarketIntelligence
```typescript
interface MarketIntelligence {
  competitors: Competitor[];
  market_position: string;
  market_share_percent?: number;
  niche: string;
  differentiation: string[];
  target_market: string[];
}

interface Competitor {
  name: string;
  slug: string;
  relationship: "direct" | "indirect";
  strengths: string[];
  weaknesses: string[];
  market_overlap_percent: number;
}
```

### Financials
```typescript
interface Financials {
  status: "public" | "private";
  
  // Public companies
  stock_symbol?: string;
  stock_price?: number;
  market_cap?: number;
  
  // Private companies
  last_funding_round?: FundingRound;
  total_funding?: number;
  valuation?: number;
  
  // Both
  revenue_estimate?: number;
  revenue_growth_yoy?: number;
  profitability_status: "profitable" | "break-even" | "burning";
  burn_rate?: string;
}

interface FundingRound {
  round: string;  // e.g., "Series C"
  amount: number;
  date: string;
  investors: string[];
  valuation: number;
}
```

### TeamCulture
```typescript
interface TeamCulture {
  leadership: Leader[];
  tech_stack: string[];
  culture_signals: string[];
  work_model: "remote" | "hybrid" | "office";
  open_positions_count: number;
  hiring_focus: string[];
}

interface Leader {
  name: string;
  title: string;
  background: string;
  linkedin_url?: string;
  photo_url?: string;
}
```

### NewsSentiment
```typescript
interface NewsSentiment {
  overall_sentiment: number;  // -1 to 1
  sentiment_label: "positive" | "neutral" | "negative";
  recent_news: NewsArticle[];
  sentiment_timeline: SentimentPoint[];
  topics: string[];
  customer_reviews: ReviewSummary;
}

interface NewsArticle {
  title: string;
  url: string;
  source: string;
  published_date: string;
  sentiment: number;
  summary: string;
  topics: string[];
}

interface SentimentPoint {
  date: string;
  sentiment: number;
  event?: string;
}

interface ReviewSummary {
  average_rating: number;
  review_count: number;
  pros: string[];
  cons: string[];
  sources: string[];
}
```

### GraphData
```typescript
interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: GraphMetadata;
}

interface GraphNode {
  id: string;
  label: string;
  properties: Record<string, any>;
  x?: number;  // For force-directed layout
  y?: number;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  properties: Record<string, any>;
}

interface GraphMetadata {
  node_count: number;
  edge_count: number;
  generated_at: string;
}
```

---


## Backend Specification

### Technology Stack
- **Framework:** FastAPI 0.109+
- **Python:** 3.11+
- **Database:** Neo4j Aura (graph), Redis (cache)
- **Async:** asyncio, httpx
- **Background Jobs:** FastAPI BackgroundTasks or Celery (if time permits)

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration and env vars
│   ├── models.py               # Pydantic models
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoints
│   │   └── websocket.py        # WebSocket handlers
│   ├── services/
│   │   ├── __init__.py
│   │   ├── research.py         # Yutori Research API
│   │   ├── browsing.py         # Yutori Browsing API
│   │   ├── financial.py        # Financial data
│   │   ├── competitor.py       # Competitor analysis
│   │   ├── sentiment.py        # News sentiment
│   │   └── graph.py            # Neo4j operations
│   ├── core/
│   │   ├── __init__.py
│   │   ├── cache.py            # Redis caching
│   │   ├── database.py         # Neo4j connection
│   │   └── orchestrator.py     # Main analysis orchestrator
│   └── utils/
│       ├── __init__.py
│       └── helpers.py          # Utility functions
├── requirements.txt
├── .env.example
└── README.md
```

### Core Dependencies
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.26.0
redis==5.0.1
neo4j==5.16.0
python-dotenv==1.0.0
websockets==12.0
```

### Environment Variables
```bash
# API Keys
YUTORI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here

# Neo4j
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Redis
REDIS_URL=redis://localhost:6379

# App Config
ENVIRONMENT=development
LOG_LEVEL=INFO
CACHE_TTL_SECONDS=3600
```

---

### Backend Implementation Guide

#### 1. Main Application (main.py)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.api import websocket
from app.core.database import init_neo4j
from app.core.cache import init_redis

app = FastAPI(
    title="CompanyIntel API",
    version="1.0.0",
    description="Complete Company Intelligence Platform"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup
@app.on_event("startup")
async def startup():
    await init_neo4j()
    await init_redis()

# Routes
app.include_router(routes.router, prefix="/api")
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {"message": "CompanyIntel API", "version": "1.0.0"}
```

#### 2. Configuration (config.py)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    yutori_api_key: str
    tavily_api_key: str
    openai_api_key: str
    alpha_vantage_api_key: str
    
    # Neo4j
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # App
    environment: str = "development"
    log_level: str = "INFO"
    cache_ttl_seconds: int = 3600
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 3. API Routes (api/routes.py)
```python
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models import AnalyzeRequest, AnalyzeResponse, CompanyResponse
from app.core.orchestrator import CompanyOrchestrator
from app.core.cache import get_cached_company, cache_company
import uuid

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse, status_code=202)
async def analyze_company(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """Initiate company analysis"""
    session_id = str(uuid.uuid4())
    
    # Start background analysis
    orchestrator = CompanyOrchestrator(session_id)
    background_tasks.add_task(
        orchestrator.analyze,
        request.company_name,
        request.options
    )
    
    return AnalyzeResponse(
        session_id=session_id,
        status="processing",
        estimated_time_seconds=30,
        websocket_url=f"ws://localhost:8000/ws/progress/{session_id}"
    )

@router.get("/company/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str):
    """Get company analysis results"""
    # Try cache first
    cached = await get_cached_company(company_id)
    if cached:
        return cached
    
    # Query Neo4j
    # ... implementation
    
    raise HTTPException(status_code=404, detail="Company not found")

@router.get("/graph/{company_id}")
async def get_graph(company_id: str, depth: int = 2):
    """Get knowledge graph data"""
    # Query Neo4j for graph
    # ... implementation
    pass

@router.get("/companies")
async def list_companies(limit: int = 20, offset: int = 0):
    """List cached companies"""
    # ... implementation
    pass

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "neo4j": "connected",
            "redis": "connected",
            "yutori": "available",
            "tavily": "available"
        },
        "version": "1.0.0"
    }
```

#### 4. WebSocket Handler (api/websocket.py)
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.cache import get_progress_updates
import asyncio

router = APIRouter()

@router.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """WebSocket for real-time progress updates"""
    await websocket.accept()
    
    try:
        while True:
            # Get progress from Redis
            progress = await get_progress_updates(session_id)
            
            if progress:
                await websocket.send_json(progress)
                
                # If completed, close connection
                if progress.get("type") == "completed":
                    break
            
            await asyncio.sleep(0.5)
    
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()
```

#### 5. Orchestrator (core/orchestrator.py)
```python
from app.services import (
    ResearchService,
    BrowsingService,
    FinancialService,
    CompetitorService,
    SentimentService,
    GraphService
)
from app.core.cache import update_progress, cache_company
import asyncio

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
        try:
            # Stage 1: Research company (0.0 - 0.2)
            await self.update_progress(0.0, "researching_company")
            overview = await self.research.get_company_overview(company_name)
            
            # Stage 2: Extract APIs (0.2 - 0.4)
            await self.update_progress(0.2, "extracting_apis")
            apis = await self.browsing.extract_api_docs(overview["website"])
            
            # Stage 3: Analyze competitors (0.4 - 0.6)
            await self.update_progress(0.4, "analyzing_competitors")
            competitors = await self.competitor.find_competitors(company_name)
            
            # Stage 4: Gather financials (0.6 - 0.7)
            await self.update_progress(0.6, "gathering_financials")
            financials = await self.financial.get_financial_data(company_name)
            
            # Stage 5: Analyze team (0.7 - 0.8)
            await self.update_progress(0.7, "analyzing_team")
            team = await self.browsing.extract_team_info(overview["website"])
            
            # Stage 6: Process news (0.8 - 0.9)
            await self.update_progress(0.8, "processing_news")
            news = await self.sentiment.analyze_news(company_name)
            
            # Stage 7: Build graph (0.9 - 1.0)
            await self.update_progress(0.9, "building_graph")
            await self.graph.build_knowledge_graph(
                overview, apis, competitors, financials, team, news
            )
            
            # Complete
            await self.update_progress(1.0, "completed")
            
            # Cache results
            result = {
                "overview": overview,
                "products_apis": apis,
                "market_intelligence": competitors,
                "financials": financials,
                "team_culture": team,
                "news_sentiment": news
            }
            await cache_company(company_name, result)
            
        except Exception as e:
            await self.update_progress(0, "error", str(e))
    
    async def update_progress(self, progress: float, stage: str, message: str = ""):
        """Update progress in Redis"""
        await update_progress(self.session_id, {
            "type": "progress" if progress < 1.0 else "completed",
            "session_id": self.session_id,
            "stage": stage,
            "progress": progress,
            "message": message or f"Processing {stage}...",
            "timestamp": datetime.utcnow().isoformat()
        })
```

#### 6. Services Implementation

**Research Service (services/research.py)**
```python
import httpx
from app.config import settings

class ResearchService:
    def __init__(self):
        self.api_key = settings.yutori_api_key
        self.base_url = "https://api.yutori.com/v1"
    
    async def get_company_overview(self, company_name: str) -> dict:
        """Use Yutori Research API to get company overview"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/research/tasks",
                headers={"X-API-Key": self.api_key},
                json={
                    "query": f"Comprehensive overview of {company_name}: "
                             f"description, founding year, headquarters, "
                             f"employee count, mission, industry"
                }
            )
            task_id = response.json()["task_id"]
            
            # Poll for results
            result = await self._poll_task(task_id)
            return self._parse_overview(result)
    
    async def _poll_task(self, task_id: str) -> dict:
        """Poll Yutori task until complete"""
        # Implementation
        pass
    
    def _parse_overview(self, raw_data: dict) -> dict:
        """Parse raw research data into CompanyOverview format"""
        # Implementation
        pass
```

**Browsing Service (services/browsing.py)**
```python
class BrowsingService:
    async def extract_api_docs(self, website: str) -> dict:
        """Use Yutori Browsing to extract API documentation"""
        # Navigate to /docs or /api
        # Extract endpoints, pricing, SDKs
        pass
    
    async def extract_team_info(self, website: str) -> dict:
        """Extract team and culture info from careers/about pages"""
        pass
```

**Financial Service (services/financial.py)**
```python
class FinancialService:
    async def get_financial_data(self, company_name: str) -> dict:
        """Get financial data from multiple sources"""
        # Try stock data first (Alpha Vantage)
        # Fall back to funding data (Crunchbase via Yutori)
        pass
```

**Competitor Service (services/competitor.py)**
```python
class CompetitorService:
    async def find_competitors(self, company_name: str) -> dict:
        """Identify and analyze competitors"""
        # Use Yutori Research + Tavily
        # Analyze market positioning
        pass
```

**Sentiment Service (services/sentiment.py)**
```python
class SentimentService:
    async def analyze_news(self, company_name: str) -> dict:
        """Analyze news sentiment"""
        # Use Tavily for news search
        # Use OpenAI for sentiment analysis
        pass
```

**Graph Service (services/graph.py)**
```python
from neo4j import AsyncGraphDatabase

class GraphService:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    
    async def build_knowledge_graph(self, *data):
        """Build Neo4j knowledge graph from all data"""
        async with self.driver.session() as session:
            # Create nodes and relationships
            pass
    
    async def get_graph_data(self, company_id: str, depth: int = 2):
        """Query graph for visualization"""
        pass
```

---

### Backend Development Priority

**Hour 1: Core Infrastructure**
1. Set up FastAPI project structure
2. Configure environment variables
3. Implement basic API endpoints (analyze, get_company, health)
4. Set up Neo4j and Redis connections
5. Test with mock data

**Hour 2: Services Implementation**
1. Implement ResearchService (Yutori Research API)
2. Implement BrowsingService (Yutori Browsing API)
3. Implement basic caching
4. Test end-to-end with one company

**Hour 3: Advanced Features**
1. Implement FinancialService
2. Implement CompetitorService
3. Implement SentimentService
4. Build GraphService for Neo4j

**Hour 4: Integration & Polish**
1. Implement WebSocket progress updates
2. Pre-cache 10-15 demo companies
3. Test all endpoints
4. Deploy to Render

---


## Frontend Specification

### Technology Stack
- **Framework:** React 18 with TypeScript
- **UI Library:** Material-UI (MUI) v5
- **State Management:** React Query (TanStack Query)
- **Routing:** React Router v6
- **Charts:** Recharts
- **Graph Viz:** React Force Graph
- **HTTP Client:** Axios
- **WebSocket:** native WebSocket API

### Project Structure
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── App.tsx
│   ├── index.tsx
│   ├── api/
│   │   ├── client.ts           # Axios instance
│   │   ├── endpoints.ts        # API endpoints
│   │   └── websocket.ts        # WebSocket client
│   ├── components/
│   │   ├── CompanySearch.tsx   # Search input
│   │   ├── LoadingProgress.tsx # Progress indicator
│   │   ├── Dashboard.tsx       # Main dashboard
│   │   ├── tabs/
│   │   │   ├── OverviewTab.tsx
│   │   │   ├── APIsTab.tsx
│   │   │   ├── MarketTab.tsx
│   │   │   ├── FinancialsTab.tsx
│   │   │   ├── TeamTab.tsx
│   │   │   └── NewsTab.tsx
│   │   └── KnowledgeGraph.tsx  # Neo4j visualization
│   ├── hooks/
│   │   ├── useCompanyAnalysis.ts
│   │   ├── useWebSocket.ts
│   │   └── useCompanyData.ts
│   ├── types/
│   │   └── index.ts            # TypeScript interfaces
│   ├── utils/
│   │   └── helpers.ts
│   └── theme.ts                # MUI theme
├── package.json
├── tsconfig.json
└── README.md
```

### Core Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@mui/material": "^5.15.0",
    "@mui/icons-material": "^5.15.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0",
    "react-force-graph-2d": "^1.25.0",
    "typescript": "^5.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

---

### Frontend Implementation Guide

#### 1. API Client (api/client.ts)
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use((config) => {
  // Add API key if needed
  return config;
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
```

#### 2. API Endpoints (api/endpoints.ts)
```typescript
import { apiClient } from './client';
import {
  AnalyzeRequest,
  AnalyzeResponse,
  CompanyResponse,
  GraphData,
  CompanyListResponse
} from '../types';

export const companyApi = {
  // Analyze company
  analyze: async (request: AnalyzeRequest): Promise<AnalyzeResponse> => {
    const { data } = await apiClient.post('/analyze', request);
    return data;
  },

  // Get company data
  getCompany: async (companyId: string): Promise<CompanyResponse> => {
    const { data } = await apiClient.get(`/company/${companyId}`);
    return data;
  },

  // Get graph data
  getGraph: async (companyId: string, depth: number = 2): Promise<GraphData> => {
    const { data } = await apiClient.get(`/graph/${companyId}`, {
      params: { depth }
    });
    return data;
  },

  // List companies
  listCompanies: async (limit: number = 20, offset: number = 0): Promise<CompanyListResponse> => {
    const { data } = await apiClient.get('/companies', {
      params: { limit, offset }
    });
    return data;
  },

  // Health check
  healthCheck: async () => {
    const { data } = await apiClient.get('/health');
    return data;
  }
};
```

#### 3. WebSocket Hook (hooks/useWebSocket.ts)
```typescript
import { useEffect, useState, useCallback } from 'react';

interface ProgressMessage {
  type: 'progress' | 'completed' | 'error';
  session_id: string;
  stage: string;
  progress: number;
  message: string;
  timestamp: string;
}

export const useWebSocket = (sessionId: string | null) => {
  const [progress, setProgress] = useState<ProgressMessage | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const wsUrl = `ws://localhost:8000/ws/progress/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      const data: ProgressMessage = JSON.parse(event.data);
      setProgress(data);
    };

    ws.onerror = (event) => {
      setError('WebSocket error occurred');
      console.error('WebSocket error:', event);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [sessionId]);

  return { progress, isConnected, error };
};
```

#### 4. Company Analysis Hook (hooks/useCompanyAnalysis.ts)
```typescript
import { useMutation, useQuery } from '@tanstack/react-query';
import { companyApi } from '../api/endpoints';
import { AnalyzeRequest } from '../types';

export const useCompanyAnalysis = () => {
  const analyzeMutation = useMutation({
    mutationFn: (request: AnalyzeRequest) => companyApi.analyze(request),
  });

  return {
    analyze: analyzeMutation.mutate,
    isAnalyzing: analyzeMutation.isPending,
    analyzeData: analyzeMutation.data,
    analyzeError: analyzeMutation.error,
  };
};

export const useCompanyData = (companyId: string | null) => {
  return useQuery({
    queryKey: ['company', companyId],
    queryFn: () => companyApi.getCompany(companyId!),
    enabled: !!companyId,
  });
};

export const useGraphData = (companyId: string | null) => {
  return useQuery({
    queryKey: ['graph', companyId],
    queryFn: () => companyApi.getGraph(companyId!),
    enabled: !!companyId,
  });
};
```

#### 5. Company Search Component (components/CompanySearch.tsx)
```typescript
import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Autocomplete
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useCompanyAnalysis } from '../hooks/useCompanyAnalysis';

interface CompanySearchProps {
  onAnalysisStart: (sessionId: string) => void;
}

const DEMO_COMPANIES = [
  'Stripe', 'OpenAI', 'Anthropic', 'Yutori', 'Neo4j',
  'Render', 'Shopify', 'Twilio', 'Vercel', 'Supabase'
];

export const CompanySearch: React.FC<CompanySearchProps> = ({ onAnalysisStart }) => {
  const [companyName, setCompanyName] = useState('');
  const { analyze, isAnalyzing } = useCompanyAnalysis();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName.trim()) return;

    analyze(
      {
        company_name: companyName,
        options: {
          include_apis: true,
          include_financials: true,
          include_competitors: true,
          include_team: true,
          include_news: true,
          include_graph: true,
        },
      },
      {
        onSuccess: (data) => {
          onAnalysisStart(data.session_id);
        },
      }
    );
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom align="center">
        Company Intelligence Platform
      </Typography>
      <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 3 }}>
        Enter any company name to get comprehensive intelligence
      </Typography>

      <Box component="form" onSubmit={handleSubmit}>
        <Autocomplete
          freeSolo
          options={DEMO_COMPANIES}
          value={companyName}
          onInputChange={(_, newValue) => setCompanyName(newValue)}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Company Name"
              placeholder="e.g., Stripe, OpenAI, Shopify"
              fullWidth
              disabled={isAnalyzing}
            />
          )}
        />

        <Button
          type="submit"
          variant="contained"
          size="large"
          fullWidth
          startIcon={<SearchIcon />}
          disabled={isAnalyzing || !companyName.trim()}
          sx={{ mt: 2 }}
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze Company'}
        </Button>
      </Box>
    </Paper>
  );
};
```

#### 6. Loading Progress Component (components/LoadingProgress.tsx)
```typescript
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import { useWebSocket } from '../hooks/useWebSocket';

interface LoadingProgressProps {
  sessionId: string;
  onComplete: (companyId: string) => void;
}

const STAGES = [
  { key: 'researching_company', label: 'Researching company overview' },
  { key: 'extracting_apis', label: 'Extracting API documentation' },
  { key: 'analyzing_competitors', label: 'Analyzing competitors' },
  { key: 'gathering_financials', label: 'Gathering financial data' },
  { key: 'analyzing_team', label: 'Analyzing team & culture' },
  { key: 'processing_news', label: 'Processing news & sentiment' },
  { key: 'building_graph', label: 'Building knowledge graph' },
];

export const LoadingProgress: React.FC<LoadingProgressProps> = ({
  sessionId,
  onComplete
}) => {
  const { progress, isConnected } = useWebSocket(sessionId);

  React.useEffect(() => {
    if (progress?.type === 'completed') {
      // Extract company ID from progress data and call onComplete
      onComplete(sessionId);
    }
  }, [progress, sessionId, onComplete]);

  const currentProgress = progress?.progress || 0;
  const currentStage = progress?.stage || '';

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Analyzing Company...
      </Typography>

      <Box sx={{ mb: 3 }}>
        <LinearProgress
          variant="determinate"
          value={currentProgress * 100}
          sx={{ height: 10, borderRadius: 5 }}
        />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {Math.round(currentProgress * 100)}% complete
        </Typography>
      </Box>

      <List>
        {STAGES.map((stage, index) => {
          const stageProgress = index / STAGES.length;
          const isComplete = currentProgress > stageProgress;
          const isCurrent = stage.key === currentStage;

          return (
            <ListItem key={stage.key}>
              <ListItemIcon>
                {isComplete ? (
                  <CheckCircleIcon color="success" />
                ) : (
                  <HourglassEmptyIcon color={isCurrent ? 'primary' : 'disabled'} />
                )}
              </ListItemIcon>
              <ListItemText
                primary={stage.label}
                primaryTypographyProps={{
                  color: isComplete ? 'success.main' : isCurrent ? 'primary' : 'text.secondary'
                }}
              />
              {isCurrent && <Chip label="In Progress" size="small" color="primary" />}
            </ListItem>
          );
        })}
      </List>

      {!isConnected && (
        <Typography variant="body2" color="error" sx={{ mt: 2 }}>
          Connection lost. Retrying...
        </Typography>
      )}
    </Paper>
  );
};
```

#### 7. Dashboard Component (components/Dashboard.tsx)
```typescript
import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  Button,
  Chip
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useCompanyData, useGraphData } from '../hooks/useCompanyData';
import { OverviewTab } from './tabs/OverviewTab';
import { APIsTab } from './tabs/APIsTab';
import { MarketTab } from './tabs/MarketTab';
import { FinancialsTab } from './tabs/FinancialsTab';
import { TeamTab } from './tabs/TeamTab';
import { NewsTab } from './tabs/NewsTab';
import { KnowledgeGraph } from './KnowledgeGraph';

interface DashboardProps {
  companyId: string;
  onNewSearch: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ companyId, onNewSearch }) => {
  const [activeTab, setActiveTab] = useState(0);
  const { data: companyData, isLoading, error } = useCompanyData(companyId);
  const { data: graphData } = useGraphData(companyId);

  if (isLoading) return <Typography>Loading...</Typography>;
  if (error) return <Typography color="error">Error loading data</Typography>;
  if (!companyData) return null;

  const tabs = [
    { label: 'Overview', component: <OverviewTab data={companyData.data.overview} /> },
    { label: 'Products & APIs', component: <APIsTab data={companyData.data.products_apis} /> },
    { label: 'Market Intelligence', component: <MarketTab data={companyData.data.market_intelligence} /> },
    { label: 'Financials', component: <FinancialsTab data={companyData.data.financials} /> },
    { label: 'Team & Culture', component: <TeamTab data={companyData.data.team_culture} /> },
    { label: 'News & Sentiment', component: <NewsTab data={companyData.data.news_sentiment} /> },
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h4">{companyData.company_name}</Typography>
            <Box display="flex" gap={1} mt={1}>
              <Chip
                label={`Analyzed ${new Date(companyData.analyzed_at).toLocaleDateString()}`}
                size="small"
              />
              <Chip
                label={`Confidence: ${Math.round(companyData.metadata.confidence_score * 100)}%`}
                size="small"
                color="success"
              />
            </Box>
          </Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={onNewSearch}
          >
            New Search
          </Button>
        </Box>
      </Paper>

      {/* Tabs */}
      <Paper elevation={2}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {tabs.map((tab, index) => (
            <Tab key={index} label={tab.label} />
          ))}
        </Tabs>

        <Box sx={{ p: 3 }}>
          {tabs[activeTab].component}
        </Box>
      </Paper>

      {/* Knowledge Graph */}
      {graphData && (
        <Paper elevation={2} sx={{ mt: 3, p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Knowledge Graph
          </Typography>
          <KnowledgeGraph data={graphData} />
        </Paper>
      )}
    </Box>
  );
};
```

#### 8. Tab Components (Example: tabs/OverviewTab.tsx)
```typescript
import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Avatar
} from '@mui/material';
import { CompanyOverview } from '../../types';

interface OverviewTabProps {
  data: CompanyOverview;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ data }) => {
  return (
    <Grid container spacing={3}>
      {/* Company Logo & Basic Info */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Avatar
                src={data.logo_url}
                alt={data.name}
                sx={{ width: 80, height: 80 }}
              />
              <Box>
                <Typography variant="h5">{data.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {data.description}
                </Typography>
                <Box display="flex" gap={1} mt={1}>
                  {data.industry.map((ind) => (
                    <Chip key={ind} label={ind} size="small" />
                  ))}
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Key Metrics */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">
              Founded
            </Typography>
            <Typography variant="h6">{data.founded_year}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">
              Employees
            </Typography>
            <Typography variant="h6">{data.employee_count}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">
              Headquarters
            </Typography>
            <Typography variant="h6">{data.headquarters}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">
              Status
            </Typography>
            <Chip
              label={data.status}
              color={data.status === 'public' ? 'success' : 'default'}
            />
          </CardContent>
        </Card>
      </Grid>

      {/* Mission */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Mission
            </Typography>
            <Typography variant="body1">{data.mission}</Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};
```

#### 9. Knowledge Graph Component (components/KnowledgeGraph.tsx)
```typescript
import React, { useRef, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { GraphData } from '../types';

interface KnowledgeGraphProps {
  data: GraphData;
}

export const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({ data }) => {
  const graphRef = useRef<any>();

  useEffect(() => {
    // Fit graph to view
    if (graphRef.current) {
      graphRef.current.zoomToFit(400);
    }
  }, [data]);

  return (
    <ForceGraph2D
      ref={graphRef}
      graphData={data}
      nodeLabel="properties.name"
      nodeColor={(node: any) => {
        const colors: Record<string, string> = {
          company: '#1976d2',
          product: '#2e7d32',
          competitor: '#d32f2f',
          person: '#f57c00',
          technology: '#7b1fa2',
          news: '#0288d1',
        };
        return colors[node.properties.type] || '#757575';
      }}
      linkColor={() => '#999'}
      linkWidth={2}
      nodeRelSize={6}
      onNodeClick={(node: any) => {
        console.log('Node clicked:', node);
        // Show node details in modal
      }}
      width={800}
      height={600}
    />
  );
};
```

#### 10. Main App Component (App.tsx)
```typescript
import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, CssBaseline, Container } from '@mui/material';
import { theme } from './theme';
import { CompanySearch } from './components/CompanySearch';
import { LoadingProgress } from './components/LoadingProgress';
import { Dashboard } from './components/Dashboard';

const queryClient = new QueryClient();

type AppState = 'search' | 'loading' | 'dashboard';

function App() {
  const [state, setState] = useState<AppState>('search');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [companyId, setCompanyId] = useState<string | null>(null);

  const handleAnalysisStart = (newSessionId: string) => {
    setSessionId(newSessionId);
    setState('loading');
  };

  const handleAnalysisComplete = (newCompanyId: string) => {
    setCompanyId(newCompanyId);
    setState('dashboard');
  };

  const handleNewSearch = () => {
    setState('search');
    setSessionId(null);
    setCompanyId(null);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container maxWidth="xl">
          {state === 'search' && (
            <CompanySearch onAnalysisStart={handleAnalysisStart} />
          )}
          {state === 'loading' && sessionId && (
            <LoadingProgress
              sessionId={sessionId}
              onComplete={handleAnalysisComplete}
            />
          )}
          {state === 'dashboard' && companyId && (
            <Dashboard
              companyId={companyId}
              onNewSearch={handleNewSearch}
            />
          )}
        </Container>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
```

---

### Frontend Development Priority

**Hour 1: Core Setup**
1. Set up React + TypeScript + Vite project
2. Install and configure dependencies
3. Create API client and endpoints
4. Implement basic routing and state management
5. Test API connection with backend

**Hour 2: Search & Loading**
1. Build CompanySearch component
2. Implement WebSocket hook
3. Build LoadingProgress component
4. Test end-to-end flow with backend

**Hour 3: Dashboard & Tabs**
1. Build Dashboard layout with tabs
2. Implement 3 core tabs (Overview, APIs, Market)
3. Add basic styling and responsiveness
4. Test with real data from backend

**Hour 4: Polish & Graph**
1. Implement remaining tabs (Financials, Team, News)
2. Build KnowledgeGraph component
3. Add error handling and loading states
4. Final styling and UX polish

---


## Integration Checklist

### Pre-Development (Do This First!)

- [ ] **Backend Team**: Set up FastAPI project with CORS enabled
- [ ] **Frontend Team**: Set up React project with TypeScript
- [ ] **Both Teams**: Agree on API base URL (use environment variables)
- [ ] **Both Teams**: Review and confirm API contract section
- [ ] **Both Teams**: Set up shared TypeScript types (copy from Data Models section)
- [ ] **Backend Team**: Create mock endpoints that return sample data
- [ ] **Frontend Team**: Test against mock endpoints before real implementation

### During Development

**Backend Checkpoints:**
- [ ] Hour 1: Mock endpoints working, frontend can call them
- [ ] Hour 2: Real Yutori integration working, test with Postman
- [ ] Hour 3: All services implemented, test each endpoint
- [ ] Hour 4: WebSocket working, pre-cache demo companies

**Frontend Checkpoints:**
- [ ] Hour 1: Can call backend health endpoint
- [ ] Hour 2: Search and WebSocket progress working
- [ ] Hour 3: Dashboard displays data from backend
- [ ] Hour 4: All tabs working, graph visualization complete

### Integration Testing

**Test These Flows:**
1. [ ] Search for company → Receive session_id
2. [ ] WebSocket connects and receives progress updates
3. [ ] Progress reaches 100% → Dashboard loads
4. [ ] All 6 tabs display correct data
5. [ ] Knowledge graph renders correctly
6. [ ] Error handling works (invalid company, API failures)
7. [ ] Cached companies load instantly

### Common Integration Issues & Solutions

**Issue 1: CORS Errors**
```python
# Backend: Add to main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issue 2: WebSocket Connection Fails**
```typescript
// Frontend: Check WebSocket URL format
const wsUrl = `ws://localhost:8000/ws/progress/${sessionId}`;
// NOT: http://localhost:8000/ws/...
```

**Issue 3: Type Mismatches**
- **Solution**: Use shared TypeScript interfaces
- Backend team: Generate TypeScript types from Pydantic models
- Frontend team: Keep types in sync with backend

**Issue 4: Async Timing Issues**
- **Solution**: Use proper loading states
- Frontend: Show loading spinner while waiting for data
- Backend: Return 202 Accepted immediately, process in background

**Issue 5: Data Format Differences**
- **Solution**: Agree on date format (ISO 8601)
- **Solution**: Agree on number formats (no strings for numbers)
- **Solution**: Use null for missing data, not empty strings

---

## Deployment Guide

### Backend Deployment (Render)

**1. Create render.yaml**
```yaml
services:
  - type: web
    name: companyintel-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: YUTORI_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: NEO4J_URI
        sync: false
      - key: NEO4J_USER
        sync: false
      - key: NEO4J_PASSWORD
        sync: false
      - key: REDIS_URL
        sync: false
```

**2. Deploy Steps**
1. Push code to GitHub
2. Connect Render to GitHub repo
3. Add environment variables in Render dashboard
4. Deploy!

**3. Set Up Redis**
- Add Redis instance in Render
- Copy REDIS_URL to environment variables

**4. Set Up Neo4j**
- Create free Neo4j Aura instance
- Copy connection details to environment variables

### Frontend Deployment (Render Static Site)

**1. Create render.yaml**
```yaml
services:
  - type: web
    name: companyintel-frontend
    env: static
    buildCommand: npm install && npm run build
    staticPublishPath: ./dist
    envVars:
      - key: VITE_API_URL
        value: https://companyintel-api.onrender.com
```

**2. Update vite.config.ts**
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

**3. Deploy Steps**
1. Push code to GitHub
2. Connect Render to GitHub repo
3. Set VITE_API_URL environment variable
4. Deploy!

---

## Demo Preparation

### Pre-Cache These Companies (Backend)

Run this script before the demo to cache 15 companies:

```python
# scripts/cache_companies.py
import asyncio
from app.core.orchestrator import CompanyOrchestrator

DEMO_COMPANIES = [
    "Stripe", "OpenAI", "Anthropic", "Yutori", "Neo4j",
    "Render", "Shopify", "Twilio", "Vercel", "Supabase",
    "Cloudflare", "Datadog", "MongoDB", "Snowflake", "Databricks"
]

async def cache_all():
    for company in DEMO_COMPANIES:
        print(f"Caching {company}...")
        orchestrator = CompanyOrchestrator(f"cache-{company}")
        await orchestrator.analyze(company, {
            "include_apis": True,
            "include_financials": True,
            "include_competitors": True,
            "include_team": True,
            "include_news": True,
            "include_graph": True,
        })
        print(f"✓ {company} cached")

if __name__ == "__main__":
    asyncio.run(cache_all())
```

### Demo Script

**1. Opening (30 seconds)**
- "We built a comprehensive company intelligence platform"
- "Enter any company, get everything: APIs, competitors, financials, team, news"
- "Watch this..."

**2. Live Demo (90 seconds)**
- Type "Stripe" in search
- Show real-time progress (7 stages)
- Dashboard appears with 6 tabs
- Click through tabs quickly:
  - Overview: Basic info
  - APIs: 200+ endpoints cataloged
  - Market: 5 competitors analyzed
  - Financials: $14B revenue, $50B valuation
  - Team: Leadership, tech stack
  - News: Sentiment timeline
- Show knowledge graph (zoom in on connections)

**3. Technical Explanation (45 seconds)**
- "Uses 3 Yutori APIs in parallel"
- "Neo4j stores 8 relationship types"
- "Deployed on Render with worker architecture"
- "Processes 8+ data sources in 30 seconds"

**4. Business Value (15 seconds)**
- "Saves 5+ hours per company research"
- "Serves sales, developers, investors, job seekers"
- "$500M+ market opportunity"

### Backup Plans

**If Live Demo Fails:**
1. Switch to pre-cached company (instant load)
2. Show video recording of working demo
3. Show static screenshots with narration

**If API Rate Limits Hit:**
- Use cached companies only
- Explain: "In production, we'd have higher limits"

**If Graph Doesn't Render:**
- Show data in table format
- Explain: "Graph shows these relationships visually"

---

## Performance Optimization

### Backend Optimizations

**1. Parallel API Calls**
```python
# Instead of sequential:
overview = await research.get_overview()
apis = await browsing.get_apis()

# Do parallel:
overview, apis = await asyncio.gather(
    research.get_overview(),
    browsing.get_apis()
)
```

**2. Aggressive Caching**
```python
# Cache for 1 hour
@cache(ttl=3600)
async def get_company_data(company_name: str):
    # ...
```

**3. Database Connection Pooling**
```python
# Neo4j connection pool
driver = AsyncGraphDatabase.driver(
    uri,
    auth=(user, password),
    max_connection_pool_size=50
)
```

### Frontend Optimizations

**1. Code Splitting**
```typescript
// Lazy load tabs
const APIsTab = lazy(() => import('./tabs/APIsTab'));
const MarketTab = lazy(() => import('./tabs/MarketTab'));
```

**2. Memoization**
```typescript
const MemoizedGraph = React.memo(KnowledgeGraph);
```

**3. Virtual Scrolling**
```typescript
// For large lists (e.g., API endpoints)
import { FixedSizeList } from 'react-window';
```

---

## Troubleshooting Guide

### Backend Issues

**Problem: Yutori API timeout**
- **Solution**: Increase timeout, add retry logic
- **Fallback**: Use cached data or mock data

**Problem: Neo4j connection fails**
- **Solution**: Check credentials, verify network access
- **Fallback**: Store data in PostgreSQL or JSON files

**Problem: Redis not available**
- **Solution**: Use in-memory dict for caching
- **Fallback**: No caching (slower but works)

### Frontend Issues

**Problem: WebSocket disconnects**
- **Solution**: Add reconnection logic
- **Fallback**: Poll REST endpoint for progress

**Problem: Graph rendering slow**
- **Solution**: Limit nodes to 100, add pagination
- **Fallback**: Show simplified graph or table view

**Problem: Mobile responsiveness**
- **Solution**: Use MUI's responsive breakpoints
- **Fallback**: Show message "Best viewed on desktop"

---

## Success Metrics

### Must Have (Minimum Viable Demo)
- [ ] Search works for at least 5 companies
- [ ] Progress indicator shows real-time updates
- [ ] Dashboard displays with 3+ tabs working
- [ ] Knowledge graph renders (even if simple)
- [ ] Deployed and accessible via URL

### Should Have (Competitive Demo)
- [ ] All 6 tabs working with real data
- [ ] Interactive knowledge graph with click handlers
- [ ] 10+ companies pre-cached
- [ ] Error handling and loading states
- [ ] Mobile-responsive design

### Nice to Have (Winning Demo)
- [ ] 15+ companies pre-cached
- [ ] Advanced graph interactions (zoom, filter)
- [ ] Export to PDF feature
- [ ] Comparison mode (2 companies side-by-side)
- [ ] Real-time monitoring via Scouting API

---

## Final Checklist

### 1 Hour Before Demo
- [ ] Test all pre-cached companies
- [ ] Verify all API keys are valid
- [ ] Check deployment is live
- [ ] Test on different browsers
- [ ] Prepare backup video/screenshots
- [ ] Practice 3-minute pitch

### During Demo
- [ ] Start with strongest cached company (Stripe)
- [ ] Have backup company ready (OpenAI)
- [ ] Keep browser dev tools closed
- [ ] Have Postman ready for API demo if needed
- [ ] Stay calm if something breaks

### After Demo
- [ ] Note any bugs or issues
- [ ] Collect judge feedback
- [ ] Celebrate! 🎉

---

## Team Coordination

### Communication Protocol

**Daily Standup (Even During Hackathon)**
- What did you complete?
- What are you working on now?
- Any blockers?

**Integration Points**
- Hour 1: Backend mock endpoints ready
- Hour 2: Frontend can call real endpoints
- Hour 3: Full integration working
- Hour 4: Polish and testing

**Shared Resources**
- API Contract (this document)
- Shared TypeScript types
- Environment variables
- Demo script

### Division of Labor

**Backend Developer(s):**
- API endpoints
- Service implementations
- Neo4j schema and queries
- Caching layer
- Deployment

**Frontend Developer(s):**
- React components
- API integration
- UI/UX design
- Graph visualization
- Responsive design

**Shared Responsibilities:**
- Testing integration
- Demo preparation
- Documentation
- Pitch presentation

---

## Conclusion

This design document provides everything needed to build the Complete Company Intelligence Platform in 4 hours. Key success factors:

1. **Follow the API contract** - No surprises during integration
2. **Use the priority lists** - Build core features first
3. **Test frequently** - Catch issues early
4. **Pre-cache demo data** - Ensure reliable demo
5. **Have fallbacks** - Plan for failures
6. **Communicate constantly** - Stay aligned

**Remember:** A working simple demo beats a broken complex one. Focus on core features first, add polish if time permits.

Good luck! 🚀

---

**Document Version:** 1.0  
**Last Updated:** February 27, 2026  
**Authors:** Hackathon Team  
**Status:** Ready for Implementation
