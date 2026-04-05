import redis.asyncio as redis


class RedisClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        self.client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        if await self.client.ping():
            print("Connected to Redis successfully!")
        else:
            raise print("Failed to connect to Redis")

    async def close(self):
        await self.client.aclose()


redis_client = RedisClient()
