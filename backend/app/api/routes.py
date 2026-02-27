from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models import (
    AnalyzeRequest, AnalyzeResponse, CompanyResponse,
    CompanyListResponse, HealthResponse, GraphData
)
from app.core.cache import get_cached_company
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse, status_code=202)
async def analyze_company(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """Initiate company analysis"""
    session_id = str(uuid.uuid4())
    
    logger.info(f"Starting analysis for {request.company_name} (session: {session_id})")
    
    # Import here to avoid circular dependency
    from app.core.orchestrator import CompanyOrchestrator
    
    # Start background analysis
    orchestrator = CompanyOrchestrator(session_id)
    background_tasks.add_task(
        orchestrator.analyze,
        request.company_name,
        request.options.model_dump()
    )
    
    # Determine WebSocket URL based on environment
    ws_protocol = "wss" if "https" in str(request) else "ws"
    ws_url = f"{ws_protocol}://localhost:8000/ws/progress/{session_id}"
    
    return AnalyzeResponse(
        session_id=session_id,
        status="processing",
        estimated_time_seconds=30,
        websocket_url=ws_url
    )

@router.get("/company/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str):
    """Get company analysis results"""
    # Try cache first
    cached = await get_cached_company(company_id)
    if cached:
        logger.info(f"Returning cached data for {company_id}")
        return cached
    
    # If not in cache, return 404
    raise HTTPException(
        status_code=404,
        detail=f"Company {company_id} not found. Please analyze it first."
    )

@router.get("/graph/{company_id}", response_model=GraphData)
async def get_graph(company_id: str, depth: int = 2):
    """Get knowledge graph data"""
    from app.services.graph import GraphService
    
    try:
        graph_service = GraphService()
        graph_data = await graph_service.get_graph_data(company_id, depth)
        return graph_data
    except Exception as e:
        logger.error(f"Error getting graph for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies", response_model=CompanyListResponse)
async def list_companies(limit: int = 20, offset: int = 0):
    """List cached companies"""
    # For now, return empty list
    # In production, query Redis or database for all cached companies
    return CompanyListResponse(
        companies=[],
        total=0,
        limit=limit,
        offset=offset
    )

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from app.core.database import get_neo4j_driver
    from app.core.cache import redis_cache
    
    services = {
        "neo4j": "connected" if get_neo4j_driver() else "disconnected",
        "redis": "connected" if redis_cache.client else "disconnected",
        "yutori": "available",
        "tavily": "available"
    }
    
    return HealthResponse(
        status="healthy",
        services=services,
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )
