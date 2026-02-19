"""
Middleware for API metrics
"""
import time
from fastapi import Request
from fastapi import Response

from api.metrics.aggregator import record

def add_metrics_middleware(app):
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start = time.perf_counter()

        try:
            response: Response = await call_next(request)

            route = request.scope.get("route").path if request.scope.get("route") else request.url.path
            route.replace('\x00', '') # When sending routes with Nul (0x00) byte postgres will throw an error. So replace here 
            status = response.status_code

        except Exception:
            status = 500
            raise

        finally:
            duration = time.perf_counter() - start
            record(route, duration, status)

        return response