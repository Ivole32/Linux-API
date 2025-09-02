from fastapi import FastAPI, Request
from slowapi.middleware import SlowAPIMiddleware

from api.endpoints.admin_endpoints import router as admin_router
from api.endpoints.user_endpoints import router as user_router
from api.endpoints.system_endpoints import router as system_router
from api.endpoints.unauthenticated_endpoints import router as unauthenticated_router
from api.endpoints.mixed_endpoints import router as mixed_router

from core_functions.limiter import limiter


from fastapi import FastAPI, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

API_KEY_NAME = "X-API-Key"
DEMO_KEY = "my-demo-key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

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

app.include_router(unauthenticated_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(system_router)
app.include_router(mixed_router)