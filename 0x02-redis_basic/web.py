import redis
import requests
from typing import Callable
from functools import wraps

redis_client = redis.Redis()


def cache_page(method: Callable) -> Callable:
    """Decorator to cache the response of a function."""

    @wraps(method)
    def wrapper(url: str) -> str:
        cached_response = redis_client.get(url)
        if cached_response:
            redis_client.incr(f"count:{url}")
            return cached_response.decode('utf-8')

        response = method(url)

        redis_client.setex(url, 10, response)

        redis_client.incr(f"count:{url}")

        return response

    return wrapper


@cache_page
def get_page(url: str) -> str:
    """Fetch the HTML content of a given URL."""
    response = requests.get(url)
    return response.text


# Example usage
if __name__ == "__main__":
    url = (
        "http://slowwly.robertomurray.co.uk/delay/1000/"
        "url/http://example.com"
    )

    print(get_page(url))
