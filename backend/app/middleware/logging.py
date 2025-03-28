import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.utils.logging import log_api_request

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request and response details."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Start timer
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        
        # Process the request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Get user ID if available
        user_id = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.id
        
        # Log the request
        log_api_request(
            method=method,
            path=path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_id=user_id
        )
        
        return response
