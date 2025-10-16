from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from data.init_db import SessionDep

from models.db_models import ConcertBase, ConcertPubic, ConcertUpdate
from data import concerts
from service.common_params import commonDep


router = APIRouter(prefix="/concerts", tags=["concerts"])

@router.get("/")
async def get_all_concerts(session: SessionDep, common_param: commonDep):
    result = await concerts.get_all_concerts(common_param, session)
    return result

@router.get("/{concert_id}")
async def get_concert(concert_id: int, session: SessionDep):
    result = await concerts.get_concert_by_id(concert_id, session)
    if result:
        return result
    raise HTTPException(status_code=404, detail=f"Concert with id {concert_id} not found")

@router.get("/{concert_name}")
async def get_concert_by_name(concert_name: str, session: SessionDep):
    result = await concerts.get_concert_by_name(concert_name, session)
    if result:
        return result
    raise HTTPException(status_code=404, detail=f"Concert with name {concert_name} not found")

@router.post("/", response_model=ConcertPubic)
async def create_concert(concert: Annotated[ConcertBase, Depends()], session: SessionDep):
    result = await concerts.create_conceert(concert, session)
    return result

@router.put("/{concert_id}", response_model=ConcertPubic)
async def update_concert(concert_id: int, concert_update: Annotated[ConcertUpdate, Depends()], session: SessionDep):
    result = await concerts.update_concert(concert_id, concert_update, session)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Concert not found")

@router.delete("/{concert_id}", response_model=ConcertPubic)
async def delete_concert(concert_id: int, session: SessionDep):
    result = await concerts.delete_concert(concert_id, session)
    if result:
        return result.name
    raise HTTPException(status_code=404, detail="Concert not found")