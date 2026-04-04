import redis.asyncio as redis


class RedisClient:
    async def __init__(self, host="localhost", port=6379):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        if await self.client.ping():
            print("Connected to Redis successfully.")
        else:
            print("Failed to connect to Redis.")


redis_client = RedisClient()
