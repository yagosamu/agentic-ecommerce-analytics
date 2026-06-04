from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class Customer(BaseModel):
    customer_id: UUID
    name: str
    email: str
    city: str | None = None
    state: str | None = Field(default=None, min_length=2, max_length=2)
    segment: Literal["premium", "standard", "basic"] | None = None


class Product(BaseModel):
    product_id: UUID
    name: str
    category: str
    price: float = Field(gt=0)
    brand: str | None = None


class Order(BaseModel):
    order_id: UUID
    customer_id: UUID
    product_id: UUID
    qty: int = Field(ge=1, le=10)
    total: float = Field(ge=0)
    status: Literal["delivered", "shipped", "processing", "cancelled"]
    payment: Literal["pix", "credit_card", "boleto"]
    created_at: datetime | None = None


class Review(BaseModel):
    review_id: UUID
    order_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str
    sentiment: Literal["positive", "neutral", "negative"]
