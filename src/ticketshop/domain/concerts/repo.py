from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.ticketshop.domain.concerts.models import Concerts
from src.ticketshop.domain.concerts.schemas import ConcertUpdate

async def get_Concerts(session: AsyncSession, Concerts_id: int) -> Concerts | None:
    return await session.get(Concerts, Concerts_id)

async def get_Concerts_by_name(session: AsyncSession, name: str) -> Concerts | None:
    res = await session.exec(select(Concerts).where(Concerts.name == name))
    return res.first()

async def list_Concerts(session: AsyncSession, *, limit: int = 50, offset: int = 0) -> list[Concerts]:
    res = await session.exec(select(Concerts).offset(offset).limit(limit))
    return list(res.all())

async def create_Concerts(session: AsyncSession, Concerts: Concerts) -> Concerts:
    session.add(Concerts)
    await session.commit()
    await session.refresh(Concerts)
    return Concerts

async def update_Concerts(session: AsyncSession, Concerts: Concerts, payload: ConcertUpdate) -> Concerts:
    if payload.name is not None:
        Concerts.name = payload.name
    if payload.date is not None:
        Concerts.date = payload.date
    if payload.id_hall is not None:
        Concerts.id_hall = payload.id_hall

    session.add(Concerts)
    await session.commit()
    await session.refresh(Concerts)
    return Concerts


async def delete_Concerts(session: AsyncSession, Concerts: Concerts) -> None:
    await session.delete(Concerts)
    await session.commit()