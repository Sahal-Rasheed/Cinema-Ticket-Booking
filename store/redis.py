from datetime import datetime, timedelta, timezone
from uuid import uuid4


from schemas.booking import Booking, BookingStatus
from adapters.redis import redis_client as redis

HOLD_TTL = 120  # 2 minutes


async def hold_seat(booking: Booking) -> tuple[bool, Booking | None]:
    """
    Hold a seat for a user for a specified time (default 2 minutes).
    """
    id = str(uuid4())
    now = datetime.now(timezone.utc)
    seat_key = f"seat:{booking.movie_id}:{booking.seat_id}"
    session_key = f"session:{id}"

    booking.id = id
    booking.status = BookingStatus.HELD

    ok = await redis.client.set(
        seat_key,
        booking.model_dump_json(),
        nx=True,  # only set if the key does not already exist (lock ~ atomic o/p)
        ex=HOLD_TTL,
    )
    # seat is already held by someone else
    if not ok:
        return False, None

    # reverse mapping to get booking details from session key
    await redis.client.set(
        session_key,
        seat_key,
        ex=HOLD_TTL,
    )
    booking.expires_at = (now + timedelta(seconds=HOLD_TTL)).isoformat()

    return True, booking


async def confirm_booking(session_id: str, user_id: str) -> tuple[bool, Booking | None]:
    """
    Confirm a booking by changing its status to "confirmed".
    """
    session_key = f"session:{session_id}"
    seat_key = await redis.client.get(session_key)
    if not seat_key:
        return False, None  # session expired

    booking_data_json = await redis.client.get(seat_key)
    if not booking_data_json:
        return False, None  # seat hold expired

    # persist the booking by removing ttl
    await redis.client.persist(seat_key)
    await redis.client.persist(session_key)

    # update booking status and user_id (confirm the booking)
    booking = Booking.model_validate_json(booking_data_json)
    booking.status = BookingStatus.CONFIRMED
    booking.user_id = user_id
    await redis.client.set(seat_key, booking.model_dump_json())
    return True, booking


async def release_seat(session_id: str) -> bool:
    """
    Release a held seat, making it available for others.
    """
    session_key = f"session:{session_id}"
    seat_key = await redis.client.get(session_key)
    if not seat_key:
        return False  # session expired

    booking_data_json = await redis.client.get(seat_key)
    if not booking_data_json:
        return False  # seat hold expired

    # delete both keys to release the seat, only after lock identifier matches (safety check)
    if Booking.model_validate_json(booking_data_json).id != session_id:
        print(
            f"Session ID mismatch for release: expected {session_id}, got {booking_data_json['id']}"
        )
        return False
    await redis.client.delete(seat_key, session_key)
    return True


async def bookings_for_movie(movie_id: str) -> list[Booking]:
    """
    List all current bookings (both held and confirmed) for a given movie.
    """
    pattern = f"seat:{movie_id}:*"
    bookings: list[Booking] = []

    # use `scan_iter` over `keys` cmd
    # - `keys` cmd blocks redis while it runs.
    # - `scan_iter`` pages through in batches safely.
    async for seat_key in redis.client.scan_iter(pattern):
        booking_data_json = await redis.client.get(seat_key)
        if not booking_data_json:
            continue
        try:
            bookings.append(Booking.model_validate_json(booking_data_json))
        except Exception as ex:
            print(f"Error parsing booking data for key {seat_key}: {ex}")
            continue

    return bookings
