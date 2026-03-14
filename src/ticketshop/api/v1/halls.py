from fastapi import APIRouter, HTTPException, status
from src.ticketshop.api.deps import SessionDep, AdminDep
from src.ticketshop.domain.halls.models import Hall
from src.ticketshop.domain.halls.schemas import HallPublic, HallBase, HallUpdate
from src.ticketshop.domain.halls import repo

router = APIRouter(prefix="/halls", tags=["halls"])


@router.get("/", response_model=list[HallPublic])
async def list_(session: SessionDep, limit: int = 50, offset: int = 0):
    return await repo.list_halls(session, limit=limit, offset=offset)


@router.get("/{hall_id}", response_model=HallPublic)
async def get_(hall_id: int, session: SessionDep):
    h = await repo.get_hall(session, hall_id)
    if not h:
        raise HTTPException(404, "Hall not found")
    return h


@router.post("/", response_model=HallPublic, status_code=status.HTTP_201_CREATED)
async def create_(payload: HallBase, session: SessionDep, _: AdminDep):
    h = Hall(**payload.model_dump())
    return await repo.create_hall(session, h)


@router.patch("/{hall_id}", response_model=HallPublic)
async def update_(hall_id: int, payload: HallUpdate, session: SessionDep, _: AdminDep):
    h = await repo.get_hall(session, hall_id)
    if not h:
        raise HTTPException(404, "Hall not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(h, k, v)

    session.add(h)
    await session.commit()
    await session.refresh(h)
    return h


@router.delete("/{hall_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_(hall_id: int, session: SessionDep, _: AdminDep):
    h = await repo.get_hall(session, hall_id)
    if not h:
        raise HTTPException(404, "Hall not found")
    await repo.delete_hall(session, h)