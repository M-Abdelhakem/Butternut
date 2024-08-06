import logging
import os
import stripe
from fastapi import APIRouter, Request, HTTPException, Cookie
from fastapi.responses import JSONResponse
from database import DBManager
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

# Set up Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

stripe_router = APIRouter()
DB_Manager = DBManager()

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_directory = os.path.join(parent_directory, "templates")
templates = Jinja2Templates(directory=templates_directory)

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
async def create_checkout_session(request: Request, username: str = Cookie(None)):
    if not username:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    user_profile = DB_Manager.check_user({"username": username})
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")

    stripe_customer_id = user_profile.get("stripe_customer_id")
    full_name = f"{user_profile.get('profile_info', {}).get('first_name', 'Unknown')} {user_profile.get('profile_info', {}).get('last_name', 'User')}"

    if not stripe_customer_id:
        # Create a new Stripe customer if it doesn't exist
        try:
            stripe_customer = stripe.Customer.create(
                email=username,
                description=full_name,
            )
            stripe_customer_id = stripe_customer.id

            # Update the user's profile with the new Stripe customer ID
            DB_Manager.add_stripe_id(username, stripe_customer_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    try:
        data = await request.json()
        plan = data.get("plan")

        if plan not in PRICE_IDS:
            raise HTTPException(status_code=400, detail="Invalid plan")

        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": PRICE_IDS[plan],
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url="http://peppercorn.email/success",
            cancel_url="http://peppercorn.email/cancel",
        )
        return JSONResponse({"id": checkout_session.id})
    except stripe.error.StripeError as e:
        # Handle Stripe API errors
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Handle other errors
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Success route
@stripe_router.get("/success")
async def success(request: Request, username: str = Cookie(None)):
    DB_Manager.update_subscription(username)
    return templates.TemplateResponse("success.html", {"request": request})


# Cancel route
@stripe_router.get("/cancel")
async def cancel(request: Request):
    logger.info("Payment canceled")
    # Redirect to the account page with a red alert message
    return RedirectResponse(url="/account?message=payment_failed")
