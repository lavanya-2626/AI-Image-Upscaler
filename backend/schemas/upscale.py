"""
Pydantic Schemas for Image Upscaler API

Request and response models for validation.
"""

from typing import Optional, List, Tuple
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class UpscaleScale(int, Enum):
    """Supported upscaling scales."""
    X2 = 2
    X4 = 4


class JobType(str, Enum):
    """Job types."""
    SINGLE = "single"
    BULK = "bulk"


class JobStatus(str, Enum):
    """Job statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class ImageDimensions(BaseModel):
    """Image dimensions model."""
    width: int
    height: int


# Request Schemas

class UpscaleSingleRequest(BaseModel):
    """Request model for single image upscaling."""
    scale: UpscaleScale = Field(default=UpscaleScale.X2, description="Upscaling factor (2x or 4x)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scale": 2
            }
        }


class UpscaleBulkRequest(BaseModel):
    """Request model for bulk image upscaling."""
    scale: UpscaleScale = Field(default=UpscaleScale.X2, description="Upscaling factor (2x or 4x)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scale": 4
            }
        }


class CreateJobResponse(BaseModel):
    """Response when creating a new job."""
    job_id: str
    task_id: str
    status: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": "abc123",
                "status": "pending",
                "message": "Upscaling job queued successfully"
            }
        }


class UpscaleResult(BaseModel):
    """Single upscaling result."""
    success: bool
    input_path: str
    output_path: Optional[str] = None
    original_size: Optional[Tuple[int, int]] = None
    upscaled_size: Optional[Tuple[int, int]] = None
    error: Optional[str] = None


class JobStatusResponse(BaseModel):
    """Response for job status query."""
    job_id: str
    status: JobStatus
    job_type: JobType
    scale: int
    progress: Optional[int] = Field(None, ge=0, le=100)
    current_step: Optional[str] = None
    result: Optional[UpscaleResult] = None
    results: Optional[List[UpscaleResult]] = None
    total_files: Optional[int] = None
    processed_files: Optional[int] = None
    failed_files: Optional[int] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "job_type": "single",
                "scale": 2,
                "progress": 45,
                "current_step": "Upscaling image with RealESRGAN..."
            }
        }


class JobListItem(BaseModel):
    """Job item in list response."""
    job_id: str
    status: JobStatus
    job_type: JobType
    scale: int
    original_filename: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    

class JobListResponse(BaseModel):
    """Response for job list query."""
    jobs: List[JobListItem]
    total: int


class CompareResponse(BaseModel):
    """Response for before/after comparison."""
    original_url: str
    upscaled_url: str
    original_dimensions: ImageDimensions
    upscaled_dimensions: ImageDimensions
    scale: int
    original_size: Optional[int] = None
    upscaled_size: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_url": "/api/download/original/123",
                "upscaled_url": "/api/download/upscaled/123",
                "original_dimensions": {"width": 512, "height": 512},
                "upscaled_dimensions": {"width": 1024, "height": 1024},
                "scale": 2,
                "original_size": 102400,
                "upscaled_size": 204800
            }
        }


class SystemStatusResponse(BaseModel):
    """System status response."""
    status: str
    queue_size: int
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    gpu_available: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "queue_size": 5,
                "active_jobs": 2,
                "completed_jobs": 150,
                "failed_jobs": 3,
                "gpu_available": True
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    celery_status: Optional[str] = None
