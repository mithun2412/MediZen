from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
from app.core.logging import get_logger, set_request_context

logger = get_logger("middleware")

class RequestTrackerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Generates unique request_id
    2. Logs every request with timing
    3. Sets context for nested logging
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Extract user_id if available (from JWT token)
        user_id = ""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # We'll extract user_id from token here later
            # For now, just pass empty
            pass
        
        # Set context for all logs in this request
        set_request_context(request_id, user_id)
        
        # Add request_id to response headers
        response_headers = {"X-Request-ID": request_id}
        
        # Start timer
        start_time = time.time()
        
        # Log request start
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "extra": {
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": request.client.host if request.client else "",
                    "user_agent": request.headers.get("user-agent", ""),
                }
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Add request_id to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "extra": {
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": round(duration_ms, 2),
                        "client_ip": request.client.host if request.client else "",
                    }
                }
            )
            
            return response
            
        except Exception as e:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "extra": {
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(e),
                        "duration_ms": round(duration_ms, 2),
                    }
                }
            )
            raise