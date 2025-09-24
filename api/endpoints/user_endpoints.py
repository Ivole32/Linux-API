from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from core_functions.limiter import limiter
from core_functions.auth import get_user_role

router = APIRouter()

@router.get(
    "/user/user-info",
    tags=["User"],
    description="This endpoint returns the key owner's user informations.",
    responses={
        200: {
            "description": "User information returned",
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "Valid API key",
                            "value": {
                                "username": "testuser",
                                "role": "user"
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
        }
    }
)
@limiter.limit("10/minute")
def user_info(request: Request, user_data = get_user_role("user")):
    return JSONResponse(content={
        "username": user_data["username"],
        "role": user_data["role"]
    })

@router.delete(
    "/user/delete",
    tags=["User"],
    description="Deletes the current authenticated user.",
    responses={
        200: {
            "description": "User deleted successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "User deleted",
                            "value": {
                                "detail": "User deleted successfully"
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
        }
    }
)