import io
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

# CairoSVG is optional - only needed for SVG conversion
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError):
    CAIROSVG_AVAILABLE = False
    cairosvg = None


class ImageConverter:
    """Service for converting images between different formats."""
    
    ALLOWED_INPUT_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
    ALLOWED_OUTPUT_FORMATS = {"webp", "png", "jpg", "jpeg"}
    if CAIROSVG_AVAILABLE:
        ALLOWED_OUTPUT_FORMATS.add("svg")
    
    @staticmethod
    def validate_input_file(filename: str) -> bool:
        """Check if the input file format is supported."""
        ext = Path(filename).suffix.lower()
        return ext in ImageConverter.ALLOWED_INPUT_FORMATS
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get the file extension from filename."""
        return Path(filename).suffix.lower()
    
    @staticmethod
    def get_format_from_extension(ext: str) -> str:
        """Get image format from file extension."""
        ext = ext.lower().replace(".", "")
        format_map = {
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "png": "PNG",
            "webp": "WEBP",
            "bmp": "BMP",
            "tiff": "TIFF",
        }
        return format_map.get(ext, "JPEG")
    
    @classmethod
    def convert_to_webp(
        cls, 
        image_data: bytes, 
        quality: int = 85,
        filename: str = "image.jpg"
    ) -> Tuple[bytes, int, int]:
        """
        Convert image to WebP format.
        
        Args:
            image_data: Raw image bytes
            quality: WebP quality (1-100)
            filename: Original filename for format detection
            
        Returns:
            Tuple of (converted_bytes, original_size, converted_size)
        """
        original_size = len(image_data)
        
        # Load image using Pillow
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ("RGBA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[3] if image.mode == "RGBA" else None)
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")
        
        # Save as WebP
        output_buffer = io.BytesIO()
        image.save(output_buffer, format="WEBP", quality=quality, method=6)
        output_buffer.seek(0)
        
        converted_data = output_buffer.getvalue()
        converted_size = len(converted_data)
        
        return converted_data, original_size, converted_size
    
    @classmethod
    def convert_to_svg(
        cls, 
        image_data: bytes, 
        filename: str = "image.png"
    ) -> Tuple[bytes, int, int]:
        """
        Convert image to SVG format using potrace-like approach.
        Note: True raster to SVG conversion is complex. This uses a simplified approach.
        
        Args:
            image_data: Raw image bytes
            filename: Original filename
            
        Returns:
            Tuple of (converted_bytes, original_size, converted_size)
        """
        if not CAIROSVG_AVAILABLE:
            raise RuntimeError(
                "SVG conversion requires Cairo library. "
                "Please install GTK+ for Windows or run without SVG conversion."
            )
        
        original_size = len(image_data)
        
        # Load and process image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGBA for processing
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        # Create a simple SVG representation
        # This is a simplified vectorization - for production, consider using potrace
        width, height = image.size
        
        # Create SVG with embedded image (base64) as a fallback
        # For true vectorization, external libraries like potrace would be needed
        import base64
        
        base64_data = base64.b64encode(image_data).decode('utf-8')
        ext = Path(filename).suffix.lower().replace('.', '')
        mime_type = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
     width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <title>Converted from {filename}</title>
  <desc>Image converted using Image Morph</desc>
  <image width="{width}" height="{height}" xlink:href="data:{mime_type};base64,{base64_data}"/>
</svg>'''
        
        converted_data = svg_content.encode('utf-8')
        converted_size = len(converted_data)
        
        return converted_data, original_size, converted_size
    
    @classmethod
    def convert_image(
        cls,
        image_data: bytes,
        output_format: str,
        filename: str = "image.jpg",
        quality: int = 85
    ) -> Tuple[bytes, int, int]:
        """
        Convert image to specified format.
        
        Args:
            image_data: Raw image bytes
            output_format: Target format (webp, svg, png, jpg)
            filename: Original filename
            quality: Quality setting for lossy formats
            
        Returns:
            Tuple of (converted_bytes, original_size, converted_size)
        """
        output_format = output_format.lower()
        
        if output_format == "webp":
            return cls.convert_to_webp(image_data, quality, filename)
        elif output_format == "svg":
            return cls.convert_to_svg(image_data, filename)
        elif output_format in ["png", "jpg", "jpeg"]:
            return cls._convert_standard_format(image_data, output_format, quality, filename)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    @classmethod
    def _convert_standard_format(
        cls,
        image_data: bytes,
        output_format: str,
        quality: int,
        filename: str
    ) -> Tuple[bytes, int, int]:
        """Convert to standard formats (PNG, JPEG)."""
        original_size = len(image_data)
        
        image = Image.open(io.BytesIO(image_data))
        
        # Handle mode conversions
        if output_format.lower() in ["jpg", "jpeg"]:
            if image.mode in ("RGBA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                if image.mode == "RGBA":
                    background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")
        elif output_format.lower() == "png":
            if image.mode != "RGBA":
                image = image.convert("RGBA")
        
        output_buffer = io.BytesIO()
        
        format_map = {
            "png": "PNG",
            "jpg": "JPEG",
            "jpeg": "JPEG"
        }
        
        save_kwargs = {}
        if output_format.lower() in ["jpg", "jpeg"]:
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        elif output_format.lower() == "png":
            save_kwargs["optimize"] = True
        
        image.save(output_buffer, format=format_map[output_format.lower()], **save_kwargs)
        output_buffer.seek(0)
        
        converted_data = output_buffer.getvalue()
        converted_size = len(converted_data)
        
        return converted_data, original_size, converted_size
    
    @staticmethod
    def get_mime_type(format_name: str) -> str:
        """Get MIME type for a format."""
        mime_types = {
            "webp": "image/webp",
            "svg": "image/svg+xml",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }
        return mime_types.get(format_name.lower(), "application/octet-stream")
