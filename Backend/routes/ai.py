from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Shop
from schemas import ChatMessage
from dotenv import load_dotenv
import anthropic, os, json

load_dotenv()

router = APIRouter(prefix="/api/chat", tags=["AI Chat"])

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@router.post("/")
def chat(data: ChatMessage, db: Session = Depends(get_db)):
    # Load shop data
    shop = db.query(Shop).filter(Shop.slug == data.shop_slug).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    # Parse services
    try:
        services = json.loads(shop.services) if shop.services else []
    except:
        services = []

    services_text = "\n".join([f"- {s['name']}: ₹{s['price']}" for s in services]) or "No services listed"

    # System prompt with shop data baked in
    system_prompt = f"""You are a friendly AI booking assistant for "{shop.name}".

SHOP INFO:
- Name: {shop.name}
- Category: {shop.category or 'General'}
- Address: {shop.address or 'Not provided'}
- Working Hours: {shop.open_time} to {shop.close_time}
- Working Days: {shop.work_days}
- Description: {shop.description or ''}

SERVICES & PRICES:
{services_text}

YOUR JOB:
1. Greet the customer warmly
2. Help them choose a service
3. Ask for their preferred date and time
4. Ask for their name and phone number
5. Confirm the booking details clearly
6. End with a confirmation message

RULES:
- Be friendly, short and clear. Use emojis naturally.
- Only book within working hours ({shop.open_time} - {shop.close_time})
- Only offer services listed above
- When booking is confirmed, respond with a JSON block at the end like this:
  BOOKING_CONFIRMED:{{"customer_name":"...","customer_phone":"...","service":"...","booking_date":"...","booking_time":"..."}}
- Respond in the same language the customer uses (Hindi or English)
"""

    # Build message history
    messages = []
    for msg in (data.history or []):
        if msg.get("role") in ["user", "assistant"] and msg.get("content"):
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": data.message})

    # Call Anthropic
    response = client.messages.create(
        model      = "claude-opus-4-6",
        max_tokens = 500,
        system     = system_prompt,
        messages   = messages
    )

    reply = response.content[0].text

    # Check if booking was confirmed in the reply
    booking_data = None
    if "BOOKING_CONFIRMED:" in reply:
        try:
            json_part = reply.split("BOOKING_CONFIRMED:")[1].split("\n")[0].strip()
            booking_data = json.loads(json_part)
            # Clean reply text — remove the JSON part
            reply = reply.split("BOOKING_CONFIRMED:")[0].strip()
        except:
            pass

    return {
        "reply": reply,
        "booking_confirmed": booking_data is not None,
        "booking_data": booking_data
    }