import os
from fastapi import APIRouter, Cookie, HTTPException, Request, Body
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from database import DBManager
from utils.email_generation import PepperLLM
import boto3

class PromptRequest(BaseModel):
    prompt: str

sending_emails_router = APIRouter()
DB_Manager = DBManager()

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_directory = os.path.join(parent_directory, "templates")
templates = Jinja2Templates(directory=templates_directory)

ses_client = boto3.client(
    service_name="ses",
    region_name="us-west-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

@sending_emails_router.get("/send-email")
async def send_email(request: Request):
    return templates.TemplateResponse("send_email.html", {"request": request})

async def get_emails_customers_from_db(username: str):
    client = DB_Manager.check_user({"username": username})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    email_addresses = [customer["email"] for customer in client.get("customers", [])]
    customers = [customer for customer in client.get("customers", [])]
    return customers, email_addresses

async def get_business_context_from_db(username: str):
    business_context = DB_Manager.get_business_context(username)
    if not business_context:
        raise HTTPException(status_code=404, detail="Business context not found")
    return business_context

@sending_emails_router.post("/send-email")
async def send_email(
    username: str = Cookie(None),
    prompt_request: PromptRequest = Body(...)
):
    try:
        if not username:
            raise HTTPException(status_code=400, detail="Username cookie is missing")

        print(f"Username: {username}")
        print(f"Prompt: {prompt_request.prompt}")

        customers, email_addresses = await get_emails_customers_from_db(username)
        business_context = str(await get_business_context_from_db(username))

        # Generate email content using PepperLLM
        email_content = PepperLLM(
            business_context=business_context,
            customer=customers[0],  # Example customer, you can iterate over all customers
            prompt=prompt_request.prompt,
        )

        # Mock response to be sent back to the front-end
        generated_emails = {
            "generatedEmailShort": f"Short Email:\n{email_content}",
            "generatedEmailLong": f"Long Email:\n{email_content}",
            "generatedEmailFormal": f"Formal Email:\n{email_content}",
            "generatedEmailInformal": f"Informal Email:\n{email_content}",
        }

        return JSONResponse(content=generated_emails)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@sending_emails_router.post("/verify-email")
async def verify_email_identity(username: str = Cookie(None)):
    response = ses_client.verify_email_identity(EmailAddress=username)
    return RedirectResponse(url="/send-email")
