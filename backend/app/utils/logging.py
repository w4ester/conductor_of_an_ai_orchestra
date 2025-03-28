import logging
import sys
import os
from typing import Dict, Any, Optional

# Configure logging format
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create logger
logger = logging.getLogger("ollama-workshop")
logger.setLevel(getattr(logging, log_level))

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(console_handler)

# Create file handler if LOG_FILE is set
log_file = os.getenv("LOG_FILE")
if log_file:
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

def log_api_request(method: str, path: str, status_code: int, duration_ms: float, user_id: Optional[str] = None):
    """
    Log API request details
    """
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        "user_id": user_id or "anonymous"
    }
    
    log_msg = (
        f"API Request: {method} {path} - "
        f"Status: {status_code} - "
        f"Duration: {log_data['duration_ms']}ms - "
        f"User: {log_data['user_id']}"
    )
    
    if 200 <= status_code < 300:
        logger.info(log_msg, extra={"data": log_data})
    elif 400 <= status_code < 500:
        logger.warning(log_msg, extra={"data": log_data})
    elif status_code >= 500:
        logger.error(log_msg, extra={"data": log_data})
    else:
        logger.debug(log_msg, extra={"data": log_data})

def log_error(error: Exception, context: Dict[str, Any] = None):
    """
    Log exception with context
    """
    context = context or {}
    logger.exception(f"Error: {str(error)}", extra={"data": context})
