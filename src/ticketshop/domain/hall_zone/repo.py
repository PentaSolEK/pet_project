from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.ticketshop.domain.hall_zone.models import HallZone


async def get_hall_zone(session: AsyncSession, id_hall: int, id_ticket_type: int) -> HallZone | None:
    res = await session.exec(statement=select(HallZone).where(
        HallZone.id_hall == id_hall, HallZone.id_type == id_ticket_type))
    hall_ticket_type = res.first()
    if hall_ticket_type:
        return hall_ticket_type
    return None