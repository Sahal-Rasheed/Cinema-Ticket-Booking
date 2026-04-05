from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse

from handlers import booking_router
from adapters.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize redis client on startup
    await redis_client.connect()
    yield
    # close redis connection on shutdown
    await redis_client.close()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={
            "detail": "Internal server error",
            "error": exc.__class__.__name__,
        },
        status_code=500,
    )


@app.get("/")
async def root():
    return FileResponse("static/index.html", media_type="text/html", status_code=200)


app.include_router(booking_router, prefix="/api/v1")
