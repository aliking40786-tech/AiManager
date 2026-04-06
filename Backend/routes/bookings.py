from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import Booking, Shop
from schemas import CreateBooking, BookingResponse, UpdateBookingStatus
from auth import decode_token
from typing import List

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


def get_owner_id(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["owner_id"]


# Customer creates a booking
@router.post("/", response_model=BookingResponse)
def create_booking(data: CreateBooking, db: Session = Depends(get_db)):
    shop = db.query(Shop).filter(Shop.slug == data.shop_slug).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    booking = Booking(
        shop_id        = shop.id,
        customer_name  = data.customer_name,
        customer_phone = data.customer_phone,
        service        = data.service,
        booking_date   = data.booking_date,
        booking_time   = data.booking_time,
        note           = data.note,
        status         = "pending"
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


# Owner gets all bookings for their shop
@router.get("/shop/{shop_slug}", response_model=List[BookingResponse])
def get_shop_bookings(shop_slug: str, db: Session = Depends(get_db), owner_id: int = Depends(get_owner_id)):
    shop = db.query(Shop).filter(Shop.slug == shop_slug, Shop.owner_id == owner_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found or not yours")

    bookings = db.query(Booking).filter(Booking.shop_id == shop.id).order_by(Booking.created_at.desc()).all()
    return bookings


# Owner updates booking status (confirm / cancel)
@router.patch("/{booking_id}", response_model=BookingResponse)
def update_booking(booking_id: int, data: UpdateBookingStatus, db: Session = Depends(get_db), owner_id: int = Depends(get_owner_id)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Verify this booking belongs to owner's shop
    shop = db.query(Shop).filter(Shop.id == booking.shop_id, Shop.owner_id == owner_id).first()
    if not shop:
        raise HTTPException(status_code=403, detail="Not your booking")

    if data.status not in ["confirmed", "cancelled", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    booking.status = data.status
    db.commit()
    db.refresh(booking)
    return booking


# Owner deletes a booking
@router.delete("/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db), owner_id: int = Depends(get_owner_id)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    shop = db.query(Shop).filter(Shop.id == booking.shop_id, Shop.owner_id == owner_id).first()
    if not shop:
        raise HTTPException(status_code=403, detail="Not your booking")

    db.delete(booking)
    db.commit()
    return {"message": "Booking deleted"}