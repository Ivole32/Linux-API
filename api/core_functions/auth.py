from fastapi import HTTPException, Depends, Header
from api.database.user_database.user_database_old import get_user_database, UserRole

user_db, demo_api_key = get_user_database()

def verify_api_key(x_api_key: str = Header(demo_api_key), required_role: str = "user"):
    result = user_db.verify_api_key(x_api_key)
    
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    username, user_role = result
    
    if required_role == "admin" and user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"username": username, "role": user_role.value}

def get_user_role(required_role: str):
    def dependency(x_api_key: str = Header(demo_api_key)):
        return verify_api_key(x_api_key, required_role)
    return Depends(dependency)