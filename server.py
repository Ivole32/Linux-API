from sys import argv

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse
from user_database import get_user_database, UserRole, initialize_default_users

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

user_db = get_user_database()

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

#Landing endpoint
@app.get("/", tags=["General"], description = "The landing endpoint of the API. It returns a message with the documentation link.")
@limiter.limit("10/minute")
def landing_page(request: Request):
    return JSONResponse(content={
            "message": "Docs at /docs",
            "doc-link": "/docs"
        })

# User endpoints
@app.get("/user/user-info", tags=["User"], description = "This endpoint returns the key owner's user informations.")
@limiter.limit("10/minute")
def user_info(request: Request, user_data = get_user_role("user")):
    return JSONResponse(content={
        "username": user_data["username"],
        "role": user_data["role"]
    })

# Admin endpoints
@app.get("/admin/admin-area", tags=["Admin"], description = "A testing endpoint")
@limiter.limit("10/minute")
def admin_area(request: Request, user_data = get_user_role("admin")):
    return {"message": f"Admin access granted for {user_data['username']} with role {user_data['role']}!"}

@app.get("/admin/users", tags=["Admin"], description = "This endpoint returns a list of all users with there account informations.")
@limiter.limit("5/minute")
def list_users(request: Request, user_data = get_user_role("admin")):
    users = user_db.list_users()
    return {"users": users}

@app.post("/admin/user/create", tags=["Admin"], description= "This endpoint creates a new user with the specified username, role, and optional API key.")
@limiter.limit("5/minute")
def create_user(request: Request, username: str, role: UserRole, api_key: str = "", user_data = get_user_role("admin")):
    user = user_db.add_user(username, role, api_key=api_key)
    if not user:
        raise HTTPException(status_code=400, detail="User creation failed or user already exists")

    return {"user": {"username": username, "role": role.value, "api_key": user}}

# User + Admin endpoints
@app.delete("/user/delete", tags=["Admin", "User"])
@limiter.limit("5/minute")
def delete_user(request: Request, username: str, api_key: str, user_data = get_user_role("user"))
    if user_data["role"] == "admin":
        user_db.delete_user(username)

    elif user_data["username"] == username:
        user_db.delete_user(username)