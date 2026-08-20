"""
PlanGram Backend - Main Application Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
import logging
from dotenv import load_dotenv

# Import custom errors
from app.core.errors import PlanGramError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="PlanGram API",
    description="Interactive Spatial Decision Support for Rural Infrastructure Planning",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "PlanGram API",
        "version": "1.0.0",
        "status": "active",
        "tagline": "Explore. Simulate. Plan.",
        "description": "Interactive Spatial Decision Support for Rural Infrastructure Planning",
        "docs": "/api/docs",
        "phase": "Phase 12 - Production Ready"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "data_mode": os.getenv("DATA_MODE", "prototype"),
        "ai_provider": os.getenv("AI_PROVIDER", "none"),
        "version": "1.0.0"
    }


@app.get("/api/config")
async def get_config():
    """Get public configuration"""
    return {
        "data_mode": os.getenv("DATA_MODE", "prototype"),
        "distance_threshold_meters": int(os.getenv("DISTANCE_THRESHOLD_METERS", "500")),
        "max_upload_size_mb": int(os.getenv("MAX_UPLOAD_SIZE_MB", "100")),
        "supported_infrastructure_types": [
            "water",
            "waste",
            "health",
            "education",
            "public_toilet",
            "bus_stop"
        ]
    }


# Custom error handlers

@app.exception_handler(PlanGramError)
async def plangram_error_handler(request: Request, exc: PlanGramError):
    """Handle custom PlanGram errors"""
    logger.error(f"PlanGram Error: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    # Extract error details
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error['loc'])
        errors.append(f"{field}: {error['msg']}")
    
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters",
                "details": "; ".join(errors),
                "fields": exc.errors()
            }
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unexpected error: {type(exc).__name__} - {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "Please contact support",
                "type": type(exc).__name__
            }
        }
    )


# Import API routes
from app.api import villages, analysis, scenarios, constraints, candidates, optimization, ai

# Register API routes
app.include_router(villages.router, prefix="/api", tags=["villages"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(scenarios.router, prefix="/api", tags=["scenarios"])
app.include_router(constraints.router, prefix="/api", tags=["constraints"])
app.include_router(candidates.router, prefix="/api", tags=["candidates"])
app.include_router(optimization.router, prefix="/api", tags=["optimization"])
app.include_router(ai.router, tags=["ai"])

# Future API routes:
# app.include_router(data_ingestion.router, prefix="/api/data", tags=["data"])


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    reload = os.getenv("BACKEND_RELOAD", "true").lower() == "true"
    
    logger.info(f"Starting PlanGram API on {host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
