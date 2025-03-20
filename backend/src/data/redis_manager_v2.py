import asyncio
import json
import traceback
from typing import Any, Optional

from redis import asyncio as aioredis
from redis.asyncio import BlockingConnectionPool
from redis.commands.json.path import Path
from redis.commands.json import JSON

from loguru import logger

class RedisInterface:
    def __init__(self, slack_client, host="127.0.0.1", port=6379, db=0, max_connections=1000, connection_timeout=5):
        self.slack_client = slack_client
        self.redis_client: Optional[aioredis.Redis] = None
        self.json_client: Optional[JSON] = None
        self.host = host
        self.port = port
        self.db = db
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout

    async def connect(self):
        """
        Function to establish connection with the redis server.
        """
        try:
            pool = BlockingConnectionPool(max_connections=self.max_connections, timeout=self.connection_timeout,
                                          host=self.host, port=self.port, db=self.db)

            self.redis_client = await aioredis.Redis(connection_pool=pool)
            # self.redis_client = await aioredis.from_url(f'redis://{self.host}:{self.port}/{self.db}')
            logger.info("[Redis Interface] Initialized Redis Client Successfully ...")

            self.json_client = JSON(self.redis_client)
            logger.info("[Redis Interface] Initialized Redis JSON Client Successfully!")
        except Exception as e:
            err = f"[Redis Interface] Exception occurred while connecting to redis: {str(e)}, " \
                  f"{traceback.format_exc()}"
            logger.exception(err)
            if self.slack_client:
                asyncio.ensure_future(
                    self.slack_client.send_slack_message(err, severity_level=2, action_needed="Investigation needed")
                )

    async def set_data(self, key, value, expiry=None):
        """
        Set a key-value pair in Redis with an optional expiry time.

        :param key: The key to set.
        :param value: The value to associate with the key.
        :param expiry: The expiry time in seconds (optional).
        """
        try:
            if self.redis_client is None:
                raise ValueError("[Redis Interface] Redis Client has not been initialized !!!")

            if expiry is not None:
                await self.redis_client.setex(key, expiry, value)
            else:
                await self.redis_client.set(key, value)
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while setting data to redis: {str(e)}")

    async def get_data(self, key):
        """
        Retrieve the value associated with a key in Redis.

        :param key: The key to retrieve.
        :return: The value associated with the key, or None if the key does not exist.
        """
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while getting data from redis: {str(e)}",
                             extra={'device_id': key})
            return None

    async def remove_data(self, key):
        """
        Retrieve the value associated with a key in Redis.

        :param key: The key to retrieve.
        :return: The value associated with the key, or None if the key does not exist.
        """
        try:
            return await self.redis_client.delete(key)
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while removing data to redis: {str(e)}")
            return None

    async def add_data_to_list(self, key, value):
        """
        Add a value to a set in Redis.

        :param key: The key of the set.
        :param value: The value to add to the set.
        """
        try:
            await self.redis_client.sadd(key, value)
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while adding to set in redis: {str(e)}")

    async def remove_data_from_list(self, key, value):
        """
        Remove a value from a set in Redis.

        :param key: The key of the set.
        :param value: The value to remove from the set.
        """
        try:
            await self.redis_client.srem(key, value)
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while removing from set in redis: {str(e)}")

    async def get_list(self, key):
        """
        Get all the values in a set in Redis.

        :param key: The key of the set.
        :return: The set of values.
        """
        try:
            set_members = await self.redis_client.smembers(key)
            result_set = set()

            for member in set_members:
                if member is not None:
                    raw_str = member.decode('utf-8')
                    try:
                        parsed_value = json.loads(raw_str)
                    except json.JSONDecodeError:
                        parsed_value = raw_str
                else:
                    parsed_value = None

                result_set.add(parsed_value)

            return result_set
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while getting set from redis: {str(e)}")
            return None

    async def check_in_list(self, key, value):
        """
        Check if a value is in a set in Redis.

        :param key: The key of the set.
        :param value: The value to check in the set.
        :return: True if the value is in the set, False otherwise.
        """
        try:
            return await self.redis_client.sismember(key, value)
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while checking in set in redis: {str(e)}")
            return False

    async def get_keys(self, keys):
        """
        Fetch multiple keys from Redis in a single operation.

        :param keys: A list of keys to fetch from Redis
        :return: A dictionary with keys and their corresponding values (None for non-existent keys)
        """
        try:
            # Perform MGET operation
            values = await self.redis_client.mget(keys)

            # Combine keys with their values
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        # Attempt to deserialize the value (assuming it's stored as JSON)
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        # If it's not JSON, store the raw value
                        result[key] = value.decode('utf-8') if isinstance(value, bytes) else value
                else:
                    result[key] = None

            return result

        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while fetching multiple keys from Redis: {str(e)}")
            # Return None for all keys in case of an error
            return {key: None for key in keys}

    async def set_hash_field(self, key: str, field: str, value: Any, expiry: Optional[int] = None) -> bool:
        """
        Set a field in a hash in Redis.

        :param key: The key of the hash.
        :param field: The field to set.
        :param value: The value to set.
        :param expiry: The expiry time in seconds (optional).
        :return: True if the field was successfully set, False otherwise.
        """
        try:
            value = json.dumps(value)
            await self.redis_client.hset(key, field, value)
            if expiry is not None:
                await self.redis_client.expire(key, expiry)
            return True
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while setting hash field in redis: {str(e)}")
            return False

    async def get_hash_field(self, key: str, field: str) -> Optional[Any]:
        """
        Get a field from a hash in Redis.

        :param key: The key of the hash.
        :param field: The field to get.
        :return: The value associated with the field, or None if the field does not exist.
        """
        try:
            result = await self.redis_client.hget(key, field)
            if result is not None:
                try:
                    deserialized_result = json.loads(result)
                except json.JSONDecodeError:
                    deserialized_result = result.decode('utf-8') if isinstance(result, bytes) else result
            else:
                deserialized_result = None
            return deserialized_result
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while getting hash field from redis: {str(e)}",
                             extra={'device_id': key})
            return None

    async def delete_hash_field(self, key: str, field: str) -> bool:
        """
        Delete a field from a hash in Redis.

        :param key: The key of the hash.
        :param field: The field to delete.
        :return: True if the field was successfully deleted, False otherwise.
        """
        try:
            await self.redis_client.hdel(key, field)
            return True
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while deleting hash field from redis: {str(e)}")
            return False

    async def get_all_hash_fields(self, key: str) -> Optional[dict]:
        """
        Get all fields and values from a hash in Redis.

        :param key: The key of the hash.
        :return: A dictionary of all fields and values in the hash, or None if the hash does not exist.
        """
        try:
            result = await self.redis_client.hgetall(key)
            deserialized_result = {}
            for k, v in result.items():
                if k is not None:
                    try:
                        deserialized_key = json.loads(k)
                    except json.JSONDecodeError:
                        deserialized_key = k.decode('utf-8') if isinstance(k, bytes) else k
                else:
                    deserialized_key = None

                if v is not None:
                    try:
                        deserialized_value = json.loads(v)
                    except json.JSONDecodeError:
                        deserialized_value = v.decode('utf-8') if isinstance(v, bytes) else v
                else:
                    deserialized_value = None

                deserialized_result[deserialized_key] = deserialized_value
            return deserialized_result
        except Exception as e:
            logger.exception(f"[Redis Interface] Exception occurred while getting all hash fields from redis: {str(e)}")
            return None