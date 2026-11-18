
import os

import redis
from dotenv import load_dotenv


load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise ValueError("REDIS_URL is missing from .env file")


redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def get_redis_client():
    """Return Redis client."""
    return redis_client


def test_redis_connection():
    """Test Redis server connection."""
    return redis_client.ping()
