from pydantic import BaseModel


class Booking(BaseModel):
    id: str
    movie_id: str
    seat_id: str
    user_id: str | None
    status: str  # e.g., "held", "confirmed", "cancelled"
    expires_at: int | None  # timestamp when the hold expires
