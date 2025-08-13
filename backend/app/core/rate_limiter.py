from time import time
from typing import Callable
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

class RateLimiterMiddleware:
    def __init__(self, max_requests_per_minute: int = 100) -> None:
        self.max_requests = max_requests_per_minute
        self.window_seconds = 60
        self._buckets: dict[str, list[float]] = {}

    async def __call__(self, request: Request, call_next: Callable):
        client_ip = request.client.host if request.client else "unknown"
        now = time()
        bucket = self._buckets.setdefault(client_ip, [])
        threshold = now - self.window_seconds
        while bucket and bucket[0] < threshold:
            bucket.pop(0)
        if len(bucket) >= self.max_requests:
            return JSONResponse(status_code=429, content={"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests"}})
        bucket.append(now)
        return await call_next(request)