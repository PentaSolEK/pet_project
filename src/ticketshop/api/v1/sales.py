from datetime import datetime

from fastapi import APIRouter, HTTPException
from src.ticketshop.api.deps import SessionDep, CurrentUserDep, AdminDep
from src.ticketshop.domain.sales.models import Sale
from src.ticketshop.domain.sales.schemas import SalesPublic, SalesUpdate, TicketPurchaseRequest
from src.ticketshop.domain.sales import repo
from src.ticketshop.domain.tickets.repo import get_ticket
from src.ticketshop.domain.tickettypes.repo import get_TicketType
from src.ticketshop.domain.concerts.repo import get_Concerts
from src.ticketshop.domain.hall_zone.repo import get_hall_zone

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/")
async def get_all_sales(session: SessionDep, limit: int = 50, offset: int = 0):
    return await repo.list_sales(session,limit=limit,offset=offset)


@router.post("/buy", response_model=SalesPublic)
async def buy_ticket(
    purchase: TicketPurchaseRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """Покупка билета: проверяет остатки, списывает их и создаёт запись о продаже."""
    ticket_type_id = purchase.id_ticket_type
    if not await get_TicketType(session, ticket_type_id):
        raise HTTPException(status_code=404, detail="Ticket type not found")

    concert_id = purchase.id_concert
    concert = await get_Concerts(session, concert_id)
    if not concert:
        raise HTTPException(status_code=404, detail="Concert not found")
    if concert.sales_paused:
        raise HTTPException(status_code=400, detail="Ticket sales are paused for this concert")

    hall_id = concert.id_hall
    hall_zone = await get_hall_zone(session, hall_id, ticket_type_id)
    if not hall_zone:
        raise HTTPException(status_code=404, detail="Hall zone not found")

    ticket = await get_ticket(session, concert_id, hall_zone.id_hall_zone)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found for this concert and zone")

    if ticket.remains < purchase.count:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough tickets. Available: {ticket.remains}, requested: {purchase.count}",
        )

    ticket.remains -= purchase.count
    session.add(ticket)

    sale = Sale(
        id_user=current_user.id_user,
        id_ticket=ticket.id_ticket,
        count=purchase.count,
        total_price=ticket.price * purchase.count,
        sale_date=datetime.now(),
    )
    result = await repo.create_sale(session, sale)
    return result


@router.get("/{sale_id}")
async def get_sale_by_id(sale_id: int, session: SessionDep):
    result = await repo.get_sale(session, sale_id)
    if not result:
        raise HTTPException(status_code=404, detail="Sale not found")
    return result


@router.patch("/{sale_id}", response_model=SalesPublic)
async def update_sale(sale_id: int, update_data: SalesUpdate, session: SessionDep, _: AdminDep):
    sale = await repo.get_sale(session, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return await repo.update_sale(session, sale, update_data)


@router.delete("/{sale_id}", response_model=SalesPublic)
async def delete_sale(sale_id: int, session: SessionDep, _: AdminDep):
    sale = await repo.get_sale(session, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    await repo.delete_sale(session, sale)
    return sale
