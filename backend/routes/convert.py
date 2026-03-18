import os
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
import io

from backend.database import get_db
from backend.models import ImageRecord
from backend.services.image_converter import ImageConverter
from backend.storage.r2_storage import r2_storage
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["conversion"])

# In-memory storage for files when R2 is not configured
local_storage = {}


async def _upload_single_image(file: UploadFile, db: Session):
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    if not ImageConverter.validate_input_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(ImageConverter.ALLOWED_INPUT_FORMATS)}",
        )

    # Read file content
    file_content = await file.read()

    # Check file size
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB",
        )

    # Get file format
    file_ext = ImageConverter.get_file_extension(file.filename)
    file_format = ImageConverter.get_format_from_extension(file_ext)

    # Create database record
    image_record = ImageRecord(
        original_name=file.filename,
        original_format=file_format,
        file_size=str(len(file_content)),
        status="uploaded",
    )
    db.add(image_record)
    db.commit()
    db.refresh(image_record)

    # Store file locally or upload to R2
    original_url = None
    if r2_storage.is_configured():
        original_url = r2_storage.upload_file(
            file_content,
            file.filename,
            content_type=f"image/{file_format.lower()}",
        )
    else:
        # Store in memory for development
        local_storage[f"original_{image_record.id}"] = file_content
        original_url = f"local://original_{image_record.id}"

    if original_url:
        image_record.original_url = original_url
        db.commit()

    return {
        "id": image_record.id,
        "message": "Upload successful",
        "original_name": file.filename,
        "format": file_format,
        "size": len(file_content),
        "url": original_url,
    }


@router.post("/upload")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an image file.
    
    Returns:
        JSON with upload status and image ID
    """
    return await _upload_single_image(file, db)


@router.post("/upload/bulk")
async def upload_images_bulk(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload multiple image files.

    Returns:
        JSON with uploaded items and per-file errors (if any)
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    items = []
    errors = []

    for index, file in enumerate(files):
        try:
            item = await _upload_single_image(file, db)
            item["index"] = index
            items.append(item)
        except HTTPException as e:
            errors.append(
                {
                    "index": index,
                    "filename": file.filename,
                    "detail": e.detail,
                }
            )

    return {
        "count": len(items),
        "items": items,
        "error_count": len(errors),
        "errors": errors,
    }


@router.post("/convert")
async def convert_image(
    background_tasks: BackgroundTasks,
    id: str = Form(...),
    format: str = Form(...),
    quality: int = Form(85),
    db: Session = Depends(get_db)
):
    """
    Convert an uploaded image to the specified format.
    
    Args:
        id: Image ID from upload
        format: Target format (webp, svg, png, jpg)
        quality: Quality for lossy formats (1-100)
    
    Returns:
        JSON with conversion status and download URL
    """
    # Validate format
    format = format.lower()
    if format not in ImageConverter.ALLOWED_OUTPUT_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Allowed: {', '.join(ImageConverter.ALLOWED_OUTPUT_FORMATS)}"
        )
    
    # Get image record
    image_record = db.query(ImageRecord).filter(ImageRecord.id == id).first()
    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Get original image data
    original_data = None
    if image_record.original_url and image_record.original_url.startswith("local://"):
        key = image_record.original_url.replace("local://", "")
        original_data = local_storage.get(key)
    elif r2_storage.is_configured() and image_record.original_url:
        # Extract key from URL
        key = image_record.original_url.split("/")[-2] + "/" + image_record.original_url.split("/")[-1] \
              if "/uploads/" in image_record.original_url else None
        if key:
            original_data = r2_storage.get_file(key)
    
    if not original_data:
        raise HTTPException(status_code=404, detail="Original image data not found")
    
    # Update status
    image_record.status = "converting"
    image_record.converted_format = format.upper()
    db.commit()
    
    try:
        # Convert image
        converted_data, original_size, converted_size = ImageConverter.convert_image(
            original_data,
            format,
            image_record.original_name,
            quality
        )
        
        # Upload converted file
        content_type = ImageConverter.get_mime_type(format)
        converted_url = None
        
        if r2_storage.is_configured():
            converted_url = r2_storage.upload_converted_file(
                converted_data,
                image_record.id,
                format,
                content_type
            )
        else:
            # Store locally
            local_storage[f"converted_{image_record.id}.{format}"] = converted_data
            converted_url = f"local://converted_{image_record.id}.{format}"
        
        # Update record
        image_record.converted_url = converted_url
        image_record.converted_size = str(converted_size)
        image_record.status = "completed"
        image_record.conversion_date = datetime.utcnow()
        db.commit()
        
        # Calculate savings
        savings_percent = 0
        if original_size > 0:
            savings_percent = ((original_size - converted_size) / original_size) * 100
        
        return {
            "status": "success",
            "id": image_record.id,
            "download_url": f"/api/download/{image_record.id}",
            "preview_url": f"/api/image/{image_record.id}",
            "original_size": original_size,
            "converted_size": converted_size,
            "savings_percent": round(savings_percent, 2),
            "format": format.upper()
        }
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        image_record.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.get("/image/{image_id}")
async def get_image(image_id: str, db: Session = Depends(get_db)):
    """
    Get the converted image for preview.
    
    Args:
        image_id: The image ID
    
    Returns:
        Image file
    """
    image_record = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not image_record or not image_record.converted_url:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Get image data
    image_data = None
    format_ext = image_record.converted_format.lower() if image_record.converted_format else "webp"
    
    if image_record.converted_url.startswith("local://"):
        key = image_record.converted_url.replace("local://", "")
        image_data = local_storage.get(key)
    elif r2_storage.is_configured():
        key = f"converted/{image_id}.{format_ext}"
        image_data = r2_storage.get_file(key)
    
    if not image_data:
        raise HTTPException(status_code=404, detail="Image data not found")
    
    content_type = ImageConverter.get_mime_type(format_ext)
    
    return StreamingResponse(
        io.BytesIO(image_data),
        media_type=content_type,
        headers={"Content-Disposition": f"inline; filename={image_id}.{format_ext}"}
    )


@router.get("/download/{image_id}")
async def download_image(image_id: str, db: Session = Depends(get_db)):
    """
    Download the converted image.
    
    Args:
        image_id: The image ID
    
    Returns:
        Image file as download
    """
    image_record = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not image_record or not image_record.converted_url:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Get image data
    image_data = None
    format_ext = image_record.converted_format.lower() if image_record.converted_format else "webp"
    original_name = image_record.original_name
    base_name = original_name.rsplit(".", 1)[0] if "." in original_name else original_name
    download_name = f"{base_name}_converted.{format_ext}"
    
    if image_record.converted_url.startswith("local://"):
        key = image_record.converted_url.replace("local://", "")
        image_data = local_storage.get(key)
    elif r2_storage.is_configured():
        key = f"converted/{image_id}.{format_ext}"
        image_data = r2_storage.get_file(key)
    
    if not image_data:
        raise HTTPException(status_code=404, detail="Image data not found")
    
    content_type = ImageConverter.get_mime_type(format_ext)
    
    return StreamingResponse(
        io.BytesIO(image_data),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={download_name}"}
    )


@router.get("/images")
async def list_images(limit: int = 20, db: Session = Depends(get_db)):
    """
    List recent image conversions.
    
    Args:
        limit: Maximum number of results
    
    Returns:
        List of image records
    """
    images = db.query(ImageRecord).order_by(ImageRecord.upload_date.desc()).limit(limit).all()
    return {
        "images": [img.to_dict() for img in images],
        "count": len(images)
    }


@router.delete("/image/{image_id}")
async def delete_image(image_id: str, db: Session = Depends(get_db)):
    """
    Delete an image record and its files.
    
    Args:
        image_id: The image ID
    
    Returns:
        Deletion status
    """
    image_record = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Clean up local storage if applicable
    if image_record.original_url and image_record.original_url.startswith("local://"):
        key = image_record.original_url.replace("local://", "")
        local_storage.pop(key, None)
    
    if image_record.converted_url and image_record.converted_url.startswith("local://"):
        key = image_record.converted_url.replace("local://", "")
        local_storage.pop(key, None)
    
    # Delete from R2 if configured
    if r2_storage.is_configured():
        if image_record.original_url and "/uploads/" in image_record.original_url:
            key = "uploads/" + image_record.original_url.split("/")[-1]
            r2_storage.delete_file(key)
        
        if image_record.converted_format:
            format_ext = image_record.converted_format.lower()
            r2_storage.delete_file(f"converted/{image_id}.{format_ext}")
    
    # Delete from database
    db.delete(image_record)
    db.commit()
    
    return {"message": "Image deleted successfully", "id": image_id}
