#!/usr/bin/env python3
"""
Image Morph - Startup Script

This script provides an easy way to start the Image Morph application.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    import uvicorn
    from backend.config import settings
    
    print("""
    Image Morph - Starting Server
    
    URL: http://{}:{}
    API Docs: http://{}:{}/docs
    Health: http://{}:{}/health
    
    Press Ctrl+C to stop
    """.format(settings.APP_HOST, settings.APP_PORT, 
               settings.APP_HOST, settings.APP_PORT,
               settings.APP_HOST, settings.APP_PORT))
    
    uvicorn.run(
        "backend.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
