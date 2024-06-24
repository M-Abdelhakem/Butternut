import os
from fastapi import APIRouter, Cookie, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from database import DBManager
from utils.email_generation import PepperLLM
from schemas.email_content import EmailContent
import boto3

sending_emails_router = APIRouter()
DB_Manager = DBManager()

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_directory = os.path.join(parent_directory, "templates")
templates = Jinja2Templates(directory=templates_directory)


ses_client = boto3.client(
    service_name="ses",
    region_name="us-west-1",  # os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


@sending_emails_router.get("/send-email")
async def send_email(request: Request):
    return templates.TemplateResponse("send_email.html", {"request": request})


async def get_emails_customers_from_db(username: str):
    # Fetch the client record from the database based on the username
    # print(f"Fetching emails and customers for username: {username}")
    client = DB_Manager.check_user({"username": username})
    # print(f"Client data: {client}")
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    # Extract the list of email addresses from the customers key of the client record
    email_addresses = [customer["email"] for customer in client.get("customers", [])]
    customers = [customer for customer in client.get("customers", [])]
    return customers, email_addresses


async def get_business_context_from_db(username: str):
    # print(f"Fetching business context for username: {username}")
    business_context = DB_Manager.get_business_context(username)
    # print(f"Business context: {business_context}")
    if not business_context:
        raise HTTPException(status_code=404, detail="Business context not found")
    return business_context


@sending_emails_router.post("/send-email")
async def send_email(
    username: str = Cookie(None),
    prompt: str = Form(...),
):
    try:
        if not username:
            raise HTTPException(status_code=400, detail="Username cookie is missing")

        # print(f"Username: {username}")

        customers, email_addresses = await get_emails_customers_from_db(username)
        business_context = str(await get_business_context_from_db(username))

        for customer in customers:
            # Generate email content using PepperLLM
            email_content = PepperLLM(
                business_context=business_context,
                customer=customer,
                prompt=prompt,
            )

            # Separate the email_content into subject and body (Assuming the email_content has a delimiter for this example)
            subject, body = email_content.split("\n\n", 1)
            subject = subject.replace("Subject: ", "")

            response = ses_client.send_email(
                Source=username,
                Destination={"ToAddresses": [customer["email"]]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                },
            )

        return {"message": "Email sent successfully"}
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@sending_emails_router.post("/verify-email")
async def verify_email_identity(username: str = Cookie(None)):
    response = ses_client.verify_email_identity(EmailAddress=username)
    print("Verify Response: ", response)
    # Redirect the user to "/send-email"
    return RedirectResponse(url="/send-email")