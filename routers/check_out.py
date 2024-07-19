from fastapi import APIRouter, HTTPException
import stripe
import os

stripe_router = APIRouter()

# Set your Stripe API key
stripe.api_key = os.getenv('STRIPE_API_KEY')

@stripe_router.post("/create-checkout-session")
async def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'subscription',
                    },
                    'unit_amount': 100,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8000/success',
            cancel_url='http://localhost:8000/cancel',
        )
        # session.id = 'prod_QRzKeoE5E4LUda'
        return {"id": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@stripe_router.get("/success")
async def success():
    return "Payment successful!"

@stripe_router.get("/cancel")
async def cancel():
    return "Payment canceled!"
