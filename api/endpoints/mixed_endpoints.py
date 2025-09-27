from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, HTTPException

from core_functions.limiter import limiter
from core_functions.auth import get_user_role
from core_functions.user_database import get_user_database

router = APIRouter()

user_db, _ = get_user_database()

@router.delete(
    "/user/delete",
    tags=["Admin", "User"],
    description="A endpoint to delete a user. If you are an admin you can delete any user, as a normal user you can only delete your own account.",
    responses={
        200: {
            "description": "User was deleted successfully",
            "content": {
                "application/json": {
                    "example": {"status": "success"}
                }
            }
        },
        400: {
            "description": "Unauthorized. Invalid or missing API key",
            "content": {
                "application/json": {
                    "example": {"detail": "User deletion failed or user does not exist"}
                }
            }
        },
        401: {
            "description": "Unauthorized. Invalid or missing API key",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or missing API key"}
                }
            }
        },
        403: {
            "description": "You don't have the rights to delete that user",
            "content": {
                "application/json": {
                    "examples": {
                        "not_admin": {
                            "summary": "Normal user deleting another account",
                            "value": {"detail": "Admin access required for performing this action on other user's accounts."}
                        },
                        "admin_account_deletion_forbidden": {
                            "summary": "The admin account cannot be deleted",
                            "value": {"detail": "The admin account cannot be deleted."}
                        }
                    }
                }
            }
        }
    }
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