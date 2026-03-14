from typing import Optional
from sqlmodel import SQLModel, Field


class Genre(SQLModel, table=True):
    __tablename__ = "genre"

    id_genre: Optional[int] = Field(default=None, primary_key=True)
    genre_name: str


class MusicGroups(SQLModel, table=True):
    __tablename__ = "musicgroups"

    id_group: Optional[int] = Field(default=None, primary_key=True)
    name: str
    albumCount: int = Field(ge=0)
    site: str
    id_genre: int = Field(foreign_key="genre.id_genre", index=True)