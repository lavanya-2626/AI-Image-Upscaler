"""
Unified Database Models for Image Morph

Includes models for:
- Image conversion (ImageRecord)
- Image upscaling (UpscaleJob, ProcessedImage)
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ImageRecord(Base):
    """Model for image format conversion records."""
    
    __tablename__ = "images"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_name = Column(String(255))
    original_format = Column(String(10))
    converted_format = Column(String(10))
    original_url = Column(Text)
    converted_url = Column(Text)
    file_size = Column(String(20))
    converted_size = Column(String(20))
    status = Column(String(20), default="uploaded")  # uploaded, converting, completed, failed
    upload_date = Column(DateTime, default=datetime.utcnow)
    conversion_date = Column(DateTime)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "original_name": self.original_name,
            "original_format": self.original_format,
            "converted_format": self.converted_format,
            "original_url": self.original_url,
            "converted_url": self.converted_url,
            "file_size": self.file_size,
            "converted_size": self.converted_size,
            "status": self.status,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "conversion_date": self.conversion_date.isoformat() if self.conversion_date else None,
        }


class UpscaleJob(Base):
    """Model for tracking image upscaling jobs."""
    
    __tablename__ = "upscale_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Job details
    job_type = Column(String(20), default="single")  # 'single' or 'bulk'
    status = Column(String(20), default="pending")  # 'pending', 'processing', 'completed', 'failed', 'partial'
    
    # Upscaling parameters
    scale = Column(Integer, default=2)  # 2 or 4
    
    # File info
    original_filename = Column(String(255))
    result_filename = Column(String(255))
    original_path = Column(Text)
    result_path = Column(Text)
    
    # Image dimensions
    original_width = Column(Integer)
    original_height = Column(Integer)
    upscaled_width = Column(Integer)
    upscaled_height = Column(Integer)
    
    # Processing info
    celery_task_id = Column(String(100))
    processing_time = Column(Float)  # in seconds
    
    # Bulk processing
    total_files = Column(Integer, default=1)
    processed_files = Column(Integer, default=0)
    failed_files = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "job_type": self.job_type,
            "status": self.status,
            "scale": self.scale,
            "original_filename": self.original_filename,
            "result_filename": self.result_filename,
            "original_dimensions": {
                "width": self.original_width,
                "height": self.original_height
            } if self.original_width else None,
            "upscaled_dimensions": {
                "width": self.upscaled_width,
                "height": self.upscaled_height
            } if self.upscaled_width else None,
            "processing_time": self.processing_time,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "error_message": self.error_message
        }


class ProcessedImage(Base):
    """Model for storing processed image metadata from upscaling."""
    
    __tablename__ = "processed_images"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Job reference
    job_id = Column(String(36))
    
    # File info
    original_path = Column(Text)
    result_path = Column(Text)
    original_filename = Column(String(255))
    result_filename = Column(String(255))
    
    # Image info
    original_size = Column(Integer)  # file size in bytes
    result_size = Column(Integer)
    original_width = Column(Integer)
    original_height = Column(Integer)
    result_width = Column(Integer)
    result_height = Column(Integer)
    
    # Processing info
    scale = Column(Integer)
    processing_time = Column(Float)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "original_filename": self.original_filename,
            "result_filename": self.result_filename,
            "original_size": self.original_size,
            "result_size": self.result_size,
            "original_dimensions": {
                "width": self.original_width,
                "height": self.original_height
            },
            "result_dimensions": {
                "width": self.result_width,
                "height": self.result_height
            },
            "scale": self.scale,
            "processing_time": self.processing_time
        }


# Status constants for upscaling
class UpscaleStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # For bulk jobs with some failures
