from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.ticketshop.domain.halls.models import Hall
from src.ticketshop.domain.halls.schemas import HallUpdate


async def get_hall(session: AsyncSession, Hall_id: int) -> Hall | None:
    return await session.get(Hall, Hall_id)

async def get_hall_by_name(session: AsyncSession, name: str) -> Hall | None:
    res = await session.exec(select(Hall).where(Hall.name == name))
    return res.first()

async def list_halls(session: AsyncSession, *, limit: int = 50, offset: int = 0) -> list[Hall]:
    res = await session.exec(select(Hall).offset(offset).limit(limit))
    return list(res.all())

async def create_hall(session: AsyncSession, Hall: Hall) -> Hall:
    session.add(Hall)
    await session.commit()
    await session.refresh(Hall)
    return Hall


async def update_hall(session: AsyncSession, hall: Hall, payload: HallUpdate) -> Hall:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(hall, k, v)
    session.add(hall)
    await session.commit()
    await session.refresh(hall)
    return hall


async def delete_hall(session: AsyncSession, Hall: Hall) -> None:
    await session.delete(Hall)
    await session.commit()