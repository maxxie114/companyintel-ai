from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import init_neo4j, close_neo4j
from app.core.cache import init_redis, close_redis
from app.api import routes, websocket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting CompanyIntel API...")
    await init_neo4j()
    await init_redis()
    logger.info("All services initialized")
    yield
    # Shutdown
    logger.info("Shutting down...")
    await close_neo4j()
    await close_redis()

app = FastAPI(
    title="CompanyIntel API",
    version="1.0.0",
    description="Complete Company Intelligence Platform",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(routes.router, prefix="/api")
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {
        "message": "CompanyIntel API",
        "version": "1.0.0",
        "docs": "/docs"
    }
