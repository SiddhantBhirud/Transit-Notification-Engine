import pytest
from unittest.mock import patch, MagicMock
from app.tasks import poll_transit_feed

MOCK_DELAYS = [
    {"trip_id": "trip_1", "route_id": "38", "stop_id": "stop_1", "delay_seconds": 300}
]

@patch("app.tasks.send_alert")
@patch("app.tasks.cache_delays")
@patch("app.tasks.get_cached_delays")
@patch("app.tasks.fetch_trip_updates")
def test_poll_sends_alert_on_cache_miss(mock_fetch, mock_get_cache, mock_cache, mock_alert):
    """On a cache miss, poll_transit_feed caches data and fires an alert."""
    mock_fetch.return_value = MOCK_DELAYS
    mock_get_cache.return_value = None  # cache miss

    poll_transit_feed()

    mock_cache.assert_called_once_with("38", MOCK_DELAYS)
    mock_alert.delay.assert_called_once_with(
        route_id="38",
        trip_id="trip_1",
        delay_seconds=300,
    )

@patch("app.tasks.send_alert")
@patch("app.tasks.cache_delays")
@patch("app.tasks.get_cached_delays")
@patch("app.tasks.fetch_trip_updates")
def test_poll_skips_alert_on_cache_hit(mock_fetch, mock_get_cache, mock_cache, mock_alert):
    """On a cache hit, poll_transit_feed skips caching and sends no alert."""
    mock_fetch.return_value = MOCK_DELAYS
    mock_get_cache.return_value = MOCK_DELAYS  # cache hit

    poll_transit_feed()

    mock_cache.assert_not_called()
    mock_alert.delay.assert_not_called()

@patch("app.tasks.fetch_trip_updates")
def test_poll_handles_empty_feed(mock_fetch):
    """poll_transit_feed handles an empty feed gracefully."""
    mock_fetch.return_value = []
    result = poll_transit_feed()
    assert result is None