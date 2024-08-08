from datetime import timedelta, datetime, timezone
import os
from fastapi import APIRouter, Cookie, HTTPException, Request, Body
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import DBManager
from utils.email_generation import PepperLLM
from schemas.email_content import PromptBody
import boto3
import requests
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse

sending_emails_router = APIRouter()
DB_Manager = DBManager()

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_directory = os.path.join(parent_directory, "templates")
templates = Jinja2Templates(directory=templates_directory)


ses_client = boto3.client(
    service_name="ses",
    region_name=os.getenv("AWS_REGION"),
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
    prompt: PromptBody = Body(...),
):

    subscription_start_date = DB_Manager.get_subscription_start_date(username)

    if subscription_start_date:
        # Check if the subscription is still valid (within one month)
        current_date = datetime.now(timezone.utc)
        subscription_validity_period = timedelta(days=30)

        if current_date - subscription_start_date < subscription_validity_period:
            print("Subscription is still valid.")
        else:
            print("Subscription has expired. Please resubscribe.")
            return "Subscription has expired. Please resubscribe."
    else:
        print("User is not subscribed. Please subscribe.")
        return "User is not subscribed. Please subscribe."

    try:
        print("Sending email...")
        if not username:
            raise HTTPException(status_code=400, detail="Username cookie is missing")

        print(f"Username: {username}")
        print(f"Prompt: {prompt.prompt}")

        customers, email_addresses = await get_emails_customers_from_db(username)
        business_context = str(await get_business_context_from_db(username))

        for customer in customers:
            # Generate email content using PepperLLM
            email_content = PepperLLM(
                business_context=business_context,
                customer=customer,
                prompt=prompt.prompt,
            )
            # For different versions, TODO but need to decide which one is gonna be sent
            # email_content_short = PepperLLM(
            #     business_context=business_context,
            #     customer=customer,
            #     prompt=prompt + " short version",
            # )

            # email_content_long = PepperLLM(
            #     business_context=business_context,
            #     customer=customer,
            #     prompt=prompt + " long version",
            # )

            # email_content_formal = PepperLLM(
            #     business_context=business_context,
            #     customer=customer,
            #     prompt=prompt + " formal version",
            # )

            # email_content_informal = PepperLLM(
            #     business_context=business_context,
            #     customer=customer,
            #     prompt=prompt + " informal version",
            # )

            # Mock response to be sent back to the front-end
            generated_emails = {
                "generatedEmailShort": email_content,
                "generatedEmailLong": email_content,
                "generatedEmailFormal": email_content,
                "generatedEmailInformal": email_content,
            }

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

        return JSONResponse(content=generated_emails)

    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@sending_emails_router.post("/verify-email")
async def verify_email_identity(username: str):
    response = ses_client.verify_email_identity(EmailAddress=username)
    print("Verify Response: ", response)
    # Redirect the user to "/send-email"
    return RedirectResponse(url="/customer-list")

# Add a route to serve the tracking pixel
@sending_emails_router.get("/track_email/{email_id}")
async def track_email(email_id: str, request: Request):
    ip_address = request.client.host
    user_agent = request.headers.get('user-agent')
    timestamp = datetime.now(timezone.utc)

    # Get location info from ipapi
    response = requests.get(f'http://ip-api.com/json/{ip_address}')
    location_data = response.json()

    # Log the email open event in your database or any storage
    DB_Manager.log_email_open(
        email_id=email_id,
        ip_address=ip_address,
        user_agent=user_agent,
        location=location_data,
        opened_at=timestamp
    )

    # Serve the tracking pixel
    return FileResponse('static/transparent_pixel.png', media_type='image/png')
