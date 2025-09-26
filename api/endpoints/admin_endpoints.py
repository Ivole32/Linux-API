from fastapi import APIRouter, Request, HTTPException

from core_functions.limiter import limiter
from core_functions.auth import get_user_role
from core_functions.user_database import get_user_database, UserRole

user_db, _ = get_user_database()

router = APIRouter()

@router.get(
    "/admin/admin-area",
    tags=["Admin"],
    description="A testing endpoint.",
    responses={
        200: {
            "description": "You are admin!!!",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Admin access granted for adminuser with role admin!"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized. Invalid API key",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or missing API key"}
                }
            }
        },
        403: {
            "description": "Admin access required",
            "content": {
                "application/json": {
                    "example": {"detail": "Admin access required"}
                }
            }
        }
    }
)
@limiter.limit("10/minute")
def admin_area(request: Request, user_data = get_user_role("admin")):
    return {"message": f"Admin access granted for {user_data['username']} with role {user_data['role']}!"}

@router.get(
    "/admin/users",
    tags=["Admin"],
    description="Returns a list of all users with their account information.",
    responses={
        200: {
            "description": "Users listed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "users": [
                            {"username": "adminuser", "role": "admin"},
                            {"username": "testuser", "role": "user"}
                        ]
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized. Invalid API key",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or missing API key"}
                }
            }
        },
        403: {
            "description": "Admin access required",
            "content": {
                "application/json": {
                    "example": {"detail": "Admin access required"}
                }
            }
        }
    }
)
@limiter.limit("5/minute")
def list_users(request: Request, user_data = get_user_role("admin")):
    users = user_db.list_users()
    return {"users": users}

@router.post(
    "/admin/user/create",
    tags=["Admin"],
    description="Creates a new user with the specified username, role, and optional API key.",
    responses={
        200: {
            "description": "The user was created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "username": "testuser",
                            "role": "user",
                            "api_key": "1234567890abcdef..."
                        }
                    }
                }
            }
        },
        400: {
            "description": "User creation failed or user already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "User creation failed or user already exists"}
                }
            }
        },
        401: {
            "description": "Unauthorized. Invalid API key",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or missing API key"}
                }
            }
        },
        403: {
            "description": "Admin access required",
            "content": {
                "application/json": {
                    "example": {"detail": "Admin access required"}
                }
            }
        }
    }
)
@limiter.limit("5/minute")
def create_user(request: Request, username: str, role: UserRole, api_key: str = "", user_data = get_user_role("admin")):
    user = user_db.add_user(username, role, api_key=api_key)
    if not user:
        raise HTTPException(status_code=400, detail="User creation failed or user already exists")

    return {"user": {"username": username, "role": role.value, "api_key": user}}