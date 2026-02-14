from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from api.limiter.limiter import limiter
from api.auth.legacy_auth import get_user_role

router = APIRouter()

@router.get("/user/user-info", description="This endpoint returns the key owner's user informations.")
@limiter.limit("10/minute")
async def user_info(request: Request, user_data = get_user_role("user")):
    return JSONResponse(content={
        "username": user_data["username"],
        "role": user_data["role"]
    })