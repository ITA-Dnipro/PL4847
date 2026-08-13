import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    """
    Автоматично очищає кеш Django перед і після кожного тесту,
    щоб лічильники rate-limiting (throttling) не впливали на інші тести.
    """
    cache.clear()
    yield
    cache.clear()
