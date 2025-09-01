from fastapi import HTTPException

from data.init_db import SessionDep

from sqlmodel import select

from models.db_models import Tickettypes, TickettypesBase, TickettypesPublic, TickettypesUpdate



async def get_all_tickets_types(common_params: dict, session: SessionDep):
    tickets = session.exec(statement=select(Tickettypes).offset(common_params["skip"]).
                           limit(common_params["limit"])).all()
    return tickets

async def get_tickets_type_by_id(session: SessionDep, ticket_id: int):
    ticket = session.exec(statement=select(Tickettypes).where(Tickettypes.id_type == ticket_id)).first()
    if ticket:
        return ticket
    return None


async def create_ticket_type(ticket: TickettypesBase, session: SessionDep):
    db_ticket = Tickettypes.model_validate(ticket)
    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)
    return db_ticket


async def update_ticket(ticket_id: int, ticket_update: TickettypesUpdate, session: SessionDep):
    ticket = session.get(Tickettypes, ticket_id)
    if ticket:
        ticket_data = ticket_update.model_dump(exclude_unset=True)
        ticket.sqlmodel_update(ticket_data)
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        return ticket
    return None


async def delete_ticket(ticket_id: int, session: SessionDep):
    ticket = session.get(Tickettypes, ticket_id)
    if ticket:
        session.delete(ticket)
        session.commit()
        return ticket
    return None