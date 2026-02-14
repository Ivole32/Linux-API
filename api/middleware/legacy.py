"""
Middleware to add warnings to legacy response headers and return bodies.
"""
from fastapi import Request, HTTPException
from fastapi.responses import Response
from api.config.config import LEGACY_API_PREFIX

def add_legacy_middleware(app):
    @app.middleware("http")
    async def legacy_middleware(request: Request, call_next):
        response: Response = await call_next(request)

        # I saw some error related to a issue I created some time ago (it got closed)
        # Second try to fix Ref
        # Ref: https://github.com/pallets/werkzeug/issues/3063
        # ZAP found it so here is a possible fix with try/except
        try:
            request_url = request.url.path
            request_method = request.method

        except Exception as e:
            raise HTTPException(status_code=500, detail="Unexpected error while parsing host header")

        if request_url.startswith(LEGACY_API_PREFIX) and request_method != "OPTIONS":

            response.headers["X-Legacy-Endpoint"] = "true"
            response.headers["X-Legacy-Warning"] = "deprecated"

        return response
    
    return app