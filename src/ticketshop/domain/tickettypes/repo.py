from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.ticketshop.domain.tickettypes.models import TicketType
from src.ticketshop.domain.tickettypes.schemas import TickettypesUpdate

async def get_TicketType(session: AsyncSession, TicketType_id: int) -> TicketType | None:
    return await session.get(TicketType, TicketType_id)

async def get_TicketType_by_type(session: AsyncSession, type_name: str) -> TicketType | None:
    res = await session.exec(select(TicketType).where(TicketType.type == type_name))
    return res.first()

async def list_TicketTypes(session: AsyncSession, *, limit: int = 50, offset: int = 0) -> list[TicketType]:
    res = await session.exec(select(TicketType).offset(offset).limit(limit))
    return list(res.all())

async def create_TicketType(session: AsyncSession, TicketType: TicketType) -> TicketType:
    session.add(TicketType)
    await session.commit()
    await session.refresh(TicketType)
    return TicketType

async def update_ticket(session: AsyncSession, ticketype: TicketType, payload: TickettypesUpdate) -> TicketType:
    if payload.type is not None:
        ticketype.type = payload.type
    session.add(ticketype)
    await session.commit()
    await session.refresh(ticketype)
    return ticketype


async def delete_TicketType(session: AsyncSession, TicketType: TicketType) -> None:
    await session.delete(TicketType)
    await session.commit()