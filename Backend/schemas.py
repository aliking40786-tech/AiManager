from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ─── AUTH ────────────────────────────────────────────

class RegisterOwner(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str
    user_type: str = "owner"   # "owner" or "customer"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: str
    owner_id: Optional[int] = None

# ─── SHOP ────────────────────────────────────────────

class ServiceItem(BaseModel):
    name: str
    price: int

class CreateShop(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    services: Optional[List[ServiceItem]] = []
    open_time: Optional[str] = "09:00"
    close_time: Optional[str] = "21:00"
    work_days: Optional[str] = "Monday to Saturday"

class ShopResponse(BaseModel):
    id: int
    name: str
    slug: str
    category: Optional[str]
    description: Optional[str]
    address: Optional[str]
    services: Optional[str]   # raw JSON string
    open_time: str
    close_time: str
    work_days: str

    class Config:
        from_attributes = True

# ─── BOOKING ─────────────────────────────────────────

class CreateBooking(BaseModel):
    shop_slug: str
    customer_name: str
    customer_phone: Optional[str] = None
    service: str
    booking_date: str
    booking_time: str
    note: Optional[str] = None

class BookingResponse(BaseModel):
    id: int
    shop_id: int
    customer_name: str
    customer_phone: Optional[str]
    service: str
    booking_date: str
    booking_time: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class UpdateBookingStatus(BaseModel):
    status: str   # "confirmed" | "cancelled"

# ─── CHAT ────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str
    shop_slug: str
    history: Optional[List[dict]] = []   # [{"role":"user","content":"..."}]