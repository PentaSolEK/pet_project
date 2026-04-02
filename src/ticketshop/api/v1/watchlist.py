from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.ticketshop.api.deps import SessionDep, CurrentUserDep
from src.ticketshop.domain.concerts import repo as concerts_repo
from src.ticketshop.domain.concerts.schemas import ConcertPublic
from src.ticketshop.domain.watchlist import repo as watch_repo

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("/", response_model=list[ConcertPublic])
async def list_watched(session: SessionDep, current_user: CurrentUserDep):
    ids = await watch_repo.list_concert_ids(session, current_user.id_user)
    out: list = []
    for cid in ids:
        c = await concerts_repo.get_Concerts(session, cid)
        if c:
            out.append(c)
    return out


@router.post("/{concert_id}", status_code=status.HTTP_201_CREATED)
async def add_watch(concert_id: int, session: SessionDep, current_user: CurrentUserDep):
    c = await concerts_repo.get_Concerts(session, concert_id)
    if not c:
        raise HTTPException(status_code=404, detail="Concert not found")
    if await watch_repo.is_watching(session, current_user.id_user, concert_id):
        return {"ok": True, "already": True}
    try:
        await watch_repo.add_watch(session, current_user.id_user, concert_id)
    except IntegrityError:
        await session.rollback()
        return {"ok": True, "already": True}
    return {"ok": True, "already": False}


@router.delete("/{concert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_watch(concert_id: int, session: SessionDep, current_user: CurrentUserDep):
    ok = await watch_repo.remove_watch(session, current_user.id_user, concert_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not in watchlist")


@router.get("/{concert_id}/status")
async def watch_status(concert_id: int, session: SessionDep, current_user: CurrentUserDep):
    return {"watching": await watch_repo.is_watching(session, current_user.id_user, concert_id)}
