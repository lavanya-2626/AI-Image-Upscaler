"""
RealESRGAN Image Upscaling Service

Supports 2x and 4x upscaling using Real-ESRGAN models.
"""

import os
from PIL import Image
from typing import Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import torch and realesrgan, but make them optional
try:
    import torch
    import numpy as np
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available. RealESRGAN upscaling will not work.")

try:
    from realesrgan import RealESRGANer
    from basicsr.archs.rrdbnet_arch import RRDBNet
    REALESRGAN_AVAILABLE = True
except ImportError:
    REALESRGAN_AVAILABLE = False
    logger.warning("RealESRGAN not available. Using basic upscaling only.")


class RealESRGANUpscaler:
    """
    RealESRGAN-based image upscaler supporting 2x and 4x upscaling.
    """
    
    # Model URLs for Real-ESRGAN
    MODEL_URLS = {
        "2x": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth",
        "4x": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
    }
    
    ALLOWED_INPUT_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    
    def __init__(self, models_dir: str = "models"):
        if not TORCH_AVAILABLE or not REALESRGAN_AVAILABLE:
            raise ImportError("PyTorch/RealESRGAN not available")
        
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        
        logger.info(f"RealESRGANUpscaler initialized. Device: {self.device}")
    
    def _get_model_path(self, scale: int) -> Path:
        """Get path to model file."""
        return self.models_dir / f"RealESRGAN_x{scale}plus.pth"
    
    def _load_model(self, scale: int):
        """Load Real-ESRGAN model for specified scale."""
        if not REALESRGAN_AVAILABLE or not TORCH_AVAILABLE:
            raise ImportError("RealESRGAN/PyTorch not available. Install with: pip install torch realesrgan")
        
        if scale in self.models:
            return self.models[scale]
        
        model_path = self._get_model_path(scale)
        
        # Download model if not exists
        if not model_path.exists():
            self._download_model(scale)
        
        # Initialize model
        if scale == 2:
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, 
                           num_block=23, num_grow_ch=32, scale=2)
        else:  # scale == 4
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                           num_block=23, num_grow_ch=32, scale=4)
        
        upsampler = RealESRGANer(
            scale=scale,
            model_path=str(model_path),
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=self.device.type == 'cuda'  # Use half precision on GPU
        )
        
        self.models[scale] = upsampler
        return upsampler
    
    def _download_model(self, scale: int):
        """Download Real-ESRGAN model."""
        import urllib.request
        from tqdm import tqdm
        
        url = self.MODEL_URLS.get(f"{scale}x")
        if not url:
            raise ValueError(f"No model URL for scale {scale}x")
        
        model_path = self._get_model_path(scale)
        
        logger.info(f"Downloading RealESRGAN {scale}x model...")
        
        class DownloadProgressBar(tqdm):
            def update_to(self, b=1, bsize=1, tsize=None):
                if tsize is not None:
                    self.total = tsize
                self.update(b * bsize - self.n)
        
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=f"RealESRGAN_x{scale}") as t:
            urllib.request.urlretrieve(url, model_path, reporthook=t.update_to)
        
        logger.info(f"Model downloaded to {model_path}")
    
    def upscale(self, image_path: str, scale: int = 2, 
                output_path: Optional[str] = None) -> Tuple[str, Tuple[int, int], Tuple[int, int]]:
        """
        Upscale an image using RealESRGAN.
        
        Args:
            image_path: Path to input image
            scale: Upscaling factor (2 or 4)
            output_path: Optional output path (auto-generated if None)
        
        Returns:
            Tuple of (output_path, original_size, upscaled_size)
        """
        import numpy as np
        
        if scale not in [2, 4]:
            raise ValueError("Scale must be 2 or 4")
        
        # Load image
        img = Image.open(image_path).convert('RGB')
        original_size = img.size
        
        # Load model
        upsampler = self._load_model(scale)
        
        # Convert PIL to numpy
        img_np = np.array(img)
        
        # Upscale
        try:
            output, _ = upsampler.enhance(img_np, outscale=scale)
        except RuntimeError as error:
            logger.error(f"Error during upscaling: {error}")
            # Fallback: try with tiling for large images
            upsampler.tile = 512
            output, _ = upsampler.enhance(img_np, outscale=scale)
            upsampler.tile = 0
        
        # Convert back to PIL
        output_img = Image.fromarray(output)
        upscaled_size = output_img.size
        
        # Generate output path if not provided
        if output_path is None:
            input_path = Path(image_path)
            output_dir = input_path.parent / "upscaled"
            output_dir.mkdir(exist_ok=True)
            output_path = str(output_dir / f"{input_path.stem}_x{scale}{input_path.suffix}")
        
        # Save upscaled image
        output_img.save(output_path, quality=95, optimize=True)
        
        logger.info(f"Upscaled {image_path} ({original_size}) -> {output_path} ({upscaled_size})")
        
        return output_path, original_size, upscaled_size
    
    def validate_image(self, image_path: str) -> bool:
        """Validate if image can be processed."""
        try:
            ext = Path(image_path).suffix.lower()
            if ext not in self.ALLOWED_INPUT_FORMATS:
                return False
            
            # Try to open
            with Image.open(image_path) as img:
                img.verify()
            
            return True
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False


# Simple fallback upscaler using PIL/Bicubic (if RealESRGAN not available)
class BasicUpscaler:
    """Basic upscaler using PIL (fallback when RealESRGAN is not available)."""
    
    ALLOWED_INPUT_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    
    def upscale(self, image_path: str, scale: int = 2,
                output_path: Optional[str] = None) -> Tuple[str, Tuple[int, int], Tuple[int, int]]:
        """Upscale using bicubic interpolation."""
        img = Image.open(image_path)
        original_size = img.size
        
        new_size = (original_size[0] * scale, original_size[1] * scale)
        upscaled = img.resize(new_size, Image.LANCZOS)
        
        if output_path is None:
            input_path = Path(image_path)
            output_dir = input_path.parent / "upscaled"
            output_dir.mkdir(exist_ok=True)
            output_path = str(output_dir / f"{input_path.stem}_x{scale}{input_path.suffix}")
        
        upscaled.save(output_path, quality=95, optimize=True)
        
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
        except Exception:
            return False


# Factory function to get upscaler instance
def get_upscaler():
    """Get best available upscaler instance."""
    try:
        if TORCH_AVAILABLE and REALESRGAN_AVAILABLE:
            return RealESRGANUpscaler()
        else:
            raise ImportError("RealESRGAN dependencies not available")
    except Exception as e:
        logger.warning(f"RealESRGAN not available ({e}), using basic upscaler")
        return BasicUpscaler()
