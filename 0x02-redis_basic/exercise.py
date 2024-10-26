#!/usr/bin/env python3

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator that counts how many times a method is called."""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function to increment the call count and call
        the original method.
        """
        key = method.__qualname__

        self._redis.incr(key)

        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs of a function."""

    @wraps(method)
    def wrapper(self, *args):
        """Wrapper to record inputs and outputs in Redis."""

        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))

        output = method(self, *args)

        self._redis.rpush(output_key, str(output))

        return output

    return wrapper


class Cache:
    def __init__(self):
        """Initialize the Cache class with a Redis client
        and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store the data in Redis with a randomly generated key."""
        key = str(uuid.uuid4())

        self._redis.set(key, data)

        return key

    def get_type(self, key: str) -> Union[str, bytes, None]:
        """Retrieve data from Redis."""
        return self._redis.get(key)

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
