"""
Tests for PUT /api/v1/sessions/{session_id}/confirm

Covers:
  - Happy path: confirming a held session
  - Confirming makes the seat show as confirmed in the seat list
  - A confirmed seat cannot be held by another user
  - Confirming a non-existent expired session fails
  - Confirming the same session twice is idempotent (seat stays confirmed)
"""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.integration


async def _hold(
    client: AsyncClient, movie_id="inception", seat_id="A1", user_id="user-alice"
):
    """
    Helper: hold a seat and return the session data.
    """
    resp = await client.post(
        f"/api/v1/movies/{movie_id}/seats/{seat_id}/hold",
        json={"user_id": user_id},
    )
    assert resp.status_code == 201, f"Hold failed: {resp.text}"
    return resp.json()


async def test_confirm_held_session_returns_200(client: AsyncClient):
    """
    Confirming a valid held session returns 200 with status=confirmed
    """
    session = await _hold(client)

    resp = await client.put(
        f"/api/v1/sessions/{session['session_id']}/confirm",
        json={"user_id": "user-alice"},
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["user_id"] == "user-alice"
    assert data["status"] == "confirmed"
    assert data["seat_id"] == "A1"
    assert data["movie_id"] == "inception"
    assert data["session_id"] == session["session_id"]


async def test_confirmed_seat_appears_in_seat_list(client: AsyncClient):
    """
    After confirming, the seat must appear as confirmed when listing seats.
    """
    session = await _hold(client, seat_id="D4")

    await client.put(
        f"/api/v1/sessions/{session['session_id']}/confirm",
        json={"user_id": "user-alice"},
    )

    seats_resp = await client.get("/api/v1/movies/inception/seats")
    assert seats_resp.status_code == 200

    seats = seats_resp.json()
    confirmed = [s for s in seats if s["seat_id"] == "D4"]

    assert len(confirmed) == 1
    assert confirmed[0]["status"] == "confirmed"


async def test_confirmed_seat_cannot_be_held_by_another_user(client: AsyncClient):
    """
    A confirmed seat is permanently taken — no one else can hold it.
    """
    session = await _hold(client, seat_id="E5")

    await client.put(
        f"/api/v1/sessions/{session['session_id']}/confirm",
        json={"user_id": "user-alice"},
    )

    second = await client.post(
        "/api/v1/movies/inception/seats/E5/hold",
        json={"user_id": "user-bob"},
    )
    assert second.status_code == 409


async def test_confirm_invalid_session_returns_400(client: AsyncClient):
    """
    Confirming a session ID that doesn't exist must return 400.
    """
    resp = await client.put(
        "/api/v1/sessions/00000000/confirm",
        json={"user_id": "user-alice"},
    )
    assert resp.status_code == 400


async def test_confirm_is_idempotent_within_session(client: AsyncClient):
    """
    Confirming the same session twice the seat stays confirmed. We just check the seat list stays correct.
    """
    session = await _hold(client, seat_id="C6")

    await client.put(
        f"/api/v1/sessions/{session['session_id']}/confirm",
        json={"user_id": "user-alice"},
    )

    await client.put(
        f"/api/v1/sessions/{session['session_id']}/confirm",
        json={"user_id": "user-alice"},
    )

    seats = (await client.get("/api/v1/movies/inception/seats")).json()
    c6 = next((s for s in seats if s["seat_id"] == "C6"), None)
    assert c6 is not None
    assert c6["status"] == "confirmed"
