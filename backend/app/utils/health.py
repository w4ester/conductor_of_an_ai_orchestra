import time
import requests
import os
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.db.database import get_db

# Configuration for Ollama API
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")

class HealthChecker:
    """Health check utility for the application."""
    
    @staticmethod
    def check_database(db: Session) -> Dict[str, Any]:
        """Check database connection."""
        start_time = time.time()
        try:
            # Simple query to check database connection
            db.execute("SELECT 1").fetchall()
            status = "healthy"
            error = None
        except Exception as e:
            status = "unhealthy"
            error = str(e)
        
        response_time = (time.time() - start_time) * 1000  # ms
        
        return {
            "component": "database",
            "status": status,
            "response_time": round(response_time, 2),
            "error": error
        }
    
    @staticmethod
    def check_ollama_api() -> Dict[str, Any]:
        """Check Ollama API connection."""
        start_time = time.time()
        try:
            response = requests.get(
                f"{OLLAMA_API_URL}/tags", 
                timeout=5.0
            )
            status = "healthy" if response.status_code == 200 else "unhealthy"
            error = None if response.status_code == 200 else f"HTTP {response.status_code}"
        except Exception as e:
            status = "unhealthy"
            error = str(e)
        
        response_time = (time.time() - start_time) * 1000  # ms
        
        return {
            "component": "ollama_api",
            "status": status,
            "response_time": round(response_time, 2),
            "error": error
        }
    
    @classmethod
    def check_all(cls, db: Session) -> Dict[str, Any]:
        """Run all health checks."""
        start_time = time.time()
        
        db_check = cls.check_database(db)
        ollama_check = cls.check_ollama_api()
        
        # Overall status is healthy only if all components are healthy
        overall_status = "healthy"
        if db_check["status"] != "healthy" or ollama_check["status"] != "healthy":
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "uptime": time.time() - float(os.getenv("APP_START_TIME", time.time())),
            "checks": [
                db_check,
                ollama_check
            ],
            "response_time": round((time.time() - start_time) * 1000, 2)
        }
