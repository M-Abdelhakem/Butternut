from fastapi import HTTPException
from pydantic import BaseModel, validator
import re


class UserCredentials(BaseModel):
    username: str
    password: str

    @validator("username")
    def username_must_be_valid_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise HTTPException(
                status_code=400,
                detail="Invalid email format. Please enter a valid email address.",
            )
        return v

    @validator("password")
    def validate_password(cls, value):
        regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()-_+=])[A-Za-z\d!@#$%^&*()-_+=]{8,}$"

        if not re.match(regex, value):
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long and contain at least one lowercase letter, one uppercase letter, one digit, one special character",
            )
        return value
