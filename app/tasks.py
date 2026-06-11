import logging
from celery import Celery
from app.config import REDIS_URL, DELAY_THRESHOLD_SECONDS
from app.gtfs_client import fetch_trip_updates
from app.cache import get_cached_delays, cache_delays
from app.notifier import send_delay_alert

logger = logging.getLogger(__name__)

celery_app = Celery(
    "transit",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
)

@celery_app.task(name="tasks.poll_transit_feed")
def poll_transit_feed():
    """
    Main polling task. Called every 30s by Celery Beat.
    Fetches live GTFS-RT data, checks cache per route,
    and triggers alerts for any delays over the threshold.
    """
    logger.info("Polling GTFS-RT feed...")

    # Fetch all current delays from the live feed
    all_delays = fetch_trip_updates()

    if not all_delays:
        logger.info("No delays found in feed.")
        return

    # Group delays by route_id
    routes = {}
    for delay in all_delays:
        route_id = delay["route_id"]
        if route_id not in routes:
            routes[route_id] = []
        routes[route_id].append(delay)

    # For each route, check cache before processing
    for route_id, delays in routes.items():
        cached = get_cached_delays(route_id)

        if cached is not None:
            # Cache hit — skip external processing for this route
            logger.info(f"Using cached data for route {route_id}, skipping reprocess.")
            continue

        # Cache miss — process fresh data and store it
        cache_delays(route_id, delays)

        # Check each delay against threshold and fire alerts
        for delay in delays:
            if delay["delay_seconds"] >= DELAY_THRESHOLD_SECONDS:
                send_alert.delay(
                    route_id=delay["route_id"],
                    trip_id=delay["trip_id"],
                    delay_seconds=delay["delay_seconds"],
                )

@celery_app.task(name="tasks.send_alert")
def send_alert(route_id: str, trip_id: str, delay_seconds: int):
    """
    Sends a delay alert via SNS.
    Runs as a separate Celery task so alert sending
    doesn't block the main polling loop.
    """
    logger.info(f"Sending alert for route {route_id}, delay {delay_seconds}s")
    send_delay_alert(route_id, trip_id, delay_seconds)