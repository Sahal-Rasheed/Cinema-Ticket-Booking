import time
from uuid import uuid4


from schemas.booking import Booking
from adapters.redis import redis_client as redis

HOLD_TLL = 120  # 2 minutes


async def hold_seat(booking: Booking) -> tuple[bool, Booking | None]:
    """
    Hold a seat for a user for a specified time (default 10 minutes).
    """
    id = str(uuid4())
    now = int(time.time())
    seat_key = f"seat:{booking.movie_id}:{booking.seat_id}"
    session_key = f"session:{id}"

    booking.id = id
    booking.status = "held"

    ok = await redis.client.set(
        seat_key,
        booking.model_dump(),
        nx=True,  # only set if the key does not already exist (lock ~ atomic o/p)
        ex=HOLD_TLL,
    )
    # seat is already held by someone else
    if not ok:
        return False, None

    # reverse mapping to get booking details from session key
    await redis.client.set(
        session_key,
        seat_key,
        ex=HOLD_TLL,
    )
    booking.expires_at = now + HOLD_TLL

    return True, booking

# TODO: confirm booking, cancel booking, release seat, get booking details