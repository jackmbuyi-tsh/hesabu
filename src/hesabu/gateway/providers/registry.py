from functools import lru_cache

from ..models import Provider
from .base import ProviderAdapter
from .mock import MockProvider


@lru_cache
def get_adapter(provider: Provider) -> ProviderAdapter:
    # Only mock adapters exist for now. Real ones plug in here later.
    return MockProvider(provider.value)
