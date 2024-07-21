from pydantic import BaseModel


class ProfileInfo(BaseModel):
    first_name: str
    last_name: str
    address: str
    city: str
    country: str
    postal_code: str
