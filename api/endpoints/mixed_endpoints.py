from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse

from core_functions.auth import get_user_role
from core_functions.user_database import get_user_database
from core_functions.limiter import limiter

router = APIRouter()

user_db = get_user_database()

@router.delete(
    "/user/delete",
    tags=["Admin", "User"],
    description="A endpoint to delete a user. If you are an admin you can delete any user, as a normal user you can only delete your own account.",
    responses={
        200: {"description": "User was deleted successfully"},
        403: {"description": "You don't have the rights to delete that user"},
        401: {"description": "Unauthorized. Invalid API key"}
    }
)
@limiter.limit("5/minute")
def delete_user(request: Request, username: str, user_data = get_user_role("user")):
    if user_data["role"] == "admin":
        if user_db.delete_user(username) == True:
            return JSONResponse(content={
                "status": "success"
            })

    elif user_data["username"] == username:
        if user_db.delete_user(username) == True:
            return JSONResponse(content={
                "status": "success"
            })

    else:
        raise HTTPException(status_code=403, detail="Admin access required for performing this action on other user's accounts.")