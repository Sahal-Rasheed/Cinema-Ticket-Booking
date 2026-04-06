from schemas.booking import Booking
from store.redis import hold_seat, release_seat, confirm_booking, bookings_for_movie


async def list_bookings(movie_id: str) -> list[Booking]:
    """
    List all current bookings (both held and confirmed).
    """
    return await bookings_for_movie(movie_id)


async def book_seat(booking: Booking) -> tuple[bool, Booking | None]:
    """
    Attempt to book a seat by first holding it and then confirming the booking.
    """
    success, held_booking = await hold_seat(booking)
    if not success:
        return False, None

    # print(f"Seat held successfully: {held_booking}")
    return True, held_booking


async def confirm_seat(session_id: str, user_id: str) -> bool:
    """
    Confirm a booking by changing its status to "confirmed".
    """
    return await confirm_booking(session_id, user_id)


async def unbook_seat(session_id: str) -> bool:
    """
    Release a held seat, making it available for others.
    """
    return await release_seat(session_id)
