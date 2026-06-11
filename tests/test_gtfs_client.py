import pytest
from unittest.mock import MagicMock, patch
from app.gtfs_client import fetch_trip_updates


def make_mock_feed():
    """Builds a fake GTFS-RT feed with one delayed trip."""
    mock_stop_time = MagicMock()
    mock_stop_time.stop_id = "stop_1"
    mock_stop_time.HasField.side_effect = lambda f: f == "arrival"
    mock_stop_time.arrival.delay = 300

    mock_trip_update = MagicMock()
    mock_trip_update.trip.trip_id = "trip_1"
    mock_trip_update.trip.route_id = "38"
    mock_trip_update.stop_time_update = [mock_stop_time]

    mock_entity = MagicMock()
    mock_entity.HasField.return_value = True
    mock_entity.trip_update = mock_trip_update

    mock_feed = MagicMock()
    mock_feed.entity = [mock_entity]
    return mock_feed


@patch("app.gtfs_client.gtfs_realtime_pb2.FeedMessage")
@patch("app.gtfs_client.requests.get")
def test_fetch_trip_updates_returns_delays(mock_get, mock_feed_class):
    """fetch_trip_updates parses delays from a valid GTFS-RT response."""
    mock_response = MagicMock()
    mock_response.content = b"fake-protobuf-bytes"
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    mock_feed_class.return_value = make_mock_feed()

    result = fetch_trip_updates()

    assert len(result) == 1
    assert result[0]["route_id"] == "38"
    assert result[0]["delay_seconds"] == 300


@patch("app.gtfs_client.requests.get")
def test_fetch_trip_updates_handles_request_error(mock_get):
    """fetch_trip_updates returns empty list on network error."""
    mock_get.side_effect = Exception("Network error")
    result = fetch_trip_updates()
    assert result == []