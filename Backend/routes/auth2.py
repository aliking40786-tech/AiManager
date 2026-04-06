from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Owner
from schemas import RegisterOwner, LoginRequest, TokenResponse
from auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(data: RegisterOwner, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(Owner).filter(Owner.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    owner = Owner(
        name     = data.name,
        email    = data.email,
        phone    = data.phone,
        password = hash_password(data.password)
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)

    token = create_token({"owner_id": owner.id, "email": owner.email})
    return TokenResponse(access_token=token, user_type="owner", owner_id=owner.id)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    owner = db.query(Owner).filter(Owner.email == data.email).first()

    if not owner or not verify_password(data.password, owner.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"owner_id": owner.id, "email": owner.email})
    return TokenResponse(access_token=token, user_type="owner", owner_id=owner.id)