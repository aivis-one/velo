# =============================================================================
# VELO Backend — Redis Connection
# =============================================================================
#
# HOW IT WORKS:
#   redis-py (with hiredis parser) provides an async client that maintains
#   a connection pool to Redis, similar to SQLAlchemy's engine.
#
# LIFECYCLE:
#   App startup  -> init_redis()  -> creates the client + connection pool
#   App running  -> get_redis()   -> returns the shared client instance
#   App shutdown -> close_redis() -> closes all connections cleanly
#
#   This is managed by FastAPI's lifespan context in main.py.
#
# WHY A GLOBAL CLIENT?
#   Redis connections are cheap but not free. Creating a new client per
#   request would waste resources. One shared client with a connection
#   pool handles thousands of concurrent requests efficiently.
#
# USAGE IN ENDPOINTS:
#   from app.core.redis import get_redis
#
#   @router.get("/cached-data")
#   async def get_data():
#       redis = get_redis()
#       value = await redis.get("my-key")
# =============================================================================

import redis.asyncio as aioredis

from app.core.config import settings

# Global Redis client instance. Initialized at app startup.
_redis_client: aioredis.Redis | None = None


async def init_redis() -> None:
    """Initialize the Redis client. Called once at app startup.

    Creates a connection pool that handles connection reuse,
    reconnection on failure, and connection limits.
    """
    global _redis_client
    _redis_client = aioredis.from_url(  # type: ignore[no-untyped-call]
        settings.redis_url,
        # decode_responses=True: Redis stores everything as bytes.
        # This setting auto-decodes to str, so you get "hello"
        # instead of b"hello". Saves .decode() calls everywhere.
        decode_responses=True,
    )


async def close_redis() -> None:
    """Close the Redis client. Called once at app shutdown.

    Closes all connections in the pool. Without this, connections
    would leak on app restart (especially in development with
    --reload).
    """
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


def get_redis() -> aioredis.Redis:
    """Get the shared Redis client instance.

    Raises RuntimeError if called before init_redis() — this means
    something is trying to use Redis before the app fully started.
    """
    if _redis_client is None:
        raise RuntimeError(
            "Redis client not initialized. "
            "Ensure init_redis() is called at app startup."
        )
    return _redis_client
