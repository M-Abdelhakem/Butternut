import os
from fastapi import APIRouter, Cookie, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from database import DBManager
from schemas.user_profile import ProfileInfo

profile_router = APIRouter()
DB_Manager = DBManager()

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_directory = os.path.join(parent_directory, "templates")
templates = Jinja2Templates(directory=templates_directory)


@profile_router.get("/profile-info")
async def profile_info_page(request: Request, username: str = Cookie(None)):
    if not username:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    return templates.TemplateResponse("profile_info.html", {"request": request})


@profile_router.post("/submit-profile-info")
async def submit_profile_info(profile_info: ProfileInfo, username: str = Cookie(None)):
    if not username:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    # Update user profile in the database
    user_data = profile_info.model_dump()
    DB_Manager.update_user_profile(username, user_data)

    return {"message": "Profile information updated successfully"}


@profile_router.get("/account")
async def account_page(request: Request, username: str = Cookie(None)):
    if not username:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    user_profile = DB_Manager.check_user({"username": username})
    # print(user_profile)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        "account_m.html", {"request": request, "user_profile": user_profile}
    )
