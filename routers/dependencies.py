from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from utils.token_helper import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# Dependency to verify and extract the username from the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username
