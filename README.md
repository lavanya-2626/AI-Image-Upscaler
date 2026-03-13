# 🖼️ Image Morph

A web-based image conversion platform that allows users to upload images and convert them into optimized formats like WebP and SVG.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)

## ✨ Features

- **Fast Image Conversion**: Convert images quickly using Pillow and CairoSVG
- **Multiple Formats**: Support for WebP, SVG, PNG, and JPEG output
- **Web Optimization**: Reduce image size for better web performance
- **Cloud Storage**: Optional Cloudflare R2 integration for file storage
- **REST API**: Developer-friendly API for integration
- **Drag & Drop**: Easy file upload with drag and drop support
- **Conversion History**: Track and manage previous conversions
- **File Size Comparison**: See how much space you're saving

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI** - Modern, fast web framework
- **Pillow** - Image processing library
- **CairoSVG** - SVG conversion
- **SQLAlchemy** - Database ORM
- **Boto3** - AWS S3/R2 SDK

### Frontend
- **HTML5**
- **CSS3** (with CSS Variables)
- **Vanilla JavaScript**
- **Responsive Design**

### Storage
- **Cloudflare R2** (optional) - Cloud object storage
- **SQLite** - Local database for metadata

## 📁 Project Structure

```
image_morph/
│
├── backend/
│   ├── app.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── routes/
│   │   └── convert.py         # API routes for conversion
│   ├── services/
│   │   └── image_converter.py # Image processing logic
│   ├── storage/
│   │   └── r2_storage.py      # Cloudflare R2 integration
│   ├── models/
│   │   └── image_model.py     # Database models
│   └── database/
│       └── __init__.py        # Database configuration
│
├── frontend/
│   ├── index.html             # Main HTML page
│   ├── style.css              # Stylesheet
│   └── app.js                 # Frontend JavaScript
│
├── docker/
│   ├── Dockerfile             # Docker image definition
│   ├── docker-compose.yml     # Docker Compose configuration
│   └── nginx.conf             # Nginx configuration
│
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment variables
└── README.md                 # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- pip
- (Optional) Docker and Docker Compose
- (Optional) Cloudflare R2 account for cloud storage

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lavanya-2626/Image-morph.git
   cd Image-morph
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python -m backend.app
   ```

6. **Open in browser**
   ```
   http://localhost:8000
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   cd docker
   docker-compose up --build
   ```

2. **With Nginx (production setup)**
   ```bash
   cd docker
   docker-compose --profile with-nginx up --build
   ```

## 📖 API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload an image |
| POST | `/api/convert` | Convert uploaded image |
| GET | `/api/image/{id}` | Get converted image (preview) |
| GET | `/api/download/{id}` | Download converted image |
| GET | `/api/images` | List recent conversions |
| DELETE | `/api/image/{id}` | Delete an image |
| GET | `/api/info` | Get API information |
| GET | `/health` | Health check |

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./image_morph.db` |
| `R2_ENDPOINT_URL` | Cloudflare R2 endpoint | - |
| `R2_ACCESS_KEY_ID` | R2 access key | - |
| `R2_SECRET_ACCESS_KEY` | R2 secret key | - |
| `R2_BUCKET_NAME` | R2 bucket name | `image-morph` |
| `R2_PUBLIC_URL` | Public URL for R2 files | - |
| `APP_HOST` | Server host | `0.0.0.0` |
| `APP_PORT` | Server port | `8000` |
| `MAX_FILE_SIZE` | Max upload size (bytes) | `10485760` (10MB) |
| `SECRET_KEY` | Secret key for security | - |

### Cloudflare R2 Setup (Optional)

1. Create a Cloudflare R2 bucket
2. Generate API tokens with read/write permissions
3. Add the credentials to your `.env` file

## 🖼️ Supported Formats

### Input Formats
- JPG/JPEG
- PNG
- WebP
- BMP
- TIFF

### Output Formats
- **WebP** - Best for web, smaller file sizes
- **SVG** - Scalable vector graphics
- **PNG** - Lossless compression
- **JPEG** - Universal compatibility

## 🔒 Security

- File type validation
- File size limits
- CORS protection
- Input sanitization

## 🛣️ Roadmap

- [ ] Batch image conversion
- [ ] Image resizing options
- [ ] Compression quality slider
- [ ] User authentication
- [ ] Conversion analytics dashboard
- [ ] Queue processing with Celery/Redis

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Pillow](https://python-pillow.org/) - Python Imaging Library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [CairoSVG](https://cairosvg.org/) - SVG converter
- [Cloudflare R2](https://www.cloudflare.com/developer-platform/r2/) - Object storage

---

Made with ❤️ for web developers and designers
