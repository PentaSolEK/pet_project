from fastapi import HTTPException, Depends
from sqlmodel import select

from data.init_db import SessionDep
from models.db_models import Concert, ConcertBase, ConcertUpdate, Concert_groups


async def get_all_concerts(common_param: dict, session: SessionDep):
    res = await session.exec(select(Concert).offset(common_param["skip"]).limit(common_param["limit"]))
    concerts = res.all()
    return concerts

async def get_concert_by_id(concert_id: int, session: SessionDep):
    res = await session.exec(select(Concert).where(Concert.id_concert == concert_id))
    concert = res.first()
    if concert:
        return concert
    return None

async def get_concert_by_name(concert_name: str, session: SessionDep):
    res = await session.exec(select(Concert).where(Concert.name == concert_name))
    concert_name = res.first()
    if concert_name:
        return concert_name
    return None

async def get_concert_id_by_musicgroup(musicgroup_id: int, session: SessionDep):
    statement = select(Concert_groups).where(Concert_groups.id_group == musicgroup_id)
    res = await session.exec(statement)
    concerts = res.all()
    if concerts:
        return concerts
    return None

async def create_conceert(concert: ConcertBase, session: SessionDep):
    db_concert = Concert.model_validate(concert)
    session.add(db_concert)
    await session.commit()
    await session.refresh(db_concert)
    return db_concert


async def update_concert(concert_id: int, concert_update: ConcertUpdate, session: SessionDep):
    concert = await session.get(Concert, concert_id)
    if concert:
        concert_data = concert_update.model_dump(exclude_unset=True)
        concert.sqlmodel_update(concert_data)
        session.add(concert)
        await session.commit()
        await session.refresh(concert)
        return concert
    return None


async def delete_concert(concert_id: int, session: SessionDep):
    concert = await session.get(Concert, concert_id)
    if concert:
        session.delete(concert)
        await session.commit()
        return concert
    return None
