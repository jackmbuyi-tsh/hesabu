"""Payment lifecycle.

    pending ──► succeeded
       │
       ├──► failed
       └──► expired

A payment only moves forward. Once it has a final status it never changes,
whatever a provider's callback says later.
"""

from enum import StrEnum


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXPIRED = "expired"

    @property
    def is_final(self) -> bool:
        return self is not PaymentStatus.PENDING


ALLOWED_TRANSITIONS: dict[PaymentStatus, frozenset[PaymentStatus]] = {
    PaymentStatus.PENDING: frozenset(
        {PaymentStatus.SUCCEEDED, PaymentStatus.FAILED, PaymentStatus.EXPIRED}
    ),
    PaymentStatus.SUCCEEDED: frozenset(),
    PaymentStatus.FAILED: frozenset(),
    PaymentStatus.EXPIRED: frozenset(),
}


class InvalidTransition(ValueError):
    pass


def check_transition(current: PaymentStatus, new: PaymentStatus) -> None:
    if new not in ALLOWED_TRANSITIONS[current]:
        raise InvalidTransition(f"Cannot move a payment from {current} to {new}.")
