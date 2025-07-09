from sys import argv

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse
from user_database import get_user_database, UserRole

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

user_db = get_user_database()

if "--init" in argv:
    user_db.initialize_default_users(first_run=True)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"

    return response

def verify_api_key(x_api_key: str = Header(...), required_role: str = "user"):
    result = user_db.verify_api_key(x_api_key)
    
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    username, user_role = result
    
    if required_role == "admin" and user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"username": username, "role": user_role.value}

def get_user_role(required_role: str):
    def dependency(x_api_key: str = Header(...)):
        return verify_api_key(x_api_key, required_role)
    return Depends(dependency)

@app.get("/", tags=["General"])
@limiter.limit("10/minute")
def landing_page(request: Request):
    return JSONResponse(content={"message": "Docs at /docs"})

@app.get("/user_info", tags=["User"])
@limiter.limit("10/minute")
def user_info(request: Request, user_data = get_user_role("user")):
    return JSONResponse(content={
        "username": user_data["username"],
        "role": user_data["role"]
    })

@app.get("/admin/admin-area", tags=["Admin"])
@limiter.limit("10/minute")
def admin_area(request: Request, user_data = get_user_role("admin")):
    return {"message": f"Admin access granted for {user_data['username']} with role {user_data['role']}!"}

@app.get("/admin/users", tags=["Admin"])
@limiter.limit("5/minute")
def list_users(request: Request, user_data = get_user_role("admin")):
    """Listet alle Benutzer auf (nur für Admins)."""
    users = user_db.list_users()
    return {"users": users}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)