"""Celery tasks for background processing."""

from .upscale_tasks import upscale_single, upscale_bulk, cleanup_old_files

__all__ = ["upscale_single", "upscale_bulk", "cleanup_old_files"]
