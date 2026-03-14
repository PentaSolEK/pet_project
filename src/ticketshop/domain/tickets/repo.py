from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.ticketshop.domain.tickets.models import Tickets


async def get_ticket(session: AsyncSession, id_concert: int, id_hall_zone: int):
    res = await session.exec(select(Tickets).where(Tickets.id_concert == id_concert,
                                                   Tickets.id_hall_zone == id_hall_zone))
    ticket = res.first()
    if ticket:
        return ticket
    return None