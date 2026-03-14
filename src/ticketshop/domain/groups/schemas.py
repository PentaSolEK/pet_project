from pydantic import BaseModel, Field


class GenreBase(BaseModel):
    genre_name: str = Field(min_length=1, max_length=45)


class GenrePublic(BaseModel):
    id_genre: int


class MusicgroupsBase(BaseModel):
    name: str = Field(min_length=1, max_length=45)
    albumCount: int = Field(ge=0)
    site: str = Field(min_length=1, max_length=45)
    id_genre: int

class MusicgroupsPublic(MusicgroupsBase):
    id_group: int


class MusicgroupsUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=45)
    albumCount: int | None = Field(default=None, ge=0)
    site: str | None = Field(default=None, min_length=1, max_length=45)
    id_genre: int | None = None