import logging
import os
import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

load_dotenv('env_variables.env')

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


@stripe_router.get("/success")
async def success():
    return {"message": "Payment successful"}


@stripe_router.get("/cancel")
async def cancel():
    return {"message": "Payment canceled"}
