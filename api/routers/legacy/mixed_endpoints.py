from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, HTTPException

from api.limiter.limiter import limiter
from api.core_functions.auth import get_user_role
from api.database.user_database.user_database_old import get_user_database

router = APIRouter(prefix="/users")

user_db, _ = get_user_database()

@router.delete(
    "/delete",
    tags=["Admin", "User"],
    description="A endpoint to delete a user. If you are an admin you can delete any user, as a normal user you can only delete your own account."
)
@limiter.limit("5/minute")
def delete_user(request: Request, username: str, user_data = get_user_role("user")):
    if username == "admin":
        raise HTTPException(status_code=403, detail="The admin account cannot be deleted.")
        
    if user_data["role"] == "admin":
        if user_db.delete_user(username) == True:
            return JSONResponse(content={
                "status": "success"
            })
        else:
            raise HTTPException(status_code=400, detail="User deletion failed or user does not exist")

    elif user_data["username"] == username:
        if user_db.delete_user(username) == True:
            return JSONResponse(content={
                "status": "success"
            })
        else:
            raise HTTPException(status_code=400, detail="User deletion failed or user does not exist")

    else:
        raise HTTPException(status_code=403, detail="Admin access required for performing this action on other user's accounts.")