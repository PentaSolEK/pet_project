from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.ticketshop.domain.concerts.models import Concerts, ConcertGroup
from src.ticketshop.domain.concerts.schemas import ConcertUpdate
from src.ticketshop.domain.groups.models import MusicGroups

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
    if payload.description is not None:
        Concerts.description = payload.description
    if payload.sales_paused is not None:
        Concerts.sales_paused = payload.sales_paused

    session.add(Concerts)
    await session.commit()
    await session.refresh(Concerts)
    return Concerts


async def delete_Concerts(session: AsyncSession, Concerts: Concerts) -> None:
    await session.delete(Concerts)
    await session.commit()


async def list_groups_for_concert(session: AsyncSession, concert_id: int) -> list[MusicGroups]:
    res = await session.exec(
        select(MusicGroups)
        .join(ConcertGroup, ConcertGroup.id_group == MusicGroups.id_group)
        .where(ConcertGroup.id_concert == concert_id)
    )
    return list(res.all())


async def add_group_to_concert(session: AsyncSession, concert_id: int, group_id: int) -> ConcertGroup:
    link = ConcertGroup(id_concert=concert_id, id_group=group_id)
    session.add(link)
    await session.commit()
    await session.refresh(link)
    return link


async def remove_group_from_concert(session: AsyncSession, concert_id: int, group_id: int) -> bool:
    res = await session.exec(
        select(ConcertGroup)
        .where(ConcertGroup.id_concert == concert_id, ConcertGroup.id_group == group_id)
    )
    link = res.first()
    if not link:
        return False
    await session.delete(link)
    await session.commit()
    return True