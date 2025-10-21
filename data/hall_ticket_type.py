from data.init_db import SessionDep
from sqlmodel import select
from models.db_models import Hall_TicketTypes

async def get_hall_ticket_type(id_hall: int, id_ticket_type: int, session: SessionDep):
    res = await session.exec(statement=select(Hall_TicketTypes).where(
        Hall_TicketTypes.id_hall == id_hall, Hall_TicketTypes.id_type == id_ticket_type))
    hall_ticket_type = res.first()
    if hall_ticket_type:
        return hall_ticket_type
    return None