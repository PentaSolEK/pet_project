from data.init_db import SessionDep

from sqlmodel import select

from models.db_models import Musicgroups, MusicgroupsBase, MusicgroupsPublic, MusicgroupsUpdate


async def get_all_musicgroups(common_params: dict, session: SessionDep):
    res = await session.exec(statement=select(Musicgroups).offset(common_params["skip"]).
                             limit(common_params["limit"]))
    groups = res.all()
    return groups

async def get_musicgroup_by_id(session: SessionDep, musicgroup_id: int):
    res = await session.exec(statement=select(Musicgroups).where(Musicgroups.id_group == musicgroup_id))
    group = res.first()
    if group:
        return group
    return None


async def create_group(group: MusicgroupsBase, session: SessionDep):
    db_group = Musicgroups.model_validate(group)
    session.add(db_group)
    await session.commit()
    await session.refresh(db_group)
    return db_group


async def update_group(group_id: int, group_update: MusicgroupsUpdate, session: SessionDep):
    group = await session.get(Musicgroups, group_id)
    if group:
        group_data = group_update.model_dump(exclude_unset=True)
        group.sqlmodel_update(group_data)
        session.add(group)
        await session.commit()
        await session.refresh(group)
        return group
    return None


async def delete_group(group_id: int, session: SessionDep):
    group = await session.get(Musicgroups, group_id)
    if group:
        session.delete(group)
        await session.commit()
        return group
    return None