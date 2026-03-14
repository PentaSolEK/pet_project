from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.ticketshop.domain.sales.models import Sale
from src.ticketshop.domain.sales.schemas import SalesUpdate

async def get_sale(session: AsyncSession, sale_id: int) -> Sale | None:
    return await session.get(Sale, sale_id)

async def get_sale_by_user(session: AsyncSession, user_id: int) -> list[Sale]:
    res = await session.exec(select(Sale).where(Sale.id_user == user_id))
    return list(res.all())

async def list_sales(session: AsyncSession, *, limit: int = 50, offset: int = 0) -> list[Sale]:
    res = await session.exec(select(Sale).offset(offset).limit(limit))
    return list(res.all())

async def create_sale(session: AsyncSession, Sale: Sale) -> Sale:
    session.add(Sale)
    await session.commit()
    await session.refresh(Sale)
    return Sale

async def update_sale(session: AsyncSession, sale: Sale, payload: SalesUpdate) -> Sale:
    if payload.id_user is not None:
        sale.id_user = payload.id_user
    if payload.id_ticket is not None:
        sale.id_ticket = payload.id_ticket
    if payload.count is not None:
        sale.count = payload.count
    if payload.sale_date is not None:
        sale.sale_date = payload.sale_date
    session.add(sale)
    await session.commit()
    await session.refresh(sale)
    return sale

async def delete_sale(session: AsyncSession, sale: Sale) -> None:
    await session.delete(sale)
    await session.commit()