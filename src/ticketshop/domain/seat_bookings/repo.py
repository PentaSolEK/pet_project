from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.ticketshop.domain.seat_bookings.models import SeatBooking


async def list_occupied_for_concert(session: AsyncSession, concert_id: int) -> list[SeatBooking]:
    res = await session.exec(select(SeatBooking).where(SeatBooking.id_concert == concert_id))
    return list(res.all())


async def count_for_zone(session: AsyncSession, concert_id: int, id_hall_zone: int) -> int:
    res = await session.exec(
        select(SeatBooking).where(
            SeatBooking.id_concert == concert_id,
            SeatBooking.id_hall_zone == id_hall_zone,
        )
    )
    return len(list(res.all()))


async def create_bookings(
    session: AsyncSession,
    *,
    concert_id: int,
    id_hall_zone: int,
    seats: list[tuple[int, int]],
    id_sale: int | None = None,
) -> list[SeatBooking]:
    created = []
    for row_num, seat_num in seats:
        sb = SeatBooking(
            id_concert=concert_id,
            id_hall_zone=id_hall_zone,
            row_num=row_num,
            seat_num=seat_num,
            id_sale=id_sale,
        )
        session.add(sb)
        created.append(sb)
    await session.flush()
    return created
