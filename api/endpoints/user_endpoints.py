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
                    "example": {
                        "username": "testuser",
                        "role": "user"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized. Invalid API key",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid API key"}
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