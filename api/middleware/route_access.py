"""
Middleware to disable or enable routes
"""


# FastAPI request and response
from fastapi import Request
from fastapi.responses import Response, JSONResponse

from api.config.config import ROUTE_DISABLE_CONFIG, ROUTE_DISABLED_REASON, ROUTE_DISABLED_RETRY_AFTER

def add_route_middleware(app):
    @app.middleware("http")
    async def route_middleware(request: Request, call_next):
        try:
            response: Response = await call_next(request)

            route = request.scope.get("route").path if request.scope.get("route") else request.url.path
            
            if route in ROUTE_DISABLE_CONFIG:
                return JSONResponse(status_code=503, 
                                    content=ROUTE_DISABLED_REASON,
                                    headers={"Retry-After": "300"})

        except Exception:
            raise

        return response

    return app