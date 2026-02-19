"""
Middleware to add warnings to legacy response headers and return bodies.
"""
from fastapi import Request
from fastapi.responses import Response, JSONResponse
from api.config.config import LEGACY_API_PREFIX

def add_legacy_middleware(app):
    @app.middleware("http")
    async def legacy_middleware(request: Request, call_next):
        # I saw some error related to an issue I created some time ago (it got closed)
        # Second try to fix Ref
        # Ref: https://github.com/pallets/werkzeug/issues/3063
        # ZAP found it so here is a possible fix with try/except
        try:
            response: Response = await call_next(request)

            request_url = request.url.path
            request_method = request.method

        except Exception as e:
            return JSONResponse(status_code=400, content={"detail": "Invalid request."})

        if request_url.startswith(LEGACY_API_PREFIX) and request_method != "OPTIONS":

            response.headers["X-Legacy-Endpoint"] = "true"
            response.headers["X-Legacy-Warning"] = "deprecated"

        return response
    
    return app