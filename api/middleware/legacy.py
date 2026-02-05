"""
Middleware to add warnings to legacy response headers and return bodies.
"""
import json
from fastapi import Request
from fastapi.responses import Response, JSONResponse
from api.config.config import LEGACY_API_PREFIX

def add_legacy_middleware(app):
    @app.middleware("http")
    async def legacy_middleware(request: Request, call_next):
        response: Response = await call_next(request)

        if request.url.path.startswith(LEGACY_API_PREFIX) and request.method != "OPTIONS":

            response.headers["X-Legacy-Endpoint"] = "true"
            response.headers["X-Legacy-Warning"] = "deprecated"

        return response
    
    return app