import json
import os
import redis

r = redis.StrictRedis.from_url(os.getenv("CELERY_BROKER_URL"))


def get_cached_data(cache_key):
    """
    Get data from cache if available, else fetch from database and cache it
    """
    cached_data = r.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    return None


def cache_data(cache_key, data):
    """
    Cache data in Redis
    """

    # cache for 10 minutes
    r.set(cache_key, json.dumps(data), ex=600)
