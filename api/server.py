import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware

# Legacy API routes
# => Old database system, ...
from api.routers.legacy.admin_endpoints import router as admin_router
from api.routers.legacy.user_endpoints import router as user_router
from api.routers.legacy.system_endpoints import router as system_router
from api.routers.legacy.mixed_endpoints import router as mixed_router

# Import rate limiter
from api.limiter.limiter import limiter

# Import database startup functions
from api.database.startup import startup_database

# Import header middleware
from api.middleware.headers import add_header_middleware

# Import CORS middleware
from api.middleware.cors import setup_cors

from api.config.config import API_TITLE, API_DESCRIPTION, API_VERSION, API_PREFIX, LEGACY_API_PREFIX, API_DOCS_ENABLED, DEMO_MODE

logger = logging.getLogger("uvicorn.error")

load_dotenv(dotenv_path="config.env")

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    swagger_ui_parameters={
        "docExpansion": "list",
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": DEMO_MODE,
        "filter": True,
        "syntaxHighlight.theme": "monokai",
    },
    docs_url="/docs" if API_DOCS_ENABLED else None,
    openapi_url="/openapi.json" if API_DOCS_ENABLED else None,
    redoc_url=None, # I don't like redocs so enable if you want to...
    on_startup=[startup_database]
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

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

# Include legacy routers
# Old database system
# => Other file, logic
app.include_router(user_router, prefix=LEGACY_API_PREFIX, tags=["Legacy"])
app.include_router(admin_router, prefix=LEGACY_API_PREFIX, tags=["Legacy"])
app.include_router(system_router, prefix=LEGACY_API_PREFIX, tags=["Legacy"])
app.include_router(mixed_router, prefix=LEGACY_API_PREFIX, tags=["Legacy"])

# Add custom headers middleware
add_header_middleware(app)

# Setup CORS middleware
setup_cors(app)

@app.get("/", include_in_schema=False)
@limiter.limit("10/second")
async def root(request: Request):
    if API_DOCS_ENABLED:
        return {"message": "API is running. See /docs for documentation.", "version": API_VERSION, "docs": "/docs"}
    else:
        return {"message": "API i running", "version": API_VERSION}