from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.ticketshop.domain.watchlist.models import Watchlist


async def add_watch(session: AsyncSession, id_user: int, id_concert: int) -> Watchlist:
    row = Watchlist(id_user=id_user, id_concert=id_concert)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def remove_watch(session: AsyncSession, id_user: int, id_concert: int) -> bool:
    res = await session.exec(
        select(Watchlist).where(
            Watchlist.id_user == id_user,
            Watchlist.id_concert == id_concert,
        )
    )
    row = res.first()
    if not row:
        return False
    await session.delete(row)
    await session.commit()
    return True


async def list_concert_ids(session: AsyncSession, id_user: int) -> list[int]:
    res = await session.exec(select(Watchlist).where(Watchlist.id_user == id_user))
    return [w.id_concert for w in res.all()]


async def is_watching(session: AsyncSession, id_user: int, id_concert: int) -> bool:
    res = await session.exec(
        select(Watchlist).where(
            Watchlist.id_user == id_user,
            Watchlist.id_concert == id_concert,
        )
    )
    return res.first() is not None
