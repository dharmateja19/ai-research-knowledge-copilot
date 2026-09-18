from app.redis_service import (
    redis_client,
    set_cache,
    get_cache
)


redis_client.ping()

print("Redis connected successfully!")

set_cache(
    "test:key",
    "Hello Redis",
    expire=60
)

value = get_cache("test:key")

print("Cached value:", value)