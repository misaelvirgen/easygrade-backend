import os
import stripe
from fastapi import APIRouter, Request, Header
from supabase import create_client

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            endpoint_secret
        )
    except Exception as e:
        return {"error": str(e)}

    print("Stripe event received:", event["type"])

    # Handle checkout completion
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session["customer_details"]["email"]

        supabase.table("profiles").update({"is_premium": True}).eq("email", email).execute()
        print("User upgraded:", email)

    return {"status": "success"}
