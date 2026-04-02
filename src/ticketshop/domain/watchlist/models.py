from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Watchlist(SQLModel, table=True):
    __tablename__ = "watchlist"
    __table_args__ = (UniqueConstraint("id_user", "id_concert", name="uq_watch_user_concert"),)

    id_watch: Optional[int] = Field(default=None, primary_key=True)
    id_user: int = Field(foreign_key="users.id_user", index=True)
    id_concert: int = Field(foreign_key="concert.id_concert", index=True)
