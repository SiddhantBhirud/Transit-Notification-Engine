import requests
from google.transit import gtfs_realtime_pb2
from app.config import GTFS_RT_URL
import logging

logger = logging.getLogger(__name__)

def fetch_trip_updates() -> list[dict]:
    """
    Fetches live GTFS-RT trip updates from the configured feed URL.
    Returns a list of delay dicts for each affected trip.
    """
    try:
        response = requests.get(GTFS_RT_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch GTFS-RT feed: {e}")
        return []

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    delays = []

    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue

        trip_id = entity.trip_update.trip.trip_id
        route_id = entity.trip_update.trip.route_id

        for stop_time_update in entity.trip_update.stop_time_update:
            delay = 0

            if stop_time_update.HasField("arrival"):
                delay = stop_time_update.arrival.delay
            elif stop_time_update.HasField("departure"):
                delay = stop_time_update.departure.delay

            if delay > 0:
                delays.append({
                    "trip_id": trip_id,
                    "route_id": route_id,
                    "stop_id": stop_time_update.stop_id,
                    "delay_seconds": delay,
                })

    logger.info(f"Fetched {len(delays)} delayed trips from GTFS-RT feed")
    return delays