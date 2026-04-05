from enum import StrEnum

from pydantic import BaseModel


class BookingStatus(StrEnum):
    HELD = "held"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Booking(BaseModel):
    id: str | None = None
    movie_id: str
    seat_id: str
    user_id: str
    status: BookingStatus = BookingStatus.HELD
    expires_at: str | None = None  # timestamp when the hold expires


class HoldSeatRequest(BaseModel):
    user_id: str


class HoldSeatResponse(BaseModel):
    session_id: str
    seat_id: str
    movie_id: str
    expires_at: str


class ConfirmSeatResponse(BaseModel):
    session_id: str
    seat_id: str
    movie_id: str
    user_id: str
    status: BookingStatus


class MovieResponse(BaseModel):
    id: str
    title: str
    rows: int
    seats_per_row: int
