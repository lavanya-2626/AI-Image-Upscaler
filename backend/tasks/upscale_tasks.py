"""
Celery Tasks for Image Upscaling

Handles single and bulk image upscaling with progress tracking.
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Optional
from celery import shared_task, current_task
from celery.exceptions import SoftTimeLimitExceeded
import logging

logger = logging.getLogger(__name__)

# Upload directory - use absolute paths from project root
project_root = Path(__file__).parent.parent.parent
UPLOAD_DIR = project_root / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

RESULT_DIR = project_root / "results"
RESULT_DIR.mkdir(exist_ok=True)


def get_upscaler():
    """Lazy import to avoid circular dependencies."""
    try:
        from backend.services.upscaler import get_upscaler as _get_upscaler
        return _get_upscaler()
    except ImportError:
        from backend.services.upscaler_simple import get_upscaler as _get_simple_upscaler
        return _get_simple_upscaler()


def update_db_job_status(job_id: Optional[str], status: str, **kwargs):
    """Helper to update job status in database."""
    if not job_id:
        return
    
    try:
        from backend.database import SessionLocal
        from backend.models import UpscaleJob
        
        db = SessionLocal()
        try:
            job = db.query(UpscaleJob).filter(UpscaleJob.id == job_id).first()
            if job:
                job.status = status
                for key, value in kwargs.items():
                    if hasattr(job, key):
                        setattr(job, key, value)
                db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to update job status: {e}")


def process_image_core(image_path: str, scale: int = 2, job_id: Optional[str] = None, progress_callback=None) -> Dict:
    """
    Core image processing logic (can be called directly or from Celery).
    
    Args:
        image_path: Path to the image file
        scale: Upscaling factor (2 or 4)
        job_id: Optional job ID for tracking
        progress_callback: Optional callback function for progress updates
    
    Returns:
        Dictionary with upscaling results
    """
    start_time = time.time()
    
    def update_progress(progress, status):
        if progress_callback:
            progress_callback(progress, status)
    
    try:
        # Update progress
        update_progress(10, "Loading upscaler...")
        
        # Get upscaler instance
        upscaler = get_upscaler()
        
        # Validate image
        update_progress(20, "Validating image...")
        
        if not upscaler.validate_image(image_path):
            raise ValueError("Invalid image file")
        
        # Update database if job_id provided
        update_db_job_status(job_id, "processing")
        
        # Perform upscaling
        update_progress(30, "Upscaling image...")
        
        output_filename = f"{Path(image_path).stem}_x{scale}{Path(image_path).suffix}"
        output_path = str(RESULT_DIR / output_filename)
        
        result_path, original_size, upscaled_size = upscaler.upscale(
            image_path=image_path,
            scale=scale,
            output_path=output_path
        )
        
        update_progress(90, "Finalizing...")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update database
        update_db_job_status(
            job_id, 
            "completed",
            result_path=result_path,
            processing_time=processing_time,
            original_width=original_size[0],
            original_height=original_size[1],
            upscaled_width=upscaled_size[0],
            upscaled_height=upscaled_size[1]
        )
        
        update_progress(100, "Completed")
        
        # Determine model type
        from backend.services.upscaler import RealESRGANUpscaler
        model_type = "RealESRGAN" if isinstance(upscaler, RealESRGANUpscaler) else "Basic"
        
        return {
            "success": True,
            "input_path": image_path,
            "output_path": result_path,
            "scale": scale,
            "original_size": original_size,
            "upscaled_size": upscaled_size,
            "processing_time": round(processing_time, 2),
            "model": model_type
        }
            
    except Exception as e:
        logger.error(f"Processing failed for {image_path}: {e}")
        update_db_job_status(job_id, "failed", error_message=str(e))
        raise


@shared_task(bind=True, max_retries=3)
def upscale_single(self, image_path: str, scale: int = 2, job_id: Optional[str] = None) -> Dict:
    """
    Celery task to upscale a single image.
    
    Args:
        image_path: Path to the image file
        scale: Upscaling factor (2 or 4)
        job_id: Optional job ID for tracking
    
    Returns:
        Dictionary with upscaling results
    """
    def celery_progress(progress, status):
        self.update_state(
            state="PROGRESS",
            meta={"progress": progress, "status": status}
        )
    
    try:
        return process_image_core(image_path, scale, job_id, celery_progress)
    except SoftTimeLimitExceeded:
        logger.error(f"Task timed out for {image_path}")
        update_db_job_status(job_id, "failed", error_message="Processing timeout")
        raise
        raise
        
    except Exception as exc:
        logger.error(f"Upscaling failed: {exc}")
        update_db_job_status(job_id, "failed", error_message=str(exc))
        
        # Retry on failure
        if self.request.retries < 3:
            logger.info(f"Retrying task (attempt {self.request.retries + 1})")
            raise self.retry(countdown=5, exc=exc)
        
        return {
            "success": False,
            "error": str(exc),
            "input_path": image_path
        }


@shared_task(bind=True, max_retries=2)
def upscale_bulk(self, image_paths: List[str], scale: int = 2, job_id: Optional[str] = None) -> Dict:
    """
    Upscale multiple images in batch.
    
    Args:
        image_paths: List of paths to image files
        scale: Upscaling factor (2 or 4)
        job_id: Optional job ID for tracking
    
    Returns:
        Dictionary with batch upscaling results
    """
    start_time = time.time()
    total = len(image_paths)
    results = []
    successful = 0
    failed = 0
    
    try:
        # Get upscaler instance
        upscaler = get_upscaler()
        
        # Update database
        update_db_job_status(job_id, "processing", total_files=total)
        
        # Process each image
        for i, image_path in enumerate(image_paths):
            progress = int((i / total) * 100)
            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": progress,
                    "status": f"Processing {i+1}/{total}: {Path(image_path).name}",
                    "current": i + 1,
                    "total": total,
                    "successful": successful,
                    "failed": failed
                }
            )
            
            try:
                if not upscaler.validate_image(image_path):
                    results.append({
                        "input_path": image_path,
                        "success": False,
                        "error": "Invalid image"
                    })
                    failed += 1
                    continue
                
                output_filename = f"{Path(image_path).stem}_x{scale}{Path(image_path).suffix}"
                output_path = str(RESULT_DIR / output_filename)
                
                result_path, original_size, upscaled_size = upscaler.upscale(
                    image_path=image_path,
                    scale=scale,
                    output_path=output_path
                )
                
                results.append({
                    "input_path": image_path,
                    "output_path": result_path,
                    "success": True,
                    "original_size": original_size,
                    "upscaled_size": upscaled_size
                })
                successful += 1
                
            except Exception as e:
                logger.error(f"Failed to upscale {image_path}: {e}")
                results.append({
                    "input_path": image_path,
                    "success": False,
                    "error": str(e)
                })
                failed += 1
        
        processing_time = time.time() - start_time
        
        # Update database
        final_status = "completed" if failed == 0 else "partial" if successful > 0 else "failed"
        update_db_job_status(
            job_id, 
            final_status,
            processed_files=successful,
            failed_files=failed,
            processing_time=processing_time
        )
        
        self.update_state(
            state="SUCCESS",
            meta={
                "progress": 100,
                "status": "Completed",
                "successful": successful,
                "failed": failed
            }
        )
        
        return {
            "success": failed == 0,
            "total": total,
            "successful": successful,
            "failed": failed,
            "scale": scale,
            "results": results,
            "processing_time": round(processing_time, 2)
        }
            
    except SoftTimeLimitExceeded:
        logger.error("Bulk upscaling task timed out")
        update_db_job_status(job_id, "failed", error_message="Processing timeout")
        raise
        
    except Exception as exc:
        logger.error(f"Bulk upscaling failed: {exc}")
        update_db_job_status(job_id, "failed", error_message=str(exc))
        return {
            "success": False,
            "error": str(exc),
            "total": total,
            "successful": successful,
            "failed": failed
        }


@shared_task
def cleanup_old_files(max_age_hours: int = 24):
    """
    Clean up old uploaded and result files.
    
    Args:
        max_age_hours: Maximum age of files in hours
    """
    import time
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    cleaned = 0
    for directory in [UPLOAD_DIR, RESULT_DIR]:
        for file_path in directory.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    cleaned += 1
    
    logger.info(f"Cleaned up {cleaned} old files")
    return {"cleaned_files": cleaned}
