"""A minimal in-process stand-in for a provider.

Every payment starts as pending and stays there. Realistic behaviour
(delays, duplicate or out-of-order callbacks, failures, signatures,
reconciliation files) is still to be built.
"""

import uuid
from decimal import Decimal

from ..status import PaymentStatus
from .base import InitiateResult, ProviderAdapter


class MockProvider(ProviderAdapter):
    def __init__(self, name: str):
        self.name = name
        self._payments: dict[str, PaymentStatus] = {}

    def initiate_payment(
        self, *, phone_number: str, amount: Decimal, currency: str, reference: str
    ) -> InitiateResult:
        provider_reference = f"{self.name}-{uuid.uuid4().hex[:12]}"
        self._payments[provider_reference] = PaymentStatus.PENDING
        return InitiateResult(provider_reference, PaymentStatus.PENDING)

    def check_status(self, provider_reference: str) -> PaymentStatus:
        return self._payments[provider_reference]

    def verify_callback(self, headers: dict[str, str], body: bytes) -> bool:
        raise NotImplementedError("Callback signatures are not simulated yet.")
