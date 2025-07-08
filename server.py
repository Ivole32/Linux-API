from fastapi import FastAPI, HTTPException, Depends, Header, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"

    return response

API_KEYS = {
    "key-user-123": "user",
    "key-admin-456": "admin"
}

def verify_api_key(x_api_key: str = Header(...), required_role: str = "user"):
    user_role = API_KEYS.get(x_api_key)
    if user_role is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if required_role == "admin" and user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_role

def get_user_role(required_role: str):
    def dependency(x_api_key: str = Header(...)):
        return verify_api_key(x_api_key, required_role)
    return Depends(dependency)

@app.get("/user_info", tags=["User"])
@limiter.limit("5/minute")
def user_info(request: Request, role= get_user_role("user")):
    return JSONResponse(content={"role": f"{role}"})

@app.get("/admin-area", tags=["Admin"])
@limiter.limit("5/minute")
def admin_area(request: Request, role= get_user_role("admin")):
    return {"message": f"Admin access granted for {role}!"}