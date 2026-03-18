"""
FastAPI Routes for Image Upscaling

API endpoints for single/bulk upscaling, status checks, and downloads.
"""

import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
import shutil
import logging

from backend.schemas.upscale import (
    UpscaleSingleRequest, UpscaleBulkRequest, CreateJobResponse,
    JobStatusResponse, JobListResponse, CompareResponse,
    SystemStatusResponse, HealthResponse, UpscaleResult
)
from backend.models import UpscaleJob, UpscaleStatus
from backend.database import SessionLocal
from backend.tasks.upscale_tasks import upscale_single, upscale_bulk
from backend.celery_app import get_task_status
from backend.services.upscaler import get_upscaler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upscale", tags=["upscale"])

# Directories - use absolute paths from project root
project_root = Path(__file__).parent.parent.parent
UPLOAD_DIR = project_root / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR = project_root / "results"
RESULT_DIR.mkdir(exist_ok=True)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@router.post("/single", response_model=CreateJobResponse)
async def upload_and_upscale_single(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Image file to upscale"),
    scale: int = Form(2, description="Upscaling factor (2 or 4)")
):
    """
    Upload and upscale a single image.
    
    - **file**: Image file (jpg, png, webp, bmp)
    - **scale**: Upscaling factor (2 or 4)
    
    Returns job ID and task ID for tracking progress.
    """
    # Validate scale
    if scale not in [2, 4]:
        raise HTTPException(status_code=400, detail="Scale must be 2 or 4")
    
    # Validate file extension
    ext = Path(file.filename).suffix.lower()
    allowed_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_exts)}"
        )
    
    # Generate unique ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_filename = f"{job_id}_{file.filename}"
    upload_path = UPLOAD_DIR / upload_filename
    
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")
    finally:
        file.file.close()
    
    # Create database entry
    db = get_db()
    try:
        job = UpscaleJob(
            id=job_id,
            job_type="single",
            status=UpscaleStatus.PENDING,
            scale=scale,
            original_filename=file.filename,
            original_path=str(upload_path)
        )
        db.add(job)
        db.commit()
    finally:
        db.close()
    
    # Queue Celery task (or process synchronously if Celery is not available)
    is_sync = False
    try:
        task = upscale_single.delay(
            image_path=str(upload_path),
            scale=scale,
            job_id=job_id
        )
        task_id = task.id
        message = "Upscaling job queued successfully"
        response_status = "pending"
    except Exception as e:
        logger.warning(f"Celery not available ({e}), processing synchronously")
        # Process synchronously if Celery is not available
        try:
            from backend.tasks.upscale_tasks import process_image_core
            result = process_image_core(str(upload_path), scale, job_id)
            task_id = "sync-" + job_id
            message = "Upscaling completed (synchronous mode)"
            is_sync = True
            response_status = "completed"
        except Exception as sync_error:
            logger.error(f"Synchronous processing failed: {sync_error}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {sync_error}")
    
    # Update job with task ID
    db = get_db()
    try:
        job = db.query(UpscaleJob).filter(UpscaleJob.id == job_id).first()
        if job:
            job.celery_task_id = task_id
            db.commit()
    finally:
        db.close()
    
    return CreateJobResponse(
        job_id=job_id,
        task_id=task_id,
        status=response_status,
        message=message
    )


@router.post("/bulk", response_model=CreateJobResponse)
async def upload_and_upscale_bulk(
    files: List[UploadFile] = File(..., description="Multiple image files to upscale"),
    scale: int = Form(2, description="Upscaling factor (2 or 4)")
):
    """
    Upload and upscale multiple images in bulk.
    
    - **files**: List of image files
    - **scale**: Upscaling factor (2 or 4)
    
    Returns job ID and task ID for tracking progress.
    """
    # Validate scale
    if scale not in [2, 4]:
        raise HTTPException(status_code=400, detail="Scale must be 2 or 4")
    
    # Validate file count
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 files allowed for bulk upload")
    
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Generate unique ID
    job_id = str(uuid.uuid4())
    
    # Save all files
    uploaded_paths = []
    allowed_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in allowed_exts:
            continue
        
        upload_filename = f"{job_id}_{file.filename}"
        upload_path = UPLOAD_DIR / upload_filename
        
        try:
            with open(upload_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_paths.append(str(upload_path))
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
        finally:
            file.file.close()
    
    if not uploaded_paths:
        raise HTTPException(status_code=400, detail="No valid image files uploaded")
    
    # Create database entry
    db = get_db()
    try:
        job = UpscaleJob(
            id=job_id,
            job_type="bulk",
            status=UpscaleStatus.PENDING,
            scale=scale,
            total_files=len(uploaded_paths),
            original_filename=f"{len(uploaded_paths)} files"
        )
        db.add(job)
        db.commit()
    finally:
        db.close()
    
    # Queue Celery task
    task = upscale_bulk.delay(
        image_paths=uploaded_paths,
        scale=scale,
        job_id=job_id
    )
    
    # Update job with task ID
    db = get_db()
    try:
        job = db.query(UpscaleJob).filter(UpscaleJob.id == job_id).first()
        if job:
            job.celery_task_id = task.id
            db.commit()
    finally:
        db.close()
    
    return CreateJobResponse(
        job_id=job_id,
        task_id=task.id,
        status="pending",
        message=f"Bulk upscaling job queued for {len(uploaded_paths)} files"
    )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of an upscaling job.
    
    Returns current status, progress, and results if completed.
    """
    db = get_db()
    try:
        job = db.query(UpscaleJob).filter(UpscaleJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        response = JobStatusResponse(
            job_id=job.id,
            status=job.status,
            job_type=job.job_type,
            scale=job.scale,
            total_files=job.total_files,
            processed_files=job.processed_files,
            failed_files=job.failed_files,
            processing_time=job.processing_time,
            error_message=job.error_message,
            created_at=job.created_at.isoformat() if job.created_at else None
        )
        
        # Get result from database if job is completed
        if job.status == "completed" and job.result_path:
            # Build result from database
            response.result = UpscaleResult(
                success=True,
                input_path=job.original_path,
                output_path=job.result_path,
                original_size=(job.original_width, job.original_height) if job.original_width else None,
                upscaled_size=(job.upscaled_width, job.upscaled_height) if job.upscaled_width else None
            )
        
        # Get Celery task status for progress (only for async tasks)
        if job.celery_task_id and not job.celery_task_id.startswith("sync-"):
            task_info = get_task_status(job.celery_task_id)
            
            if task_info.get("status") == "PROGRESS":
                meta = task_info.get("result", {})
                response.progress = meta.get("progress", 0)
                response.current_step = meta.get("status")
            elif task_info.get("status") == "SUCCESS":
                result = task_info.get("result", {})
                if job.job_type == "single" and result.get("success"):
                    response.result = UpscaleResult(
                        success=True,
                        input_path=result.get("input_path"),
                        output_path=result.get("output_path"),
                        original_size=result.get("original_size"),
                        upscaled_size=result.get("upscaled_size")
                    )
                elif job.job_type == "bulk":
                    response.results = [
                        UpscaleResult(**r) for r in result.get("results", [])
                    ]
        # For synchronous tasks, mark as 100% complete if done
        elif job.celery_task_id and job.celery_task_id.startswith("sync-"):
            if job.status == "completed":
                response.progress = 100
            elif job.status == "processing":
                response.progress = 50
        
        return response
        
    finally:
        db.close()


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None
):
    """
    List recent upscaling jobs.
    
    - **limit**: Number of jobs to return (1-100)
    - **offset**: Offset for pagination
    - **status**: Filter by status (optional)
    """
    db = get_db()
    try:
        query = db.query(UpscaleJob)
        
        if status:
            query = query.filter(UpscaleJob.status == status)
        
        total = query.count()
        jobs = query.order_by(UpscaleJob.created_at.desc()).offset(offset).limit(limit).all()
        
        return JobListResponse(
            jobs=[
                JobListItem(
                    job_id=job.id,
                    status=job.status,
                    job_type=job.job_type,
                    scale=job.scale,
                    original_filename=job.original_filename,
                    created_at=job.created_at.isoformat() if job.created_at else None,
                    completed_at=job.updated_at.isoformat() if job.status in ["completed", "failed"] else None
                )
                for job in jobs
            ],
            total=total
        )
        
    finally:
        db.close()


@router.get("/compare/{job_id}", response_model=CompareResponse)
async def compare_images(job_id: str):
    """
    Get before/after comparison for a completed job.
    
    Returns URLs for original and upscaled images.
    """
    db = get_db()
    try:
        job = db.query(UpscaleJob).filter(UpscaleJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != UpscaleStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Job not completed yet")
        
        # Get file sizes
        original_size = None
        upscaled_size = None
        
        if job.original_path and Path(job.original_path).exists():
            original_size = Path(job.original_path).stat().st_size
        
        if job.result_path and Path(job.result_path).exists():
            upscaled_size = Path(job.result_path).stat().st_size
        
        from backend.schemas.upscale import ImageDimensions
        
        return CompareResponse(
            original_url=f"/api/upscale/download/original/{job_id}",
            upscaled_url=f"/api/upscale/download/result/{job_id}",
            original_dimensions=ImageDimensions(
                width=job.original_width,
                height=job.original_height
            ),
            upscaled_dimensions=ImageDimensions(
                width=job.upscaled_width,
                height=job.upscaled_height
            ),
            scale=job.scale,
            original_size=original_size,
            upscaled_size=upscaled_size
        )
        
    finally:
        db.close()


@router.get("/download/original/{job_id}")
async def download_original(job_id: str):
    """Download the original uploaded image."""
    db = get_db()
    try:
        job = db.query(UpscaleJob).filter(UpscaleJob.id == job_id).first()
        if not job or not job.original_path:
            raise HTTPException(status_code=404, detail="Original file not found")
        
        file_path = Path(job.original_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            path=str(file_path),
            filename=job.original_filename or file_path.name,
            media_type="image/*"
        )
        
    finally:
        db.close()


@router.get("/download/result/{job_id}")
async def download_result(job_id: str):
    """Download the upscaled image (HD)."""
    db = get_db()
    try:
        job = db.query(UpscaleJob).filter(UpscaleJob.id == job_id).first()
        if not job or not job.result_path:
            raise HTTPException(status_code=404, detail="Result file not found")
        
        if job.status != UpscaleStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Upscaling not completed yet")
        
        file_path = Path(job.result_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Result file not found on disk")
        
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type="image/*"
        )
        
    finally:
        db.close()


@router.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and associated files."""
    db = get_db()
    try:
        job = db.query(UpscaleJob).filter(UpscaleJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Delete files
        if job.original_path and Path(job.original_path).exists():
            Path(job.original_path).unlink()
        
        if job.result_path and Path(job.result_path).exists():
            Path(job.result_path).unlink()
        
        # Delete from database
        db.delete(job)
        db.commit()
        
        return {"message": "Job deleted successfully"}
        
    finally:
        db.close()


@router.get("/system-status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get system status and queue information."""
    import torch
    
    db = get_db()
    try:
        pending = db.query(UpscaleJob).filter(UpscaleJob.status == UpscaleStatus.PENDING).count()
        processing = db.query(UpscaleJob).filter(UpscaleJob.status == UpscaleStatus.PROCESSING).count()
        completed = db.query(UpscaleJob).filter(UpscaleJob.status == UpscaleStatus.COMPLETED).count()
        failed = db.query(UpscaleJob).filter(UpscaleJob.status == UpscaleStatus.FAILED).count()
        
        return SystemStatusResponse(
            status="healthy",
            queue_size=pending,
            active_jobs=processing,
            completed_jobs=completed,
            failed_jobs=failed,
            gpu_available=torch.cuda.is_available()
        )
        
    finally:
        db.close()
