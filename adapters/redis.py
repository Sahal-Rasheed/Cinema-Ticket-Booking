import os

import redis.asyncio as redis


class RedisClient:
    def __init__(self):
        self.client = None
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))

    async def connect(self):
        if self.client is None:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                decode_responses=True,
            )
        if not await self.client.ping():
            raise ConnectionError(
                f"Failed to connect to Redis at {self.host}:{self.port}"
            )

    async def close(self):
        if self.client is not None:
            await self.client.aclose()
            self.client = None


redis_client = RedisClient()
