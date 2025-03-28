from fastapi import BackgroundTasks
from typing import Callable, Any, Dict, List
import asyncio
import time
import uuid
import os
from app.utils.logging import logger

# In-memory storage for task results
# In production, use Redis or another persistent store
_tasks = {}

# Task status constants
class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

def get_task_info(task_id: str) -> Dict[str, Any]:
    """Get information about a task."""
    if task_id not in _tasks:
        return {"task_id": task_id, "status": "not_found"}
    
    return _tasks[task_id]

async def run_in_background(func: Callable, *args, **kwargs) -> str:
    """Run a function in the background."""
    task_id = str(uuid.uuid4())
    
    # Create task record
    _tasks[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "created_at": time.time(),
        "result": None,
        "error": None
    }
    
    # Create background task
    async def _run_task():
        _tasks[task_id]["status"] = TaskStatus.RUNNING
        _tasks[task_id]["started_at"] = time.time()
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # Run synchronous function in a thread pool
                result = await asyncio.to_thread(func, *args, **kwargs)
                
            _tasks[task_id]["result"] = result
            _tasks[task_id]["status"] = TaskStatus.COMPLETED
        except Exception as e:
            logger.exception(f"Background task failed: {e}")
            _tasks[task_id]["error"] = str(e)
            _tasks[task_id]["status"] = TaskStatus.FAILED
        finally:
            _tasks[task_id]["completed_at"] = time.time()
            _tasks[task_id]["duration"] = _tasks[task_id]["completed_at"] - _tasks[task_id]["started_at"]
            
            # Clean up old tasks (keep only for 1 hour)
            clean_old_tasks()
    
    # Start the task
    asyncio.create_task(_run_task())
    
    return task_id

def clean_old_tasks(max_age: int = 3600):
    """Clean up tasks older than max_age seconds."""
    now = time.time()
    to_delete = []
    
    for task_id, task in _tasks.items():
        if task["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            if "completed_at" in task and now - task["completed_at"] > max_age:
                to_delete.append(task_id)
    
    for task_id in to_delete:
        del _tasks[task_id]

def register_background_task(background_tasks: BackgroundTasks, func: Callable, *args, **kwargs):
    """Add a task to FastAPI's BackgroundTasks."""
    background_tasks.add_task(func, *args, **kwargs)
