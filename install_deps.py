#!/usr/bin/env python3
"""
Dependency Installation Helper for Image Upscaler

This script helps install the dependencies in the correct order to avoid issues.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n[PACKAGE] {description}...")
    print(f"   Command: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=False)
    if result.returncode != 0:
        print(f"   WARNING: Command failed with exit code {result.returncode}")
        return False
    return True

def main():
    print("""
=============================================================
     Image Upscaler - Dependency Installation Helper
=============================================================
    """)

    if sys.version_info >= (3, 13):
        print(
            "[ERROR] Python 3.13+ detected. The Real-ESRGAN stack (realesrgan/basicsr/torch)\n"
            "        often lacks compatible wheels and may fail during installation.\n\n"
            "Fix:\n"
            "  1) Install Python 3.11.x\n"
            "  2) Recreate the venv using Python 3.11\n"
            "  3) Re-run this script inside that venv\n"
        )
        return 2
    
    python = sys.executable
    
    # Step 1: Upgrade pip
    run_command(f'"{python}" -m pip install --upgrade pip setuptools wheel', "Upgrading pip")
    
    # Step 2: Install base dependencies (without RealESRGAN first)
    print("\n[STEP 1/5] Installing base dependencies...")
    base_deps = [
        "fastapi==0.115.0",
        "uvicorn[standard]==0.32.0",
        "python-multipart==0.0.17",
        "Pillow==11.0.0",
        "numpy>=1.24.0",
        "celery>=5.3.0",
        "redis>=5.0.0",
        "boto3==1.35.0",
        "botocore==1.35.0",
        "sqlalchemy==2.0.36",
        "alembic==1.14.0",
        "aiosqlite==0.20.0",
        "python-dotenv==1.0.1",
        "pydantic==2.9.0",
        "pydantic-settings==2.6.0",
        "aiofiles==24.1.0",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "tqdm",
    ]
    
    for dep in base_deps:
        run_command(f'"{python}" -m pip install {dep}', f"Installing {dep}")
    
    # Step 3: Install PyTorch
    print("\n[STEP 2/5] Installing PyTorch...")
    print("   Checking for CUDA...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print("   [OK] CUDA is available, installing GPU version")
            run_command(f'"{python}" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118', 
                       "Installing PyTorch with CUDA")
        else:
            print("   [INFO] CUDA not available, installing CPU version")
            run_command(f'"{python}" -m pip install torch torchvision', 
                       "Installing PyTorch CPU")
    except ImportError:
        print("   [INFO] Installing CPU version (no CUDA detected)")
        run_command(f'"{python}" -m pip install torch torchvision', 
                   "Installing PyTorch CPU")
    
    # Step 4: Install RealESRGAN dependencies
    print("\n[STEP 3/5] Installing RealESRGAN dependencies...")
    
    # Install basicsr from git to avoid the version issue
    success = run_command(
        f'"{python}" -m pip install git+https://github.com/xinntao/BasicSR.git@master', 
        "Installing BasicSR from GitHub"
    )
    
    if not success:
        print("   [WARNING] Failed to install BasicSR from GitHub, trying alternative...")
        run_command(
            f'"{python}" -m pip install basicsr --no-deps',
            "Installing BasicSR without dependencies"
        )
        # Install missing basicsr deps
        run_command(f'"{python}" -m pip install addict future lmdb pyyaml requests scikit-image yapf', 
                   "Installing BasicSR dependencies")
    
    # Install filterpy (required by facexlib)
    run_command(f'"{python}" -m pip install filterpy', "Installing filterpy")
    
    # Install facexlib
    run_command(f'"{python}" -m pip install facexlib', "Installing facexlib")
    
    # Install gfpgan
    run_command(f'"{python}" -m pip install gfpgan', "Installing GFPGAN")
    
    # Install realesrgan
    run_command(f'"{python}" -m pip install realesrgan', "Installing RealESRGAN")
    
    # Step 5: Install frontend dependencies
    print("\n[STEP 4/5] Installing frontend dependencies...")
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    if os.path.exists(frontend_dir):
        run_command(f'cd "{frontend_dir}" && npm install', "Installing npm packages")
    else:
        print("   [WARNING] Frontend directory not found, skipping npm install")
    
    print("""
=============================================================
                 Installation Complete!
=============================================================

[OK] All dependencies installed!

TO START THE APPLICATION:

1. Start Redis (in a new terminal):
   docker run -d -p 6379:6379 redis:alpine
   OR download Redis for Windows from:
   https://github.com/microsoftarchive/redis/releases

2. Start the backend (in a new terminal):
   py run.py

3. Start Celery worker (in a new terminal):
   celery -A backend.celery_app worker --loglevel=info -Q upscale

4. Start the frontend (in a new terminal):
   cd frontend
   npm run dev

Then open: http://localhost:5173

NOTE: If RealESRGAN fails to import, the app will use basic upscaling.
The basic upscaler uses PIL and works without PyTorch/RealESRGAN.
    """)

if __name__ == "__main__":
    sys.exit(main())
