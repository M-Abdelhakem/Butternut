import os
from fastapi import APIRouter, Cookie, HTTPException, Request, Body
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from database import DBManager
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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

def PepperLLM(business_context, customer, prompt):
    response = client.chat.completions.create(model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": business_context},
        {
            "role": "system",
            "content": "Using the customer data, customize the first paragraph from what you can infer (not directly injecting the data into the paragraph because that would sound like a human did not write it). For instance, what kind of income can you infer from the occupation, living in X City? What about his gender from his name?. Write it in such a way that when someone reads it, it thinks you are just filling in the blanks. For instance, you should never directly mention his job or where he/she lives.",
        },
        {
            "role": "system",
            "content": "You are an email marketer hired to write a drip campaign for a business. The goal of the drip campaign is to convert the customer that receives the email into a paying customer by giving them information and value. Here is the customer data: "
            + str(customer)
            + " Let’s write an email that is personalized for this specific customer.",
        },
        {"role": "user", "content": prompt},
    ])
    return response.choices[0].message.content.strip()

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

        # Ensure we have at least 4 customers
        if len(customers) < 4:
            raise HTTPException(status_code=400, detail="Not enough customers to generate 4 versions")

        # Generate email content using PepperLLM
        email_content_short = PepperLLM(
            business_context=business_context,
            customer=customers[0],
            prompt=prompt_request.prompt + " short version",
        )

        email_content_long = PepperLLM(
            business_context=business_context,
            customer=customers[1],
            prompt=prompt_request.prompt + " long version",
        )

        email_content_formal = PepperLLM(
            business_context=business_context,
            customer=customers[2],
            prompt=prompt_request.prompt + " formal version",
        )

        email_content_informal = PepperLLM(
            business_context=business_context,
            customer=customers[3],
            prompt=prompt_request.prompt + " informal version",
        )

        # Mock response to be sent back to the front-end
        generated_emails = {
            "generatedEmailShort": email_content_short,
            "generatedEmailLong": email_content_long,
            "generatedEmailFormal": email_content_formal,
            "generatedEmailInformal": email_content_informal,
        }

        return JSONResponse(content=generated_emails)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@sending_emails_router.post("/verify-email")
async def verify_email_identity(username: str = Cookie(None)):
    response = ses_client.verify_email_identity(EmailAddress=username)
    return RedirectResponse(url="/send-email")
