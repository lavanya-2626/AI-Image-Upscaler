"""
Image Morph - FastAPI Backend Application

A web-based image conversion platform supporting WebP and SVG formats.
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
from backend.routes.convert import router as convert_router

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
    logger.info("Starting up Image Morph API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Image Morph API...")


# Create FastAPI application
app = FastAPI(
    title="Image Morph API",
    description="Web-based image conversion platform supporting WebP and SVG formats",
    version="1.0.0",
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
app.include_router(convert_router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serve the frontend."""
    frontend_path = project_root / "frontend" / "index.html"
    if frontend_path.exists():
        with open(frontend_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Morph API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🖼️ Image Morph API</h1>
        <p>Welcome to the Image Morph API server.</p>
        <p>
            <a href="/docs">📚 API Documentation (Swagger UI)</a> |
            <a href="/redoc">📖 API Documentation (ReDoc)</a>
        </p>
        <p>The frontend should be available at <code>/frontend/index.html</code></p>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "image-morph-api",
        "version": "1.0.0"
    }


@app.get("/api/info")
async def api_info():
    """Get API information and supported formats."""
    from backend.services.image_converter import ImageConverter
    
    return {
        "name": "Image Morph API",
        "version": "1.0.0",
        "supported_input_formats": list(ImageConverter.ALLOWED_INPUT_FORMATS),
        "supported_output_formats": list(ImageConverter.ALLOWED_OUTPUT_FORMATS),
        "max_file_size": settings.MAX_FILE_SIZE,
        "features": [
            "JPG/JPEG/PNG to WebP conversion",
            "JPG/JPEG/PNG to SVG conversion",
            "Image optimization",
            "Cloud storage support (Cloudflare R2)"
        ]
    }


# Mount static files for frontend
frontend_dir = project_root / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
