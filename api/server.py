import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware

from api.routers.admin_endpoints import router as admin_router
from api.routers.user_endpoints import router as user_router
from api.routers.system_endpoints import router as system_router
from api.routers.unauthenticated_endpoints import router as unauthenticated_router
from api.routers.mixed_endpoints import router as mixed_router

from api.core_functions.limiter import limiter


logger = logging.getLogger("uvicorn.error")

load_dotenv(dotenv_path="config.env")

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

app = FastAPI(
    title="Linux-API Server",
    version="dev",
    swagger_ui_parameters={
        "docExpansion": "list",
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": DEMO_MODE,
        "filter": True,
        "syntaxHighlight.theme": "monokai",
    },
    docs_url="/docs",
    redoc_url=None
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE"
    return response

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "500 Internal server error"},
    )

app.include_router(unauthenticated_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
app.include_router(mixed_router, prefix="/api/v1")