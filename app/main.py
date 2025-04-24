# app/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, HTTPException, Depends

# app/api/routers/analyzer.py
from app.api.routers import analyzer
from app.core.security import setup_security
from app.config.Settings import settings
from app.utils.logging import logger

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup security
setup_security(app)

# Create the router
router = APIRouter(
    prefix="/analyze",
    tags=["analyzer"]
)

# Include routers
app.include_router(analyzer.router, prefix="/api", tags=["analyzer"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Add startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME}")