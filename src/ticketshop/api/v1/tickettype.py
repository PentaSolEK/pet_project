from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from src.ticketshop.api.deps import SessionDep, AdminDep
from src.ticketshop.domain.tickettypes.models import TicketType
from src.ticketshop.domain.tickettypes.schemas import TickettypesBase, TickettypesPublic, TickettypesUpdate
from src.ticketshop.domain.tickettypes import repo

router = APIRouter(prefix="/tickettypes", tags=["tickettypes"])


@router.get("/")
async def get_all_tickets_types(session: SessionDep, limit: int = 50, offset: int = 0):
    result = await repo.list_TicketTypes(session,limit=limit, offset=offset)
    return result


@router.get("/{ticket_id}")
async def get_by_id(session: SessionDep, ticket_id: int):
    result = await repo.get_TicketType(session, ticket_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Ticket not found")


@router.post("/", response_model=TickettypesPublic)
async def create_ticket_type(ticket_type: Annotated[TickettypesBase, Depends()], session: SessionDep, _: AdminDep):
    model = TicketType(type=ticket_type.type)
    result = await repo.create_TicketType(session, model)
    return result


@router.patch("/{ticket_id}", response_model=TickettypesPublic)
async def update_ticket(ticket_id: int, ticket_update: TickettypesUpdate, session: SessionDep, _: AdminDep):
    ticketype = await repo.get_TicketType(session, ticket_id)
    if not ticketype:
        raise HTTPException(status_code=404, detail="Ticket not found")
    result = await repo.update_ticket(session, ticketype, ticket_update)
    return result


@router.delete("/{ticket_id}", response_model=TickettypesPublic)
async def delete_ticket(ticket_id: int, session: SessionDep, _: AdminDep):
    ticketype = await repo.get_TicketType(session, ticket_id)
    if not ticketype:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await repo.delete_TicketType(session, ticketype)
    return ticketype
