from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import Shop
from schemas import CreateShop, ShopResponse
from auth import decode_token
import json, re

router = APIRouter(prefix="/api/shop", tags=["Shop"])


def get_owner_id(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["owner_id"]


def make_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug


@router.post("/create", response_model=ShopResponse)
def create_shop(data: CreateShop, db: Session = Depends(get_db), owner_id: int = Depends(get_owner_id)):
    slug = make_slug(data.name)

    # Make slug unique if taken
    base_slug = slug
    count = 1
    while db.query(Shop).filter(Shop.slug == slug).first():
        slug = f"{base_slug}-{count}"
        count += 1

    services_json = json.dumps([s.dict() for s in data.services]) if data.services else "[]"

    shop = Shop(
        owner_id    = owner_id,
        name        = data.name,
        slug        = slug,
        category    = data.category,
        description = data.description,
        address     = data.address,
        services    = services_json,
        open_time   = data.open_time,
        close_time  = data.close_time,
        work_days   = data.work_days
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


@router.get("/{slug}", response_model=ShopResponse)
def get_shop(slug: str, db: Session = Depends(get_db)):
    shop = db.query(Shop).filter(Shop.slug == slug).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop


@router.get("/owner/my-shops", response_model=list[ShopResponse])
def my_shops(db: Session = Depends(get_db), owner_id: int = Depends(get_owner_id)):
    return db.query(Shop).filter(Shop.owner_id == owner_id).all()