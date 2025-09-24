from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from slowapi.middleware import SlowAPIMiddleware

from api.endpoints.admin_endpoints import router as admin_router
from api.endpoints.user_endpoints import router as user_router
from api.endpoints.system_endpoints import router as system_router
from api.endpoints.unauthenticated_endpoints import router as unauthenticated_router
from api.endpoints.mixed_endpoints import router as mixed_router

from core_functions.limiter import limiter

app = FastAPI(
    title="Linux-API Server",
    version="1.0.0",
    swagger_ui_parameters={
        "docExpansion": "list",
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
        "filter": True,
        "syntaxHighlight.theme": "monokai",
    },
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

app.include_router(unauthenticated_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(system_router)
app.include_router(mixed_router)