"""
Concurrency Test

Fires N concurrent requests at the same seat and asserts exactly one wins.
"""

import pytest
import asyncio
from httpx import AsyncClient


pytestmark = pytest.mark.integration


async def test_exactly_one_winner_under_concurrency(client: AsyncClient):
    """
    10000 concurrent users race for the same seat.
    Exactly one must succeed (201), all others must fail (409).
    """
    NUM_USERS = 10000

    async def try_hold(user_num: int):
        resp = await client.post(
            "/api/v1/movies/inception/seats/A1/hold",
            json={"user_id": f"user-{user_num}"},
        )
        return resp.status_code

    status_codes = await asyncio.gather(*[try_hold(i) for i in range(NUM_USERS)])

    successes = [s for s in status_codes if s == 201]
    conflicts = [s for s in status_codes if s == 409]

    assert len(successes) == 1, (
        f"Expected exactly 1 success (201), got {len(successes)}. "
        f"This means the Redis lock is broken."
    )
    assert len(conflicts) == NUM_USERS - 1, (
        f"Expected {NUM_USERS - 1} conflicts (409), got {len(conflicts)}."
    )


async def test_multiple_seats_all_winners_are_distinct(client: AsyncClient):
    """
    50 users each race for one of 5 seats (10 users per seat).
    Each seat must have exactly one winner.
    """
    SEATS = ["A1", "A2", "A3", "A4", "A5"]
    USERS_PER_SEAT = 10

    async def try_hold(seat: str, user_num: int):
        resp = await client.post(
            f"/api/v1/movies/interstellar/seats/{seat}/hold",
            json={"user_id": f"user-{seat}-{user_num}"},
        )
        return seat, resp.status_code

    tasks = [try_hold(seat, u) for seat in SEATS for u in range(USERS_PER_SEAT)]
    all_results = await asyncio.gather(*tasks)

    from collections import defaultdict

    by_seat: dict[str, list[int]] = defaultdict(list)
    for seat, code in all_results:
        by_seat[seat].append(code)

    for seat in SEATS:
        codes = by_seat[seat]
        wins = codes.count(201)
        assert wins == 1, (
            f"Seat {seat}: expected 1 winner, got {wins}. Full results: {codes}"
        )
