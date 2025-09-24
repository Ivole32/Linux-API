from fastapi import APIRouter, Request, HTTPException

from core_functions.limiter import limiter
from core_functions.auth import get_user_role
from core_functions.user_database import get_user_database, UserRole

user_db, _ = get_user_database()

router = APIRouter()

@router.get(
    "/admin/admin-area",
    tags=["Admin"],
    description="Test endpoint for admin users.",
    responses={
        200: {
            "description": "Admin area accessed",
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "Admin access",
                            "value": {
                                "detail": "Welcome to the admin area"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized. Invalid API key",
            "content": {
                "application/json": {
                    "examples": {
                        "Unauthorized": {
                            "summary": "Missing or invalid API key",
                            "value": {
                                "detail": "Unauthorized"
                            }
                        }
                    }
                }
            }
        },
        403: {
            "description": "Forbidden. Not an admin user",
            "content": {
                "application/json": {
                    "examples": {
                        "Forbidden": {
                            "summary": "Not admin",
                            "value": {
                                "detail": "Forbidden"
                            }
                        }
                    }
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
    description="Returns a list of all users in the system.",
    responses={
        200: {
            "description": "List of users",
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "User list",
                            "value": [
                                {"username": "admin", "role": "admin"},
                                {"username": "testuser", "role": "user"}
                            ]
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized. Invalid API key",
            "content": {
                "application/json": {
                    "examples": {
                        "Unauthorized": {
                            "summary": "Missing or invalid API key",
                            "value": {
                                "detail": "Unauthorized"
                            }
                        }
                    }
                }
            }
        },
        403: {
            "description": "Forbidden. Not an admin user",
            "content": {
                "application/json": {
                    "examples": {
                        "Forbidden": {
                            "summary": "Not admin",
                            "value": {
                                "detail": "Forbidden"
                            }
                        }
                    }
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
    description="Creates a new user with specified username and role.",
    responses={
        200: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "User created",
                            "value": {
                                "detail": "User testuser created with role user"
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Bad request. Username or role invalid",
            "content": {
                "application/json": {
                    "examples": {
                        "BadRequest": {
                            "summary": "Invalid input",
                            "value": {
                                "detail": "Invalid username or role"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized. Invalid API key",
            "content": {
                "application/json": {
                    "examples": {
                        "Unauthorized": {
                            "summary": "Missing or invalid API key",
                            "value": {
                                "detail": "Unauthorized"
                            }
                        }
                    }
                }
            }
        },
        403: {
            "description": "Forbidden. Not an admin user",
            "content": {
                "application/json": {
                    "examples": {
                        "Forbidden": {
                            "summary": "Not admin",
                            "value": {
                                "detail": "Forbidden"
                            }
                        }
                    }
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