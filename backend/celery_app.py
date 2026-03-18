"""
Celery Configuration for Background Task Processing

Handles queue-based image upscaling for single and bulk operations.
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_success, task_failure
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis URL from environment or default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "image_upscaler",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["backend.tasks.upscale_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # Soft limit 55 minutes
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Process one task at a time per worker
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
    
    # Result settings
    result_expires=3600 * 24,  # Results expire after 24 hours
    result_extended=True,
    
    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_heartbeat=30,
    
    # Queue configuration
    task_routes={
        "backend.tasks.upscale_tasks.upscale_single": {"queue": "upscale"},
        "backend.tasks.upscale_tasks.upscale_bulk": {"queue": "upscale"},
    },
    
    # Task rate limiting
    task_annotations={
        "*": {
            "rate_limit": "10/m"  # Max 10 upscale tasks per minute
        }
    }
)


# Task event handlers
@task_prerun.connect
def task_prerun_handler(task_id, task, args, kwargs, **extras):
    """Handle task start."""
    logger.info(f"Task {task.name}[{task_id}] started")


@task_postrun.connect
def task_postrun_handler(task_id, task, args, kwargs, retval, state, **extras):
    """Handle task completion."""
    logger.info(f"Task {task.name}[{task_id}] finished with state: {state}")


@task_success.connect
def task_success_handler(sender, result, **kwargs):
    """Handle successful task."""
    logger.info(f"Task {sender.name} completed successfully")


@task_failure.connect
def task_failure_handler(sender, task_id, exception, args, kwargs, traceback, einfo, **extras):
    """Handle failed task."""
    logger.error(f"Task {sender.name}[{task_id}] failed: {exception}")


def get_task_status(task_id: str) -> dict:
    """Get status of a Celery task."""
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": result.status,
        "state": result.state
    }
    
    if result.successful():
        response["result"] = result.get()
    elif result.failed():
        response["error"] = str(result.result)
    elif result.status == "PROGRESS":
        response["progress"] = result.info.get("progress", 0) if result.info else 0
    
    return response


if __name__ == "__main__":
    # Start Celery worker
    celery_app.start()
