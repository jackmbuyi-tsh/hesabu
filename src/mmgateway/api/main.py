import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import __version__
from ..db import get_session
from ..models import Payment
from ..providers import get_adapter
from ..schemas import PaymentCreate, PaymentOut

app = FastAPI(title="Mobile Money Gateway", version=__version__)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(
    body: PaymentCreate,
    session: SessionDep,
    response: Response,
    idempotency_key: Annotated[str, Header(min_length=1, max_length=100)],
) -> Payment:
    existing = session.scalar(select(Payment).where(Payment.idempotency_key == idempotency_key))
    if existing is not None:
        # Same key: return the first payment, never charge twice.
        # (Checking that the body matches the first request is still to do.)
        response.status_code = status.HTTP_200_OK
        return existing

    payment = Payment(idempotency_key=idempotency_key, **body.model_dump())
    result = get_adapter(body.provider).initiate_payment(
        phone_number=body.phone_number,
        amount=body.amount,
        currency=body.currency.value,
        reference=body.merchant_reference,
    )
    payment.provider_reference = result.provider_reference
    session.add(payment)
    session.commit()
    return payment


@app.get("/payments/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: uuid.UUID, session: SessionDep) -> Payment:
    payment = session.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Payment not found")
    return payment
