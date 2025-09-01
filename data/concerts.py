from typing import Annotated

from fastapi import HTTPException, Depends

from data.init_db import SessionDep

from sqlmodel import select

from models.db_models import Concert, ConcertBase, ConcertPubic, ConcertUpdate


async def get_all_concerts(common_param: dict, session: SessionDep):
    concerts = session.exec(select(Concert).offset(common_param["skip"]).limit(common_param["limit"])).all()
    return concerts


async def get_concert_by_id(concert_id: int, session: SessionDep):
    concert_name = session.exec(select(Concert).where(Concert.id_concert == concert_id)).first()
    if concert_name:
        return concert_name
    return None


async def create_conceert(concert: ConcertBase, session: SessionDep):
    db_concert = Concert.model_validate(concert)
    session.add(db_concert)
    session.commit()
    session.refresh(db_concert)
    return db_concert


async def update_concert(concert_id: int, concert_update: ConcertUpdate, session: SessionDep):
    concert = session.get(Concert, concert_id)
    if concert:
        concert_data = concert_update.model_dump(exclude_unset=True)
        concert.sqlmodel_update(concert_data)
        session.add(concert)
        session.commit()
        session.refresh(concert)
        return concert
    return None


async def delete_concert(concert_id: int, session: SessionDep):
    concert = session.get(Concert, concert_id)
    if concert:
        session.delete(concert)
        session.commit()
        return concert
    return None
