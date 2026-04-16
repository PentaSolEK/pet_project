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
from src.ticketshop.domain.halls.repo import get_hall
from src.ticketshop.domain.tickettypes.repo import get_TicketType
from src.ticketshop.domain.tickets.repo import get_ticket
from src.ticketshop.domain.groups.schemas import MusicgroupsPublic
from src.ticketshop.domain.groups import repo as groups_repo
from src.ticketshop.domain.seat_bookings import repo as seat_repo
from src.ticketshop.domain.concerts.schemas import HallLayoutResponse, HallLayoutZone, HallLayoutSeat

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

def _zone_role(type_name: str) -> str:
    t = (type_name or "").strip().lower()
    if "вип" in t or "vip" in t:
        return "vip"
    if "танцпол" in t or "dance" in t or "pit" in t:
        return "dance"
    if "лаунж" in t or "lounge" in t:
        return "lounge"
    return "other"


_ROLE_COLORS = {
    "vip": "#f59e0b",
    "dance": "#7c6cf0",
    "lounge": "#10b981",
    "other": "#64748b",
}


def _build_seats_for_zone(role: str, amount: int, seats_per_row: int, row_offset: int) -> tuple[list[HallLayoutSeat], int]:
    seats: list[HallLayoutSeat] = []
    if role == "dance":
        # Dance floor is represented as a single clickable area on the frontend;
        # we don't emit individual virtual spots. Capacity is tracked via ticket.remains.
        return seats, 0
    if amount <= 0 or seats_per_row <= 0:
        return seats, 0
    rows_used = (amount + seats_per_row - 1) // seats_per_row
    remaining = amount
    for r in range(rows_used):
        row_num = row_offset + r
        in_this_row = min(seats_per_row, remaining)
        for s in range(1, in_this_row + 1):
            seats.append(HallLayoutSeat(row=row_num, seat=s))
        remaining -= in_this_row
    return seats, rows_used


@router.get("/{concert_id}/hall-layout", response_model=HallLayoutResponse)
async def hall_layout(concert_id: int, session: SessionDep):
    concert = await repo.get_Concerts(session, concert_id)
    if not concert or not concert.id_hall:
        raise HTTPException(404, "Concert not found or hall not set")
    hall = await get_hall(session, concert.id_hall)
    if not hall:
        raise HTTPException(404, "Hall not found")

    rows_count = hall.rows_count or 10
    seats_per_row = hall.seats_per_row or 10
    scheme = hall.scheme or "classic"

    zones_raw = await list_hall_zones_by_hall(session, concert.id_hall)

    classified: list[dict] = []
    for z in zones_raw:
        tt = await get_TicketType(session, z.id_type)
        if not tt:
            continue
        trow = await get_ticket(session, concert_id, z.id_hall_zone)
        if not trow:
            continue
        classified.append({
            "zone": z,
            "type": tt,
            "ticket": trow,
            "role": _zone_role(tt.type),
        })

    order = {"dance": 0, "vip": 1, "lounge": 2, "other": 3}
    classified.sort(key=lambda c: order.get(c["role"], 9))

    response_zones: list[HallLayoutZone] = []
    row_cursor = 1  # row 0 is reserved for dance floor standing spots
    for c in classified:
        zone = c["zone"]
        role = c["role"]
        total = zone.amount or 0
        seats, rows_used = _build_seats_for_zone(role, total, seats_per_row, row_cursor)
        if role != "dance":
            row_cursor += rows_used
        response_zones.append(
            HallLayoutZone(
                id_hall_zone=zone.id_hall_zone,
                id_ticket_type=zone.id_type,
                name=c["type"].type,
                role=role,
                price=c["ticket"].price,
                total=total,
                remains=c["ticket"].remains,
                color=_ROLE_COLORS.get(role, "#64748b"),
                seats=seats,
            )
        )

    occupied_raw = await seat_repo.list_occupied_for_concert(session, concert_id)
    occupied = [[sb.row_num, sb.seat_num] for sb in occupied_raw]

    return HallLayoutResponse(
        scheme=scheme,
        rows_count=max(rows_count, row_cursor - 1),
        seats_per_row=seats_per_row,
        zones=response_zones,
        occupied=occupied,
    )


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