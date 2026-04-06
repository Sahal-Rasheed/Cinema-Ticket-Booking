import pytest
import asyncio
import pytest_asyncio
import redis.asyncio as aioredis
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the entire test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def redis_client():
    """
    A real async Redis client for testing.
    """
    client = aioredis.Redis(host="localhost", port=6380, decode_responses=True)

    try:
        await client.ping()
    except Exception:
        pytest.skip("Redis not available")

    yield client

    # clean up after the test
    await client.flushdb()
    await client.aclose()


@pytest_asyncio.fixture()
async def client(redis_client):
    """
    A test client for the FastAPI app. This fixture also overrides,
    the app's default Redis client with the one from the `redis_client` fixture (testing redis instance),
    so that default redis instance is not used for testing purposees so no data is shared between testing and development.
    """
    # patch the global redis_client singleton to use the testing redis instance
    from adapters.redis import redis_client as app_redis

    original_client = app_redis.client

    app_redis.client = redis_client
    await app_redis.client.flushdb()

    from main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    # reset singleton reference to original after the test
    app_redis.client = original_client
