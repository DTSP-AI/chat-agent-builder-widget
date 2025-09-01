import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import chat, admin, leads
from .deps import get_db_pool
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Agentic Widget API...")
    
    # Initialize database pool
    await get_db_pool()
    logger.info("Database pool initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agentic Widget API...")

app = FastAPI(
    title="Agentic Widget API",
    description="Multi-tenant chat widget with LangGraph agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin.router)
app.include_router(leads.router)
app.include_router(chat.router)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "agentic-widget-api"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Agentic Widget API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)