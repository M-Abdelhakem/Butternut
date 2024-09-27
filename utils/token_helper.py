import jwt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from decouple import config
from fastapi import HTTPException, status

# Load configurations from .env file
SECRET_KEY = config("JWT_SECRET_KEY")
ALGORITHM = config("JWT_ALGORITHM", default="HS256")
EXPIRATION_TIME_MINUTES = config("JWT_EXPIRATION_TIME_MINUTES", default=30, cast=int)


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRATION_TIME_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
