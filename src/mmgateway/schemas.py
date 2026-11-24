import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from .models import Currency, Provider
from .status import PaymentStatus


class PaymentCreate(BaseModel):
    merchant_reference: str = Field(min_length=1, max_length=100)
    provider: Provider
    phone_number: str = Field(pattern=r"^\+243\d{9}$", examples=["+243812345678"])
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: Currency


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant_reference: str
    provider: Provider
    phone_number: str
    amount: Decimal
    currency: Currency
    status: PaymentStatus
    provider_reference: str | None
    created_at: datetime
