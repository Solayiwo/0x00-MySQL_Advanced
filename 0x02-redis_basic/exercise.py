#!/usr/bin/env python3

import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    def __init__(self):
        """Initialize the Cache class with a Redis client
        and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store the data in Redis with a randomly generated key."""
        key = str(uuid.uuid4())

        self._redis.set(key, data)

        return key

    def get(
        self, key: str, fn: Optional[Callable] = None
    ) -> Optional[Union[str, bytes, int, float]]:
        """
        Retrieve data from Redis and optionally apply a conversion function.

        Args:
            key (str): The key to retrieve data from Redis.
            fn (Callable, optional): A function to convert the data to
            a desired type.

        Returns:
            Optional[Union[str, bytes, int, float]]: The retrieved data or
            None if the key does not exist.
        """
        data = self._redis.get(key)

        if data is None:
            return None

        if fn:
            return fn(data)

        return data

    def get_str(self, key: str) -> Optional[str]:
        """Retrieve data from Redis and convert it to a UTF-8 string."""
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """Retrieve data from Redis and convert it to an integer."""
        return self.get(key, fn=int)
