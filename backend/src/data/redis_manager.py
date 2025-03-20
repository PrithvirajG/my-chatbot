# from redis import Redis
# import os
# from backend.src.data.session_manager import SessionManager
#
# # redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379"))
# redis_client = Redis.from_url("redis://127.0.0.1:6379")
# print( "Redis Client Exists: ", redis_client.exists("some key"))
# session_manager = SessionManager(redis_client)
#
#

import redis
from ..core.config_loader import config

redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0, decode_responses=True)

def set_key(key: str, value: str, ex: int = None):
    """Set a key-value pair in Redis with optional expiration."""
    redis_client.set(key, value, ex=ex)

def get_key(key: str):
    """Retrieve a value by key from Redis."""
    return redis_client.get(key)

def delete_key(key: str):
    """Delete a key from Redis."""
    redis_client.delete(key)