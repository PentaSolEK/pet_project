<<<<<<< HEAD
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

=======
from fastapi import APIRouter, HTTPException
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
from data.init_db import SessionDep
from sqlmodel import select

from models.db_models import Concert, ConcertBase, ConcertPubic, ConcertUpdate
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
    raise HTTPException(status_code=404, detail="Concert not found")


@router.post("/", response_model=ConcertPubic)
async def create_concert(concert: ConcertBase, session: SessionDep):
    result = await concerts.create_conceert(concert, session)
    return result


@router.put("/{concert_id}", response_model=ConcertPubic)
<<<<<<< HEAD
async def update_concert(concert_id: int, concert_update: Annotated[ConcertUpdate, Depends()], session: SessionDep):
=======
async def update_concert(concert_id: int, concert_update: ConcertUpdate, session: SessionDep):
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
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