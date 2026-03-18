"""
Image Upscaler - FastAPI Backend Application

AI-powered image upscaling using RealESRGAN with queue processing.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import logging

from backend.config import settings
from backend.database import engine, Base
from backend.routes.upscale import router as upscale_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting up Image Upscaler API...")
    
    # Create upload and results directories
    upload_dir = project_root / "uploads"
    results_dir = project_root / "results"
    models_dir = project_root / "models"
    
    for dir_path in [upload_dir, results_dir, models_dir]:
        dir_path.mkdir(exist_ok=True)
        logger.info(f"Directory ready: {dir_path}")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Image Upscaler API...")


# Create FastAPI application
app = FastAPI(
    title="Image Upscaler API",
    description="AI-powered image upscaling using RealESRGAN with 2x and 4x options",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upscale_router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serve the frontend."""
    # Check if React build exists
    react_build_path = project_root / "frontend" / "dist" / "index.html"
    if react_build_path.exists():
        with open(react_build_path, "r", encoding="utf-8") as f:
            return f.read()
    
    # Fallback API landing page
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Upscaler API</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #fff;
            }
            .container { 
                max-width: 800px; 
                padding: 40px; 
                text-align: center;
            }
            h1 { 
                font-size: 3em; 
                margin-bottom: 10px;
                background: linear-gradient(45deg, #00d4ff, #7b2cbf);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .subtitle {
                font-size: 1.2em;
                color: #888;
                margin-bottom: 40px;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }
            .feature {
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            .feature h3 {
                color: #00d4ff;
                margin-bottom: 10px;
            }
            .links {
                margin-top: 40px;
            }
            .links a { 
                display: inline-block;
                color: #fff;
                text-decoration: none;
                padding: 12px 30px;
                margin: 10px;
                border-radius: 25px;
                background: linear-gradient(45deg, #00d4ff, #7b2cbf);
                transition: transform 0.2s;
            }
            .links a:hover {
                transform: translateY(-2px);
            }
            .status {
                margin-top: 30px;
                padding: 15px;
                background: rgba(0,212,255,0.1);
                border-radius: 10px;
                border: 1px solid rgba(0,212,255,0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✨ Image Upscaler API</h1>
            <p class="subtitle">AI-powered image enhancement with RealESRGAN</p>
            
            <div class="features">
                <div class="feature">
                    <h3>🎯 2x & 4x Upscaling</h3>
                    <p>Choose your desired enhancement level</p>
                </div>
                <div class="feature">
                    <h3>⚡ Queue Processing</h3>
                    <p>Celery-powered background tasks</p>
                </div>
                <div class="feature">
                    <h3>📦 Bulk Support</h3>
                    <p>Process multiple images at once</p>
                </div>
            </div>
            
            <div class="links">
                <a href="/docs">📚 API Docs (Swagger)</a>
                <a href="/redoc">📖 API Docs (ReDoc)</a>
            </div>
            
            <div class="status">
                🟢 API Server Running | Version 2.0.0
            </div>
        </div>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    import torch
    
    # Check Celery connection
    try:
        from backend.celery_app import celery_app
        inspector = celery_app.control.inspect()
        active_workers = inspector.active()
        celery_status = "connected" if active_workers is not None else "no workers"
    except Exception as e:
        celery_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "image-upscaler-api",
        "version": "2.0.0",
        "gpu_available": torch.cuda.is_available(),
        "celery_status": celery_status
    }


@app.get("/api/info")
async def api_info():
    """Get API information and supported features."""
    return {
        "name": "Image Upscaler API",
        "version": "2.0.0",
        "features": [
            "AI-powered image upscaling (RealESRGAN)",
            "2x and 4x upscaling options",
            "Single image processing",
            "Bulk image processing",
            "Before/after comparison",
            "Queue-based processing (Celery)",
            "Progress tracking",
            "HD image download"
        ],
        "supported_formats": {
            "input": ["JPEG", "PNG", "WebP", "BMP"],
            "output": ["Same as input"]
        },
        "max_file_size": settings.MAX_FILE_SIZE,
        "max_bulk_files": 20
    }


# Mount static files for frontend
frontend_dist = project_root / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
