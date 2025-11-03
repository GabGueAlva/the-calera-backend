import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        print(f"Starting request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        print(f"Completed request: {request.method} {request.url} - {response.status_code} - {process_time:.4f}s")
        
        return response