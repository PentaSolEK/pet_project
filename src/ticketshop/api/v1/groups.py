from fastapi import APIRouter, HTTPException, status
from src.ticketshop.api.deps import SessionDep, AdminDep
from src.ticketshop.domain.groups.models import MusicGroups
from src.ticketshop.domain.groups.schemas import MusicgroupsBase, MusicgroupsPublic, MusicgroupsUpdate
from src.ticketshop.domain.groups import repo

router = APIRouter(prefix="/groups", tags=["groups"])

@router.get("/", response_model=list[MusicgroupsPublic])
async def list_(session: SessionDep, limit: int = 50, offset: int = 0):
    return await repo.list_Musicgroup(session, limit=limit, offset=offset)

@router.get("/by-name/{concert_name}", response_model=MusicgroupsPublic)
async def by_name(concert_name: str, session: SessionDep):
    c = await repo.get_MusicGroups_by_name(session, concert_name)
    if not c:
        raise HTTPException(404, "Concert not found")
    return c

@router.get("/{concert_id}", response_model=MusicgroupsPublic)
async def get_(concert_id: int, session: SessionDep):
    c = await repo.get_MusicGroups(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    return c

@router.post("/", response_model=MusicgroupsPublic, status_code=status.HTTP_201_CREATED)
async def create_(payload: MusicgroupsBase, session: SessionDep, _: AdminDep):
    c = MusicGroups(name=payload.name,albumCount=payload.albumCount, site=payload.site, id_genre=payload.id_genre)
    return await repo.create_MusicGroups(session, c)

@router.patch("/{concert_id}", response_model=MusicgroupsPublic)
async def update_(concert_id: int, payload: MusicgroupsUpdate, session: SessionDep, _: AdminDep):
    c = await repo.get_MusicGroups(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    return await repo.update_MusicGroups(session, c, payload)

@router.delete("/{concert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_(concert_id: int, session: SessionDep, _: AdminDep):
    c = await repo.get_MusicGroups(session, concert_id)
    if not c:
        raise HTTPException(404, "Concert not found")
    await repo.delete_MusicGroups(session, c)