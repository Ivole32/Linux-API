import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware

# Legacy API routes
# => Old database system, ...
from api.routers.legacy.admin_endpoints import router as legacy_admin_router
from api.routers.legacy.user_endpoints import router as legacy_user_router
from api.routers.legacy.system_endpoints import router as legacy_system_router
from api.routers.legacy.mixed_endpoints import router as legacy_mixed_router

# New API routes
# => New database system, ...
from api.routers.v1.user_router import router as v1_user_router
from api.routers.v1.admin_router import router as v1_admin_router
from api.routers.v1.system_load_router import router as v1_system_load_router
from api.routers.v1.system_info_router import router as v1_system_info_router
from api.routers.v1.metrics_router import router as v1_metric_router
from api.routers.v1.health_router import router as v1_health_router

# Import rate limiter
from api.limiter.limiter import limiter

# Import database startup functions
from api.database.startup import startup_database

# Import header middleware
from api.middleware.headers import add_header_middleware

# Import legacy middleware
from api.middleware.legacy import add_legacy_middleware

# Import CORS middleware
from api.middleware.cors import setup_cors

# Import metrics middleware
from api.middleware.metrics import add_metrics_middleware

# Import HostTrust middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Import metric flush worker
from api.metrics.flush_worker import flush_loop

# Import config
from api.config.config import API_TITLE, API_DESCRIPTION, API_VERSION, API_PREFIX, LEGACY_API_PREFIX, API_DOCS_ENABLED, ALLOWED_HOSTS, ENABLE_LEGACY_ROUTES, DEMO_MODE

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context.

    Startup:
        - Initialize database
        - Start background flush worker

    Shutdown:
        - Cancel background worker gracefully
    """

    # Initialize database
    startup_database()

    # Start background metrics flush worker
    flush_task = asyncio.create_task(flush_loop())
    app.state.flush_task = flush_task

    try:
        yield

    finally:
        flush_task.cancel()

        try:
            await flush_task
        except asyncio.CancelledError:
            pass

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
    on_startup=[startup_database],
    lifespan=lifespan,
)

# Setup CORS middleware early so it wraps all requests
setup_cors(app)

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

# Add metric middleware
add_metrics_middleware(app) # Add middleware here 
                            #=> needs to be first because only then it can detect everything

@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "500 Internal server error"},
    )

# Include v1 routers
app.include_router(v1_user_router, prefix=API_PREFIX, tags=["v1"])
app.include_router(v1_admin_router, prefix=API_PREFIX, tags=["v1"])
app.include_router(v1_system_load_router, prefix=API_PREFIX, tags=["v1"])
app.include_router(v1_system_info_router, prefix=API_PREFIX, tags=["v1"])
app.include_router(v1_metric_router, prefix=API_PREFIX, tags=["v1"])
app.include_router(v1_health_router, prefix=API_PREFIX, tags=["v1"])

# Include legacy routers
# Old database system
# => Other file, logic
if ENABLE_LEGACY_ROUTES:
    app.include_router(legacy_user_router, prefix=LEGACY_API_PREFIX, tags=["Legacy"], deprecated=True)
    app.include_router(legacy_admin_router, prefix=LEGACY_API_PREFIX, tags=["Legacy"], deprecated=True)
    app.include_router(legacy_system_router, prefix=LEGACY_API_PREFIX, tags=["Legacy"], deprecated=True)
    app.include_router(legacy_mixed_router, prefix=LEGACY_API_PREFIX, tags=["Legacy"], deprecated=True)

    # Add custom legacy middleware
    add_legacy_middleware(app)

# Add custom headers middleware
add_header_middleware(app)


# Add Trusted Host Middleware
# Need to add this manually
# First try to fix Ref
# Ref: https://github.com/pallets/werkzeug/issues/3063
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS
)

@app.get("/", include_in_schema=False)
@limiter.limit("10/second")
async def root(request: Request):
    if API_DOCS_ENABLED:
        return {"message": "API is running. See /docs for documentation.", "version": API_VERSION, "docs": "/docs"}
    else:
        return {"message": "API is running", "version": API_VERSION}