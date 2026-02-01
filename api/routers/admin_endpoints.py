from fastapi import APIRouter, Request, HTTPException

from api.limiter.limiter import limiter
from api.core_functions.auth import get_user_role
from api.database.user_database.user_database_old import get_user_database, UserRole

user_db, _ = get_user_database()

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/admin-area", description="A testing endpoint.")
@limiter.limit("10/minute")
def admin_area(request: Request, user_data = get_user_role("admin")):
    return {"message": f"Admin access granted for {user_data['username']} with role {user_data['role']}!"}

@router.get("/users", description="Returns a list of all users with their account information.")
@limiter.limit("5/minute")
def list_users(request: Request, user_data = get_user_role("admin")):
    users = user_db.list_users()
    return {"users": users}

@router.post("/user/create", description="Creates a new user with the specified username, role, and optional API key.")
@limiter.limit("5/minute")
def create_user(request: Request, username: str, role: UserRole, api_key: str = "", user_data = get_user_role("admin")):
    user = user_db.add_user(username, role, api_key=api_key)
    if not user:
        raise HTTPException(status_code=400, detail="User creation failed or user already exists")

    return {"user": {"username": username, "role": role.value, "api_key": user}}