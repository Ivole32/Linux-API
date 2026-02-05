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
            warning_text = (
                "This is a legacy API endpoint. "
                "It uses old database logic and is not connected "
                "to the new database system "
            )

            response.headers["X-Legacy-Endpoint"] = "true"
            response.headers["X-Legacy-Warning"] = warning_text

            if isinstance(response, JSONResponse):
                try:
                    body = json.loads(response.body)

                    if isinstance(body, dict):
                        body["_warning"] = warning_text

                        response = JSONResponse(
                            content=body,
                            status_code=response.status_code,
                            headers=dict(response.headers)
                        )
                
                except Exception:
                    pass

        return response
    
    return app