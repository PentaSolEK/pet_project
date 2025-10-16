from datetime import datetime

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from sqlmodel.ext.asyncio.session import AsyncSession

from models.db_models import Concert, ConcertBase
from data import concerts

@pytest.fixture()
def mock_async_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture()
def mock_concerts():
    mock_concerts = [
        Concert(name="test_concert1",
                date=datetime.now(),
                id_hall=1,
                id_concert=1),
        Concert(name="test_concert2",
                date=datetime.now(),
                id_hall=2,
                id_concert=2),
    ]
    return mock_concerts


class TestConcerts:
    @pytest.mark.asyncio
    async def test_get_all_concerts(self, mock_async_session, mock_concerts):
        mock_data = mock_concerts
        mock_result = MagicMock()
        mock_result.all.return_value = mock_data
        mock_async_session.exec.return_value = mock_result

        result = await concerts.get_all_concerts(common_param={"skip": 0, "limit": 100}, session=mock_async_session)

        assert result == mock_data
        mock_async_session.exec.assert_called_once()

        query = mock_async_session.exec.call_args[0][0]
        assert hasattr(query, "offset")
        assert hasattr(query, "limit")

        assert query._offset_clause.value == 0
        assert query._limit_clause.value == 100

    @pytest.mark.asyncio
    async def test_get_once_concert(self, mock_async_session, mock_concerts):
        mock_data = mock_concerts
        mock_result = MagicMock()
        for i in range(len(mock_data)):
            mock_result.first.return_value = mock_data[i]
            mock_async_session.exec.return_value = mock_result

            result = await concerts.get_concert_by_id(concert_id=i + 1, session=mock_async_session)

            assert result == mock_data[i]
            assert result.id_concert == i + 1

        assert mock_async_session.exec.call_count == 2

    @pytest.mark.asyncio
    async def test_create_concert(self, mock_async_session, mock_concerts):
        mock_data = mock_concerts
        mock_async_session.exec.return_value = mock_data[0]

        result = await concerts.create_conceert(concert=mock_data[0], session=mock_async_session)

        assert result.name == mock_data[0].name
        assert result.date == mock_data[0].date
        assert result.id_concert == mock_data[0].id_concert
        assert result.id_hall == mock_data[0].id_hall

        assert mock_async_session.exec.call_count == 1

    @pytest.mark.asyncio
    async def test_delete_concert(self, mock_async_session, mock_concerts):
        mock_data = mock_concerts
        mock_async_session.get.return_value = mock_data[0]

        result = await concerts.delete_concert(concert_id=mock_data[0].id_concert, session=mock_async_session)
        assert result.name == mock_data[0].name
        assert result.date == mock_data[0].date
        assert result.id_concert == mock_data[0].id_concert
