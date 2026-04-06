"""
Tests for DELETE /api/v1/sessions/{session_id}

Covers:
  - Happy path: releasing a held session returns 204
  - After release the seat is available again
  - Releasing a non-existent session returns 400
  - After release the seat disappears from the seat list
"""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.integration


async def _hold(
    client: AsyncClient, movie_id="inception", seat_id="A1", user_id="user-alice"
):
    resp = await client.post(
        f"/api/v1/movies/{movie_id}/seats/{seat_id}/hold",
        json={"user_id": user_id},
    )
    assert resp.status_code == 201
    return resp.json()


async def test_release_held_session_returns_204(client: AsyncClient):
    """
    Releasing a valid held session returns 204 No Content.
    """
    session = await _hold(client)

    resp = await client.delete(f"/api/v1/sessions/{session['session_id']}")
    assert resp.status_code == 204


async def test_released_seat_becomes_available_again(client: AsyncClient):
    """
    After Alice releases her hold, Bob should be able to hold the seat.
    """
    alice_session = await _hold(client, seat_id="B1", user_id="user-alice")

    await client.delete(f"/api/v1/sessions/{alice_session['session_id']}")

    bob_resp = await client.post(
        "/api/v1/movies/inception/seats/B1/hold",
        json={"user_id": "user-bob"},
    )
    assert bob_resp.status_code == 201


async def test_release_invalid_session_returns_400(client: AsyncClient):
    """
    Releasing a session that doesn't exist must return 400.
    """
    resp = await client.delete(
        "/api/v1/sessions/00000000",
    )
    assert resp.status_code == 400


async def test_released_seat_not_in_seat_list(client: AsyncClient):
    """
    After release, the seat must disappear from the movie's seat list.
    """
    session = await _hold(client, seat_id="C1")

    await client.delete(f"/api/v1/sessions/{session['session_id']}")

    seats = (await client.get("/api/v1/movies/inception/seats")).json()
    c1 = [s for s in seats if s["seat_id"] == "C1"]
    assert len(c1) == 0, "Released seat should not appear in the seat list"
