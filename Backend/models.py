from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Owner(Base):
    __tablename__ = "owners"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    email        = Column(String, unique=True, index=True, nullable=False)
    phone        = Column(String, nullable=True)
    password     = Column(String, nullable=False)  # hashed
    created_at   = Column(DateTime, default=datetime.utcnow)

    shops        = relationship("Shop", back_populates="owner")


class Shop(Base):
    __tablename__ = "shops"

    id           = Column(Integer, primary_key=True, index=True)
    owner_id     = Column(Integer, ForeignKey("owners.id"), nullable=False)
    name         = Column(String, nullable=False)
    slug         = Column(String, unique=True, index=True, nullable=False)  # e.g. sharma-salon
    category     = Column(String, nullable=True)
    description  = Column(Text, nullable=True)
    address      = Column(String, nullable=True)
    services     = Column(Text, nullable=True)   # JSON string: [{"name":"Haircut","price":200}]
    open_time    = Column(String, default="09:00")
    close_time   = Column(String, default="21:00")
    work_days    = Column(String, default="Monday to Saturday")
    created_at   = Column(DateTime, default=datetime.utcnow)

    owner        = relationship("Owner", back_populates="shops")
    bookings     = relationship("Booking", back_populates="shop")


class Booking(Base):
    __tablename__ = "bookings"

    id              = Column(Integer, primary_key=True, index=True)
    shop_id         = Column(Integer, ForeignKey("shops.id"), nullable=False)
    customer_name   = Column(String, nullable=False)
    customer_phone  = Column(String, nullable=True)
    service         = Column(String, nullable=False)
    booking_date    = Column(String, nullable=False)   # e.g. "2025-04-06"
    booking_time    = Column(String, nullable=False)   # e.g. "3:00 PM"
    status          = Column(Enum("pending","confirmed","cancelled"), default="pending")
    note            = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    shop            = relationship("Shop", back_populates="bookings")