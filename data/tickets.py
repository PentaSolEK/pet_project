from data.init_db import SessionDep
from sqlmodel import select
from models.db_models import Tickets

async def get_ticket(id_concert: int, id_hall_ticket_type: int, session: SessionDep):
    res = await session.exec(select(Tickets).where(Tickets.id_concert == id_concert,
                                                   Tickets.id_hall_ticketTypes == id_hall_ticket_type))
    ticket = res.first()
    if ticket:
        return ticket
    return None