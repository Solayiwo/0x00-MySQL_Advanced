#!/usr/bin/env python3

import redis
import uuid
from typing import Union


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
