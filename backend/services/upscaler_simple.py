"""
Simplified Image Upscaling Service (No RealESRGAN Required)

This version uses only PIL for upscaling and doesn't require PyTorch or RealESRGAN.
Use this for testing when AI dependencies are not available.
"""

from PIL import Image, ImageFilter
from typing import Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SimpleUpscaler:
    """
    Simple image upscaler using PIL's high-quality resampling.
    
    This is a fallback when RealESRGAN is not available.
    Results won't be as good as AI upscaling, but it's fast and dependency-free.
    """
    
    ALLOWED_INPUT_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif'}
    
    def __init__(self, models_dir: str = "models"):
        """Initialize the upscaler."""
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        logger.info("SimpleUpscaler initialized (PIL-based)")
    
    def upscale(self, image_path: str, scale: int = 2,
                output_path: Optional[str] = None) -> Tuple[str, Tuple[int, int], Tuple[int, int]]:
        """
        Upscale an image using PIL.
        
        Args:
            image_path: Path to input image
            scale: Upscaling factor (2 or 4)
            output_path: Optional output path
        
        Returns:
            Tuple of (output_path, original_size, upscaled_size)
        """
        if scale not in [2, 4]:
            raise ValueError("Scale must be 2 or 4")
        
        # Load image
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        original_size = img.size
        
        # Calculate new size
        new_size = (original_size[0] * scale, original_size[1] * scale)
        
        # Upscale using Lanczos resampling (high quality)
        upscaled = img.resize(new_size, Image.LANCZOS)
        
        # Apply mild sharpening to simulate enhancement
        upscaled = upscaled.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        # Generate output path if not provided
        if output_path is None:
            input_path = Path(image_path)
            output_dir = input_path.parent / "upscaled"
            output_dir.mkdir(exist_ok=True)
            output_path = str(output_dir / f"{input_path.stem}_x{scale}{input_path.suffix}")
        
        # Save with high quality
        save_kwargs = {'quality': 95, 'optimize': True}
        if Path(output_path).suffix.lower() == '.png':
            save_kwargs = {'optimize': True}
        
        upscaled.save(output_path, **save_kwargs)
        
        logger.info(f"Upscaled {image_path} ({original_size}) -> {output_path} ({new_size})")
        
        return output_path, original_size, new_size
    
    def validate_image(self, image_path: str) -> bool:
        """Validate if image can be processed."""
        try:
            ext = Path(image_path).suffix.lower()
            if ext not in self.ALLOWED_INPUT_FORMATS:
                return False
            
            with Image.open(image_path) as img:
                img.verify()
            
            return True
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False


# Alias for compatibility
BasicUpscaler = SimpleUpscaler


def get_upscaler():
    """Get upscaler instance (always returns SimpleUpscaler)."""
    return SimpleUpscaler()
