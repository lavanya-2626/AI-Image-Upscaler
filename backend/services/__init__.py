"""Services."""

# Try to import RealESRGAN upscaler, fall back to simple upscaler
try:
    from .upscaler import RealESRGANUpscaler, BasicUpscaler, get_upscaler
except ImportError as e:
    # Fall back to simple upscaler if RealESRGAN deps are missing
    from .upscaler_simple import SimpleUpscaler, get_upscaler
    RealESRGANUpscaler = None
    BasicUpscaler = SimpleUpscaler

__all__ = ["RealESRGANUpscaler", "BasicUpscaler", "get_upscaler", "SimpleUpscaler"]
