from fastapi.responses import Response
from fastapi import APIRouter, Path, status
from fastapi.exceptions import HTTPException

from schemas.booking import (
    Booking,
    MovieResponse,
    HoldSeatRequest,
    HoldSeatResponse,
    ConfirmSeatResponse,
)
from services.booking import list_bookings, book_seat, confirm_seat, unbook_seat


booking_router = APIRouter(prefix="", tags=["bookings"])


@booking_router.get(
    "/movies",
    response_model=list[MovieResponse],
    status_code=status.HTTP_200_OK,
)
async def list_movies_handler() -> list[MovieResponse]:
    movies = [
        MovieResponse(id="inception", title="Inception", rows=5, seats_per_row=8),
        MovieResponse(id="the-matrix", title="The Matrix", rows=4, seats_per_row=6),
        MovieResponse(id="interstellar", title="Interstellar", rows=7, seats_per_row=5),
        MovieResponse(
            id="the-dark-knight", title="The Dark Knight", rows=6, seats_per_row=7
        ),
    ]
    return movies


@booking_router.get(
    "/movies/{movie_id}/seats",
    response_model=list[Booking],
    status_code=status.HTTP_200_OK,
)
async def list_bookings_handler(
    movie_id: str = Path(..., description="ID of the movie"),
) -> list[Booking]:
    return await list_bookings(movie_id)


@booking_router.post(
    "/movies/{movie_id}/seats/{seat_id}/hold",
    response_model=HoldSeatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def hold_seat_handler(
    payload: HoldSeatRequest,
    movie_id: str = Path(..., description="ID of the movie"),
    seat_id: str = Path(..., description="ID of the seat to book"),
) -> HoldSeatResponse:
    booking = Booking(user_id=payload.user_id, movie_id=movie_id, seat_id=seat_id)
    success, held_booking = await book_seat(booking)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seat is already held or booked",
        )

    return HoldSeatResponse(
        session_id=held_booking.id,
        seat_id=held_booking.seat_id,
        movie_id=held_booking.movie_id,
        expires_at=held_booking.expires_at,
    )


@booking_router.put(
    "/sessions/{session_id}/confirm",
    response_model=ConfirmSeatResponse,
    status_code=status.HTTP_200_OK,
)
async def confirm_seat_handler(
    payload: HoldSeatRequest,
    session_id: str = Path(..., description="Session ID of the held booking"),
) -> ConfirmSeatResponse:
    success, booking = await confirm_seat(session_id, payload.user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to confirm booking. Session may have expired.",
        )

    return ConfirmSeatResponse(
        session_id=booking.id,
        seat_id=booking.seat_id,
        movie_id=booking.movie_id,
        user_id=payload.user_id,
        status=booking.status,
    )


@booking_router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def release_seat_handler(
    session_id: str = Path(
        ..., description="Session ID of the held booking to release"
    ),
) -> Response:
    success = await unbook_seat(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to release booking. Session may have expired.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
