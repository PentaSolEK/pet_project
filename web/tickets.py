from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from data.init_db import SessionDep


from models.db_models import TickettypesBase, TickettypesPublic, TickettypesUpdate
from data import tickets_type
from service.common_params import commonDep

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/")
async def get_all_tickets_types(common_params: commonDep, session: SessionDep):
    result = await tickets.get_all_tickets_types(common_params, session)
    return result

@router.get("/{ticket_id}")
async def get_by_id(session: SessionDep, ticket_id: int):
    result = await tickets.get_tickets_type_by_id(session, ticket_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Ticket not found")


@router.post("/tickettype", response_model=TickettypesPublic)
async def create_ticket_type(ticket_type: Annotated[TickettypesBase, Depends()], session: SessionDep):
    result = await tickets.create_ticket_type(ticket_type, session)
    return result


@router.put("/{ticket_id}", response_model=TickettypesPublic)
async def update_ticket(ticket_id: int, ticket_update: TickettypesUpdate, session: SessionDep):
    result = await tickets.update_ticket(ticket_id, ticket_update, session)
    if result:
        return result
    raise HTTPException(status_code=404, detail="ticket not found")


@router.delete("/{ticket_id}", response_model=TickettypesPublic)
async def delete_ticket(ticket_id: int, session: SessionDep):
    result = await tickets.delete_ticket(ticket_id, session)
    if result:
        return result.name
    raise HTTPException(status_code=404, detail="ticket not found")