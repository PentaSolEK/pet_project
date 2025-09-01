from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from data.init_db import SessionDep

from models.db_models import MusicgroupsBase, MusicgroupsPublic, MusicgroupsUpdate
from data import groups
from service.common_params import commonDep

router = APIRouter(prefix="/musicgroups", tags=["musicgroups"])


@router.get("/")
async def get_all_musicgroups(common_params: commonDep, session: SessionDep):
    result = await groups.get_all_musicgroups(common_params, session)
    return result

@router.get("/{musicgroup_id}")
async def get_by_id(session: SessionDep, musicgroup_id: int):
    result = await groups.get_musicgroup_by_id(session, musicgroup_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Musicgroup not found")


@router.post("/group", response_model=MusicgroupsPublic)
async def create_group(group: Annotated[MusicgroupsBase, Depends()], session: SessionDep):
    result = await groups.create_group(group, session)
    return result


@router.put("/{MusicGroup_id}", response_model=MusicgroupsPublic)
async def update_group(group_id: int, group_update: MusicgroupsUpdate, session: SessionDep):
    result = await groups.update_group(group_id, group_update, session)
    if result:
        return result
    raise HTTPException(status_code=404, detail="MusicGroup not found")


@router.delete("/{MusicGroup_id}", response_model=MusicgroupsPublic)
async def delete_group(group_id: int, session: SessionDep):
    result = await groups.delete_group(group_id, session)
    if result:
        return result.name
    raise HTTPException(status_code=404, detail="MusicGroup not found")