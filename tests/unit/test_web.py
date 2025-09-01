import pytest
from web.concerts import get_all_concerts
from service.common_params import commonDep
from data.init_db import SessionDep

async def test_concerts_get_all():
    response = await get_all_concerts(SessionDep, commonDep)
    assert type(response) == list