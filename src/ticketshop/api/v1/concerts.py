from fastapi import APIRouter, HTTPException, status
from src.ticketshop.api.deps import SessionDep, AdminDep
from src.ticketshop.domain.concerts.models import Concerts
from src.ticketshop.domain.concerts.schemas import (
    ConcertPublic,
    ConcertUpdate,
    ConcertBase,
    PurchaseOptionItem,
)
from src.ticketshop.domain.concerts import repo
from src.ticketshop.domain.hall_zone.repo import list_hall_zones_by_hall
from src.ticketshop.domain.tickettypes.repo import get_TicketType
from src.ticketshop.domain.tickets.repo import get_ticket
from src.ticketshop.domain.groups.schemas import MusicgroupsPublic
from src.ticketshop.domain.groups import repo as groups_repo

router = APIRouter(prefix="/concerts", tags=["concerts"])

@router.get("/", response_model=list[ConcertPublic])
async def list_(session: SessionDep, limit: int = 50, offset: int = 0):
    return await repo.list_Concerts(session, limit=limit, offset=offset)

@router.get("/by-name/{concert_name}", response_model=ConcertPublic)
async def by_name(concert_name: str, session: SessionDep):
    c = await repo.get_Concerts_by_name(session, concert_name)
    if not c:
        raise HTTPException(404, "Concert not found")
    return c

@router.get("/{concert_id}/purchase-options", response_model=list[PurchaseOptionItem])
async def purchase_options(concert_id: int, session: SessionDep):
    concert = await repo.get_Concerts(session, concert_id)
    if not concert or not concert.id_hall:
        raise HTTPException(404, "Concert not found or hall not set")
    zones = await list_hall_zones_by_hall(session, concert.id_hall)
    out: list[PurchaseOptionItem] = []
    for zone in zones:
        tt = await get_TicketType(session, zone.id_type)
        if not tt:
            continue
        trow = await get_ticket(session, concert_id, zone.id_hall_zone)
        if not trow:
            continue
        out.append(
            PurchaseOptionItem(
                id_ticket_type=zone.id_type,
                ticket_type_name=tt.type,
                id_hall_zone=zone.id_hall_zone,
                price=trow.price,
                remains=trow.remains,
            )
        )
    return out

@router.get("/{concert_id}", response_model=ConcertPublic)
async def get_(concert_id: int, session: SessionDep):
    c = await repo.get_Concerts(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    return c

@router.post("/", response_model=ConcertPublic, status_code=status.HTTP_201_CREATED)
async def create_(payload: ConcertBase, session: SessionDep, _: AdminDep):
    c = Concerts(
        name=payload.name,
        date=payload.date,
        id_hall=payload.id_hall,
        description=payload.description,
        sales_paused=payload.sales_paused,
    )
    return await repo.create_Concerts(session, c)

@router.patch("/{concert_id}", response_model=ConcertPublic)
async def update_(concert_id: int, payload: ConcertUpdate, session: SessionDep, _: AdminDep):
    c = await repo.get_Concerts(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    c = await repo.update_Concerts(session, c, payload)
    return c

@router.delete("/{concert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_(concert_id: int, session: SessionDep, _: AdminDep):
    c = await repo.get_Concerts(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    await repo.delete_Concerts(session, c)


@router.get("/{concert_id}/groups", response_model=list[MusicgroupsPublic])
async def list_groups(concert_id: int, session: SessionDep):
    c = await repo.get_Concerts(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    return await repo.list_groups_for_concert(session, concert_id)


@router.post("/{concert_id}/groups/{group_id}", status_code=status.HTTP_201_CREATED)
async def add_group(concert_id: int, group_id: int, session: SessionDep, _: AdminDep):
    c = await repo.get_Concerts(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    g = await groups_repo.get_MusicGroups(session, group_id)
    if not g:
        raise HTTPException(404, "Group not found")
    return await repo.add_group_to_concert(session, concert_id, group_id)


@router.delete("/{concert_id}/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group(concert_id: int, group_id: int, session: SessionDep, _: AdminDep):
    removed = await repo.remove_group_from_concert(session, concert_id, group_id)
    if not removed:
        raise HTTPException(404, "Link not found")