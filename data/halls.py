from fastapi import HTTPException

from data.init_db import SessionDep
from sqlmodel import select
from models.db_models import Hall, HallBase, HallUpdate


async def get_all_halls(common_params: dict, session: SessionDep):
    res = await session.exec(statement=select(Hall).offset(common_params["skip"]).limit(common_params["limit"]))
    halls = res.all()
    return halls

async def get_by_id(session: SessionDep, number: int):
    result = await session.exec(statement=select(Hall).where(Hall.number == number))
    hall = result.first()
    if hall:
        return hall
    return None


async def create_hall(hall: HallBase, session: SessionDep):
    db_hall = Hall.model_validate(hall)
    session.add(db_hall)
    await session.commit()
    await session.refresh(db_hall)
    return db_hall


async def update_hall(hall_id: int, hall_update: HallUpdate, session: SessionDep):
    hall = await session.get(Hall, hall_id)
    if hall:
        hall_data = hall_update.model_dump(exclude_unset=True)
        hall.sqlmodel_update(hall_data)
        session.add(hall)
        await session.commit()
        await session.refresh(hall)
        return hall
    return None


async def delete_hall(hall_id: int, session: SessionDep):
    hall = await session.get(Hall, hall_id)
    if hall:
        session.delete(hall)
        await session.commit()
        return hall
    return None