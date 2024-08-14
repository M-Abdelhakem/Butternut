import secrets
from typing import Dict, List
import bcrypt
from fastapi import (
    APIRouter,
    Body,
    Form,
    HTTPException,
    Request,
    status,
    Cookie,
    Response,
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from schemas.business_context import BusinessContext
from database import DBManager
from schemas.user_credentials import UserCredentials, UserCredentialsLogin
from routers.email_sending import ses_client
import os

login_router = APIRouter()
DB_Manager = DBManager()

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_directory = os.path.join(parent_directory, "templates")
templates = Jinja2Templates(directory=templates_directory)


# Endpoint for main screen
@login_router.get("/")
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


# Endpoints for user registration
@login_router.get("/register")
async def main_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@login_router.post("/register")
async def register_user(user: UserCredentials):
    # Check if username already exists
    if DB_Manager.check_user({"username": user.username}):
        raise HTTPException(status_code=400, detail="username already exists")

    # Insert new user into the database
    DB_Manager.insert_user({"username": user.username, "password": user.password})

    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    return response


# Endpoints for user login
@login_router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@login_router.post("/login")
async def login_user(user: UserCredentialsLogin):
    # Check if username exists
    existing_user = DB_Manager.check_user({"username": user.username})
    if not existing_user:
        raise HTTPException(status_code=401, detail="User doesn't exist")

    # Validate password
    valid_user = DB_Manager.validate_user(
        {"username": user.username, "password": user.password}
    )
    if not valid_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Check logged-in status
    if existing_user.get("logged-in", False):
        redirect_url = "/customer-list"
    else:
        redirect_url = "/business-card"

    # If login successful, set user credentials as cookies
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="username", value=user.username)
    response.set_cookie(key="password", value=user.password)

    return response


# Endpoint for customer list
@login_router.get("/customer-list")
async def customer_list(
    request: Request, username: str = Cookie(None), password: str = Cookie(None)
):
    if username is None or password is None:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    existing_user = DB_Manager.validate_user(
        {"username": username, "password": password}
    )
    if not existing_user:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    customers = existing_user.get("customers", [])
    return templates.TemplateResponse(
        "customer_list.html",
        {"request": request, "customer_data": customers},
    )


@login_router.post("/delete-customers")
async def delete_customers(customer_ids: Dict[str, List[str]] = Body(...)):
    if not customer_ids:
        raise HTTPException(status_code=400, detail="No customer IDs provided")

    # Extract the list of customer_ids (emails) from the dictionary
    customer_list = customer_ids.get("customer_ids")
    print(customer_list)
    # Logic to delete customers from the database using customer_ids
    # Example:
    result = DB_Manager.delete_customers(customer_list)

    if result:
        return {"message": "Customers deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete customers")
    # return RedirectResponse(url="/customer-list", status_code=303)


@login_router.get("/business-card")
async def business_card(
    request: Request, username: str = Cookie(None), password: str = Cookie(None)
):
    if username is None or password is None:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    existing_user = DB_Manager.validate_user(
        {"username": username, "password": password}
    )
    if not existing_user:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    logged_in = existing_user.get("logged-in", False)
    return templates.TemplateResponse(
        "business_card.html", {"request": request, "logged_in": logged_in}
    )


@login_router.post("/submit-business-card")
async def save_business_context(
    request: Request, context: BusinessContext, username: str = Cookie(None)
):
    if username is None:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    user = DB_Manager.check_user({"username": username})
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    if not user.get("logged-in", False):
        DB_Manager.save_business_context(username, context.dict())
        ses_client.verify_email_identity(EmailAddress=username)
        DB_Manager.clients_collection.update_one(
            {"username": username}, {"$set": {"logged-in": True}}
        )

    return RedirectResponse(url="/customer-list", status_code=303)


@login_router.get("/forget-password")
async def forget_password_form(request: Request):
    return templates.TemplateResponse("forget_password.html", {"request": request})


@login_router.post("/forget-password")
async def forget_password(username: str = Form(...)):
    user = DB_Manager.check_user({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = secrets.token_urlsafe(32)
    DB_Manager.save_password_reset_token(username, token)

    reset_link = f"http://peppercorn.email/reset-password?token={token}"
    email_subject = "Password Reset Request"
    email_body = f"Click the link to reset your password: {reset_link}"

    ses_client.send_email(
        Source="modestantonny@gmail.com",  # noreply email should be here
        Destination={"ToAddresses": [username]},
        Message={
            "Subject": {"Data": email_subject},
            "Body": {"Text": {"Data": email_body}},
        },
    )

    return {"message": "Password reset email sent"}


### Step 2: Create an endpoint for resetting the password


@login_router.get("/reset-password")
async def reset_password_form(request: Request, token: str):
    return templates.TemplateResponse(
        "reset_password.html", {"request": request, "token": token}
    )


@login_router.post("/reset-password")
async def reset_password(token: str = Form(...), new_password: str = Form(...)):
    username = DB_Manager.get_username_by_token(token)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
    DB_Manager.update_password(username, hashed_password)
    DB_Manager.delete_password_reset_token(token)

    return RedirectResponse(url="/login", status_code=303)


@login_router.get("/saved_copies")
async def saved_copies(request: Request):
    return templates.TemplateResponse("saved_copies.html", {"request": request})
