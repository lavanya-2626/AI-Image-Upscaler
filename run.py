#!/usr/bin/env python3
"""
Image Upscaler - Startup Script

This script provides an easy way to start the Image Upscaler application.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_redis():
    """Check if Redis is running."""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 6379))
        sock.close()
        return result == 0
    except:
        return False

def print_banner():
    """Print startup banner."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║    ✨  Image Upscaler - AI Powered Enhancement  ✨       ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    import uvicorn
    from backend.config import settings
    
    print_banner()
    
    # Create necessary directories
    for dir_name in ['uploads', 'results', 'models']:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"  📁 {dir_name}/ directory ready")
    
    # Check Redis
    if check_redis():
        print("  ✅ Redis is running (Celery queue available)")
    else:
        print("  ⚠️  Redis not detected - Queue processing will not work")
        print("     Install and start Redis for background processing:")
        print("     - Windows: https://github.com/microsoftarchive/redis/releases")
        print("     - Docker: docker run -d -p 6379:6379 redis:alpine")
    
    print(f"""
    🚀 Server Starting...
    
    📍 Local URL:   http://localhost:{settings.APP_PORT}
    📚 API Docs:    http://localhost:{settings.APP_PORT}/docs
    🔍 ReDoc:       http://localhost:{settings.APP_PORT}/redoc
    ❤️  Health:      http://localhost:{settings.APP_PORT}/health
    
    ⚡ Features:
       • Single & Bulk Image Upscaling
       • 2x & 4x Enhancement with RealESRGAN
       • Queue-based Processing with Celery
       • Before/After Comparison
    
    Press Ctrl+C to stop
    """)
    
    uvicorn.run(
        "backend.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
