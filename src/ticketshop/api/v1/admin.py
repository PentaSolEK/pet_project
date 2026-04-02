from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import desc
from sqlmodel import select

from src.ticketshop.api.deps import SessionDep, AdminDep
from src.ticketshop.domain.concerts.repo import get_Concerts
from src.ticketshop.domain.sales.models import Sale
from src.ticketshop.domain.tickets.models import Tickets
from src.ticketshop.domain.users.repo import get_user_by_id

router = APIRouter(prefix="/admin", tags=["admin"])


class SaleAdminItem(BaseModel):
    id_sale: int
    id_user: int
    user_email: str
    id_ticket: int
    id_concert: int | None
    concert_name: str | None
    count: int
    total_price: int
    sale_date: datetime


@router.get("/sales/recent", response_model=list[SaleAdminItem])
async def recent_sales(
    session: SessionDep,
    _: AdminDep,
    limit: int = 50,
    offset: int = 0,
):
    res = await session.exec(
        select(Sale).order_by(desc(Sale.sale_date)).offset(offset).limit(limit)
    )
    sales = list(res.all())
    out: list[SaleAdminItem] = []
    for s in sales:
        user = await get_user_by_id(session, s.id_user)
        ticket = await session.get(Tickets, s.id_ticket)
        concert = None
        if ticket and ticket.id_concert is not None:
            concert = await get_Concerts(session, ticket.id_concert)
        out.append(
            SaleAdminItem(
                id_sale=s.id_sale,
                id_user=s.id_user,
                user_email=user.email if user else "?",
                id_ticket=s.id_ticket,
                id_concert=ticket.id_concert if ticket else None,
                concert_name=concert.name if concert else None,
                count=s.count,
                total_price=s.total_price,
                sale_date=s.sale_date,
            )
        )
    return out
