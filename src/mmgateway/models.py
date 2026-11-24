import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base
from .status import PaymentStatus, check_transition


class Provider(StrEnum):
    MPESA = "mpesa"
    ORANGE_MONEY = "orange_money"
    AIRTEL_MONEY = "airtel_money"


class Currency(StrEnum):
    USD = "USD"
    CDF = "CDF"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # The key the merchant sends with the request: the same key twice
    # returns the same payment instead of charging the customer again.
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True)
    merchant_reference: Mapped[str] = mapped_column(String(100))
    provider: Mapped[Provider] = mapped_column(Enum(Provider, native_enum=False, length=20))
    phone_number: Mapped[str] = mapped_column(String(20))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[Currency] = mapped_column(Enum(Currency, native_enum=False, length=3))
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False, length=20), default=PaymentStatus.PENDING
    )
    provider_reference: Mapped[str | None] = mapped_column(String(100), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def move_to(self, new_status: PaymentStatus) -> None:
        check_transition(self.status, new_status)
        self.status = new_status
