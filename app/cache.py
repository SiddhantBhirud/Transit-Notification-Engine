import json
import logging
import redis
from app.config import REDIS_URL, CACHE_TTL_SECONDS

logger = logging.getLogger(__name__)

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def make_cache_key(route_id: str) -> str:
    """Generates a consistent Redis key for a given route."""
    return f"transit:route:{route_id}"

def get_cached_delays(route_id: str) -> list[dict] | None:
    """
    Returns cached delay data for a route if it exists.
    Returns None if cache miss.
    """
    key = make_cache_key(route_id)
    try:
        data = redis_client.get(key)
        if data:
            logger.info(f"Cache HIT for route {route_id}")
            return json.loads(data)
        logger.info(f"Cache MISS for route {route_id}")
        return None
    except redis.RedisError as e:
        logger.error(f"Redis error on GET for route {route_id}: {e}")
        return None

def cache_delays(route_id: str, delays: list[dict]) -> None:
    """
    Stores delay data for a route in Redis with a TTL.
    After TTL expires, the next request will hit the API again.
    """
    key = make_cache_key(route_id)
    try:
        redis_client.setex(key, CACHE_TTL_SECONDS, json.dumps(delays))
        logger.info(f"Cached {len(delays)} delays for route {route_id} (TTL={CACHE_TTL_SECONDS}s)")
    except redis.RedisError as e:
        logger.error(f"Redis error on SET for route {route_id}: {e}")

def clear_cache(route_id: str) -> None:
    """Manually clears cached data for a route."""
    key = make_cache_key(route_id)
    try:
        redis_client.delete(key)
        logger.info(f"Cache cleared for route {route_id}")
    except redis.RedisError as e:
        logger.error(f"Redis error on DELETE for route {route_id}: {e}")