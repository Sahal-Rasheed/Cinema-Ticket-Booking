"""
Tests for POST /api/v1/movies/{movie_id}/seats/{seat_id}/hold

Covers:
  - Happy path: holding a free seat
  - Conflict: two users racing for the same seat
  - Same user trying to hold two seats
  - Holding the same seat in different movies should be independent
"""

import pytest
from httpx import AsyncClient

# mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


async def test_hold_seat_returns_session(client: AsyncClient):
    """
    Holding a free seat returns 201 with a valid session.
    """
    resp = await client.post(
        "/api/v1/movies/inception/seats/A1/hold",
        json={"user_id": "user-alice"},
    )

    assert resp.status_code == 201

    data = resp.json()
    assert data["seat_id"] == "A1"
    assert data["movie_id"] == "inception"
    assert "session_id" in data
    assert "expires_at" in data
    assert len(data["session_id"]) > 0


async def test_hold_already_held_seat_returns_409(client: AsyncClient):
    """
    A seat held by alice cannot be held by bob must return 409.
    """
    # alice holds the seat first
    first = await client.post(
        "/api/v1/movies/inception/seats/B2/hold",
        json={"user_id": "user-alice"},
    )
    assert first.status_code == 201

    # bob tries the same seat
    second = await client.post(
        "/api/v1/movies/inception/seats/B2/hold",
        json={"user_id": "user-bob"},
    )
    assert second.status_code == 409


async def test_different_seats_can_be_held_independently(client: AsyncClient):
    """
    Two users holding different seats should both succeed.
    """
    alice = await client.post(
        "/api/v1/movies/inception/seats/C1/hold",
        json={"user_id": "user-alice"},
    )
    bob = await client.post(
        "/api/v1/movies/inception/seats/C2/hold",
        json={"user_id": "user-bob"},
    )

    assert alice.status_code == 201
    assert bob.status_code == 201
    assert alice.json()["session_id"] != bob.json()["session_id"]  # different sessions


async def test_different_movies_same_seat_id_are_independent(client: AsyncClient):
    """
    Seat A1 in 'inception' and seat A1 in 'interstellar' are separate.
    """
    inception = await client.post(
        "/api/v1/movies/inception/seats/D1/hold",
        json={"user_id": "user-alice"},
    )
    interstellar = await client.post(
        "/api/v1/movies/interstellar/seats/D1/hold",
        json={"user_id": "user-bob"},
    )

    assert inception.status_code == 201
    assert interstellar.status_code == 201
    assert (
        inception.json()["session_id"] != interstellar.json()["session_id"]
    )  # different sessions
