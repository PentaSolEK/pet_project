from fastapi import APIRouter, HTTPException, status
from src.ticketshop.api.deps import SessionDep, AdminDep
from src.ticketshop.domain.concerts.models import Concerts
from src.ticketshop.domain.concerts.schemas import ConcertPublic, ConcertUpdate, ConcertBase
from src.ticketshop.domain.concerts import repo

router = APIRouter(prefix="/concerts", tags=["concerts"])

@router.get("/", response_model=list[ConcertPublic])
async def list_(session: SessionDep, limit: int = 50, offset: int = 0):
    return await repo.list_Concerts(session, limit=limit, offset=offset)

@router.get("/by-name/{concert_name}", response_model=ConcertPublic)
async def by_name(concert_name: str, session: SessionDep):
    c = await repo.get_Concerts_by_name(session, concert_name)
    if not c:
        raise HTTPException(404, "Concert not found")
    return c

@router.get("/{concert_id}", response_model=ConcertPublic)
async def get_(concert_id: int, session: SessionDep):
    c = await repo.get_Concerts(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    return c

@router.post("/", response_model=ConcertPublic, status_code=status.HTTP_201_CREATED)
async def create_(payload: ConcertBase, session: SessionDep, _: AdminDep):
    c = Concerts(name=payload.name, date=payload.date, id_hall = payload.id_hall )
    return await repo.create_Concerts(session, c)

@router.patch("/{concert_id}", response_model=ConcertPublic)
async def update_(concert_id: int, payload: ConcertUpdate, session: SessionDep, _: AdminDep):
    c = await repo.get_Concerts(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    c = await repo.update_Concerts(session, c, payload)
    return c

@router.delete("/{concert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_(concert_id: int, session: SessionDep, _: AdminDep):
    c = await repo.get_Concerts(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    await repo.delete_Concerts(session, c)