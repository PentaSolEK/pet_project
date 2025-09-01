from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from data.init_db import SessionDep

from models.db_models import Hall, HallPublic, HallBase, HallUpdate
from data import halls
from service.common_params import commonDep


router = APIRouter(prefix="/halls", tags=["halls"])


@router.get("/")
async def get_all_halls(common_params: commonDep, session: SessionDep):
    result = await halls.get_all_halls(common_params, session)
    return result


@router.get("/{hall_id}")
async def get_by_id(session: SessionDep, hall_id: int):
    result = await halls.get_by_id(session, hall_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="hall not found")


@router.post("/hall", response_model=HallPublic)
async def create_hall(hall: Annotated[HallBase, Depends()], session: SessionDep):
    result = await halls.create_hall(hall, session)
    return result


@router.put("/{hall_id}", response_model=HallPublic)
async def update_hall(hall_id: int, hall_update: HallUpdate, session: SessionDep):
    result = await halls.update_hall(hall_id, hall_update, session)
    if result:
        return result
    raise HTTPException(status_code=404, detail="hall not found")


@router.delete("/{hall_id}", response_model=HallPublic)
async def delete_hall(hall_id: int, session: SessionDep):
    result = await halls.delete_hall(hall_id, session)
    if result:
        return result.name
    raise HTTPException(status_code=404, detail="hall not found")