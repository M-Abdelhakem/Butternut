from fastapi import Request, HTTPException
from jose import jwt, JWTError
from utils.token_helper import verify_token

async def get_current_user_from_token(request: Request):
    token = request.cookies.get("Authorization")
    if token is None:
        raise HTTPException(status_code=401, detail="Unauthorized access: No token provided")
    
    # Remove 'Bearer ' prefix if present
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]
    
    try:
        payload = verify_token(token)
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
