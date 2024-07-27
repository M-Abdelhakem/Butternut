import logging
import os
import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

load_dotenv('env_variables.env')

# Set up Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

stripe_router = APIRouter()

# Replace these with your actual Price IDs from Stripe
PRICE_IDS = {
    "basic": "price_1Pf16WRxdDFnvTGA2oIVCfeL",
    "premium": "price_1Pf16tRxdDFnvTGAMnPPLo2x",
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create checkout session route
@stripe_router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    try:
        data = await request.json()
        plan = data.get("plan")

        if plan not in PRICE_IDS:
            raise HTTPException(status_code=400, detail="Invalid plan")

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": PRICE_IDS[plan],
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url="http://0.0.0.0:8000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://0.0.0.0:8000/cancel",
        )
        logger.info(f"Checkout session created: {checkout_session.id}")
        return JSONResponse({"id": checkout_session.id})
    except stripe.error.StripeError as e:
        # Handle Stripe API errors
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Handle other errors
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Define the templates directory path
templates_directory = "templates"  # Adjust the path as necessary
templates = Jinja2Templates(directory=templates_directory)

# Success route
@stripe_router.get("/success")
async def success(request: Request):
    session_id = request.query_params.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)
    customer = stripe.Customer.retrieve(session.customer)
    return templates.TemplateResponse("success.html", {"request": request, "customer": customer})

# Cancel route
@stripe_router.get("/cancel")
async def cancel(request: Request):
    logger.info("Payment canceled")
    # Redirect to the account page with a red alert message
    return RedirectResponse(url="/account?message=payment_failed")

