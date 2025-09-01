from data.init_db import SessionDep

from sqlmodel import select

from models.db_models import Musicgroups, MusicgroupsBase, MusicgroupsPublic, MusicgroupsUpdate


async def get_all_musicgroups(common_params: dict, session: SessionDep):
    groups = session.exec(statement=select(Musicgroups).offset(common_params["skip"]).
                          limit(common_params["limit"])).all()
    return groups

async def get_musicgroup_by_id(session: SessionDep, musicgroup_id: int):
    group = session.exec(statement=select(Musicgroups).where(Musicgroups.id_group == musicgroup_id)).first()
    if group:
        return group
    return None


async def create_group(group: MusicgroupsBase, session: SessionDep):
    db_group = Musicgroups.model_validate(group)
    session.add(db_group)
    session.commit()
    session.refresh(db_group)
    return db_group


async def update_group(group_id: int, group_update: MusicgroupsUpdate, session: SessionDep):
    group = session.get(Musicgroups, group_id)
    if group:
        group_data = group_update.model_dump(exclude_unset=True)
        group.sqlmodel_update(group_data)
        session.add(group)
        session.commit()
        session.refresh(group)
        return group
    return None


async def delete_group(group_id: int, session: SessionDep):
    group = session.get(Musicgroups, group_id)
    if group:
        session.delete(group)
        session.commit()
        return group
    return None