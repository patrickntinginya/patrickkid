"""
Shambani Link - Main Application Entry Point
FastAPI Backend Configuration
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers and utilities
from app.core.database import engine, Base
from app.core.redis_client import redis_client
from app.core.elasticsearch_client import es_client

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events
    """
    # Startup
    logger.info("🚀 Shambani Link Backend Starting...")
    try:
        # Test Redis connection
        redis_client.ping()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
    
    try:
        # Test Elasticsearch connection
        es_client.client.info()
        logger.info("✅ Elasticsearch connected")
    except Exception as e:
        logger.error(f"❌ Elasticsearch connection failed: {e}")
    
    logger.info("✅ Shambani Link Backend Ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shambani Link Backend Shutting Down...")
    redis_client.close()
    logger.info("✅ Shambani Link Backend Stopped")

# Initialize FastAPI app
app = FastAPI(
    title="Shambani Link API",
    description="Digital Agricultural Ecosystem Platform for East Africa",
    version="4.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "4.0.0"
    }

# Status Endpoint
@app.get("/status")
async def status():
    """Application status endpoint"""
    return {
        "name": "Shambani Link",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat()
    }

# API v1 Routes
@app.get("/api/v1")
async def api_info():
    """API Information"""
    return {
        "name": "Shambani Link API",
        "version": "1.0.0",
        "description": "Digital Agricultural Ecosystem Platform",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "docs": "/api/docs"
        }
    }

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle global exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )