import json
import pytest
from unittest.mock import MagicMock, patch
from app.cache import get_cached_delays, cache_delays, make_cache_key

MOCK_DELAYS = [
    {"trip_id": "trip_1", "route_id": "38", "stop_id": "stop_1", "delay_seconds": 300}
]

@patch("app.cache.redis_client")
def test_cache_miss_returns_none(mock_redis):
    """When no data is cached, get_cached_delays returns None."""
    mock_redis.get.return_value = None
    result = get_cached_delays("38")
    assert result is None
    mock_redis.get.assert_called_once_with("transit:route:38")

@patch("app.cache.redis_client")
def test_cache_hit_returns_data(mock_redis):
    """When data is cached, get_cached_delays returns parsed list."""
    mock_redis.get.return_value = json.dumps(MOCK_DELAYS)
    result = get_cached_delays("38")
    assert result == MOCK_DELAYS

@patch("app.cache.redis_client")
def test_cache_delays_stores_with_ttl(mock_redis):
    """cache_delays calls setex with the correct key and data."""
    cache_delays("38", MOCK_DELAYS)
    args = mock_redis.setex.call_args[0]
    assert args[0] == "transit:route:38"
    assert json.loads(args[2]) == MOCK_DELAYS