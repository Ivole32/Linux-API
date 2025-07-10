from fastapi import HTTPException, Depends, Header
from core_functions.user_database import get_user_database, UserRole

user_db = get_user_database()

def verify_api_key(x_api_key: str = Header(...), required_role: str = "user"):
    result = user_db.verify_api_key(x_api_key)
    
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    username, user_role = result
    
    if required_role == "admin" and user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"username": username, "role": user_role.value}

def get_user_role(required_role: str):
    def dependency(x_api_key: str = Header(...)):
        return verify_api_key(x_api_key, required_role)
    return Depends(dependency)