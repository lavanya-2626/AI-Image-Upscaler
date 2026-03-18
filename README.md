# Image Morph

A modern, all-in-one web-based image processing platform powered by FastAPI and React. Transform your images with AI-powered upscaling, intelligent format conversion, and batch processing capabilities.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)

## Features

### Core Features

#### Image Format Conversion
- **Smart Format Conversion**: Convert between WebP, PNG, JPG, SVG formats
- **Quality Optimization**: Adjustable quality settings for lossy formats
- **Size Reduction**: Automatic optimization to reduce file sizes
- **Bulk Conversion**: Process multiple images simultaneously

#### AI-Powered Upscaling (Optional)
- **RealESRGAN Models**: State-of-the-art deep learning for image enhancement
- **Multiple Scales**: Choose between 2x and 4x upscaling
- **Single & Bulk Processing**: Upscale one image or process up to 20 images at once
- **Queue Processing**: Celery-based background processing for handling multiple jobs
- **Before/After Comparison**: Interactive slider to compare original and upscaled images

### Frontend Features (React)
- **Drag & Drop Upload**: Intuitive file upload with drag-and-drop support
- **Image Preview**: Preview images before processing
- **Real-time Progress**: Live progress tracking with status updates
- **Responsive Design**: Works on desktop and mobile devices
- **Modern Stack**: React 18 + Vite + Tailwind CSS

### Backend Features (FastAPI)
- **Modular Services**: Separate services for conversion and upscaling
- **Job Queue**: Celery + Redis for reliable background processing
- **Unified Database**: Single SQLite database for all operations
- **REST API**: Full-featured API with Swagger documentation
- **Cloud Ready**: Optional Cloudflare R2 storage integration

## Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Database ORM with unified models
- **Celery** - Distributed task queue
- **Redis** - Message broker for Celery
- **Pillow** - Image processing
- **RealESRGAN** - AI upscaling models (PyTorch, optional)

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **react-dropzone** - File upload
- **react-compare-slider** - Before/after comparison
- **Axios** - HTTP client

### Storage
- **SQLite** - Local database (image_morph.db)
- **Cloudflare R2** (optional) - Cloud object storage

## Project Structure

```
image-morph/
│
├── backend/                   # FastAPI backend
│   ├── app.py                # Main application entry
│   ├── config.py             # Configuration settings
│   ├── celery_app.py         # Celery configuration
│   ├── database/             # Database setup
│   │   └── __init__.py
│   ├── routes/               # API routes
│   │   ├── convert.py        # Image conversion endpoints
│   │   └── upscale.py        # AI upscaling endpoints
│   ├── services/             # Business logic
│   │   ├── image_converter.py # Image format conversion
│   │   ├── upscaler.py       # RealESRGAN integration
│   │   └── upscaler_simple.py # Basic upscaling fallback
│   ├── tasks/                # Celery background tasks
│   │   └── upscale_tasks.py
│   ├── models/               # Database models
│   │   └── image_model.py    # Unified models (ImageRecord, UpscaleJob, ProcessedImage)
│   ├── schemas/              # Pydantic schemas
│   │   └── upscale.py
│   └── storage/              # Storage utilities
│       └── r2_storage.py     # Cloudflare R2 integration
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.jsx           # Main app component
│   │   ├── components/       # React components
│   │   │   ├── Header.jsx
│   │   │   ├── UploadZone.jsx
│   │   │   ├── ScaleSelector.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   ├── ImageComparison.jsx
│   │   │   ├── BulkResults.jsx
│   │   │   └── JobHistory.jsx
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useUpscale.js
│   │   │   └── useJobHistory.js
│   │   └── services/
│   │       └── api.js        # API client
│   ├── package.json
│   └── vite.config.js
│
├── docker/                    # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── ai/                        # AI coding rules and guidelines
│   └── ai/
│       ├── master_prompt.md
│       ├── coding_rules.md
│       ├── architecture_rules.md
│       ├── security_rules.md
│       └── testing_rules.md
│
├── uploads/                   # Uploaded images (created at runtime)
├── results/                   # Processed images (created at runtime)
├── models/                    # AI models (downloaded automatically)
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── run.py                     # Startup script
├── install_deps.py            # Automated dependency installer
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm
- Redis (for queue processing)
- (Optional) NVIDIA GPU with CUDA for AI upscaling

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/image-morph.git
   cd image-morph
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   python -m pip install -r requirements.txt
   ```

4. **(Optional) Enable AI upscaling (Real-ESRGAN)**

   Recommended Python for the AI stack: **3.11.x** (newer versions may force source builds and fail).

   For automated installation:
   ```bash
   python install_deps.py
   ```

   For manual installation:
   ```bash
   # Install PyTorch first (CPU or CUDA version)
   pip install torch torchvision

   # Install BasicSR from GitHub (avoids version issues)
   pip install "basicsr @ git+https://github.com/xinntao/BasicSR.git@master"

   # Install AI upscaling packages
   pip install realesrgan facexlib gfpgan filterpy
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Start Redis** (for queue processing)
   
   **Docker (recommended):**
   ```bash
   docker run -d -p 6379:6379 --name redis redis:alpine
   ```
   
   **Windows:**
   - Download Redis from: https://github.com/microsoftarchive/redis/releases
   - Or use WSL: `sudo apt-get install redis-server && redis-server`
   
   **macOS/Linux:**
   ```bash
   redis-server
   ```

7. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

#### Option 1: Start all services separately

**Terminal 1 - Backend:**
```bash
python run.py
```

**Terminal 2 - Celery Worker:**
```bash
celery -A backend.celery_app worker --loglevel=info -Q upscale
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

#### Option 2: Use Docker Compose

```bash
cd docker
docker-compose up --build
```

### Access the Application

- **Frontend:** http://localhost:5173
- **API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc

## API Documentation

### Conversion Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload a single image |
| POST | `/api/upload/bulk` | Upload multiple images |
| POST | `/api/convert` | Convert image to specified format |
| GET | `/api/image/{id}` | Get converted image (preview) |
| GET | `/api/download/{id}` | Download converted image |
| GET | `/api/images` | List recent conversions |
| DELETE | `/api/image/{id}` | Delete an image record |

### Upscaling Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upscale/single` | Upload and upscale a single image |
| POST | `/api/upscale/bulk` | Upload and upscale multiple images |
| GET | `/api/upscale/status/{job_id}` | Get job status and progress |
| GET | `/api/upscale/jobs` | List recent jobs |
| GET | `/api/upscale/compare/{job_id}` | Get comparison data |
| GET | `/api/upscale/download/original/{job_id}` | Download original image |
| GET | `/api/upscale/download/result/{job_id}` | Download upscaled image |
| DELETE | `/api/upscale/job/{job_id}` | Delete a job |
| GET | `/api/upscale/system-status` | Get system status |

### Example: Convert an Image

```bash
# Upload image
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@image.jpg"

# Returns: { "id": "uuid", ... }

# Convert to WebP
curl -X POST "http://localhost:8000/api/convert" \
  -F "id=uuid-from-upload" \
  -F "format=webp" \
  -F "quality=85"
```

### Example: Upscale an Image

```bash
curl -X POST "http://localhost:8000/api/upscale/single" \
  -H "accept: application/json" \
  -F "file=@image.jpg" \
  -F "scale=4"
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "abc123",
  "status": "pending",
  "message": "Upscaling job queued successfully"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite database path | `sqlite:///./image_morph.db` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `APP_HOST` | Server host | `0.0.0.0` |
| `APP_PORT` | Server port | `8000` |
| `MAX_FILE_SIZE` | Max upload size (bytes) | `52428800` (50MB) |
| `MODELS_DIR` | Directory for AI models | `./models` |
| `RESULTS_DIR` | Directory for processed images | `./results` |
| `UPLOADS_DIR` | Directory for uploaded images | `./uploads` |
| `R2_*` | Cloudflare R2 credentials | (optional) |

### GPU Acceleration

The application automatically detects and uses CUDA if available. To check GPU status:

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Docker Deployment

### Using Docker Compose

```bash
cd docker
docker-compose up --build
```

### Services

- **API**: FastAPI backend
- **Worker**: Celery worker for processing
- **Redis**: Message broker
- **Frontend**: React dev server (or nginx for production)

## Notes

### Supported Formats

**Input:** JPEG, PNG, WebP, BMP, SVG  
**Output:** JPEG, PNG, WebP, SVG

### Performance

**Image Conversion:**
- Instant for most formats
- ~1-5 seconds for large files

**AI Upscaling (if enabled):**
- **CPU**: ~30-60 seconds per image (depending on size)
- **GPU (CUDA)**: ~5-15 seconds per image
- **Max input dimension**: 4096px (configurable)

### First Run (AI Upscaling)

On the first run with AI upscaling enabled, RealESRGAN models will be automatically downloaded (~60MB for 2x, ~64MB for 4x). This may take a few minutes depending on your internet connection.

## Security

- File type validation
- File size limits
- CORS protection
- Input sanitization
- Secure file storage

## Roadmap

- [ ] User authentication and accounts
- [ ] Advanced upscaling options (denoise, face enhance)
- [ ] Custom model selection
- [ ] Batch download as ZIP
- [ ] Webhook notifications
- [ ] Progressive Web App (PWA)
- [ ] Dark/Light theme toggle
- [ ] Image watermarking

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- [RealESRGAN](https://github.com/xinntao/Real-ESRGAN) - AI upscaling models
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Celery](https://docs.celeryq.dev/) - Distributed task queue
- [React](https://react.dev/) - Frontend library
- [Pillow](https://python-pillow.org/) - Image processing

---

Made with love using FastAPI and React
