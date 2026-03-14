from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.ticketshop.domain.groups.models import MusicGroups
from src.ticketshop.domain.groups.schemas import MusicgroupsUpdate

async def get_MusicGroups(session: AsyncSession, MusicGroups_id: int) -> MusicGroups | None:
    return await session.get(MusicGroups, MusicGroups_id)

async def get_MusicGroups_by_name(session: AsyncSession, name: str) -> MusicGroups | None:
    res = await session.exec(select(MusicGroups).where(MusicGroups.name == name))
    return res.first()

async def list_Musicgroup(session: AsyncSession, *, limit: int = 50, offset: int = 0) -> list[MusicGroups]:
    res = await session.exec(select(MusicGroups).offset(offset).limit(limit))
    return list(res.all())

async def create_MusicGroups(session: AsyncSession, MusicGroups: MusicGroups) -> MusicGroups:
    session.add(MusicGroups)
    await session.commit()
    await session.refresh(MusicGroups)
    return MusicGroups


async def update_MusicGroups(session: AsyncSession, group: MusicGroups, payload: MusicgroupsUpdate) -> MusicGroups:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(group, k, v)
    session.add(group)
    await session.commit()
    await session.refresh(group)
    return group


async def delete_MusicGroups(session: AsyncSession, MusicGroups: MusicGroups) -> None:
    await session.delete(MusicGroups)
    await session.commit()