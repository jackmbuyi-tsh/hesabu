"""The contract every mobile money provider adapter follows.

The gateway only talks to providers through this interface, so a mock
adapter (used in development and tests, since the build machine has no
internet) and a real one can be swapped without touching the rest.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from ..status import PaymentStatus


@dataclass(frozen=True)
class InitiateResult:
    provider_reference: str
    status: PaymentStatus


class ProviderAdapter(ABC):
    name: str

    @abstractmethod
    def initiate_payment(
        self, *, phone_number: str, amount: Decimal, currency: str, reference: str
    ) -> InitiateResult:
        """Ask the provider to push a payment request to the customer's phone."""

    @abstractmethod
    def check_status(self, provider_reference: str) -> PaymentStatus:
        """Ask the provider where a payment stands."""

    @abstractmethod
    def verify_callback(self, headers: dict[str, str], body: bytes) -> bool:
        """Check that a callback really comes from the provider."""
