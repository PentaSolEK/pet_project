from datetime import datetime

import pytest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.ticketshop.domain.concerts.models import Concerts
from src.ticketshop.domain.concerts import repo


@pytest.fixture()
def mock_async_session():
    session = AsyncMock()
    session.exec = AsyncMock()
    session.get = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.delete = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture()
def mock_concerts():
    return [
        Concerts(name="test_concert1", date=datetime.now(), id_hall=1, id_concert=1),
        Concerts(name="test_concert2", date=datetime.now(), id_hall=2, id_concert=2),
    ]


class TestConcertsRepo:
    @pytest.mark.asyncio
    async def test_list_concerts(self, mock_async_session, mock_concerts):
        mock_data = mock_concerts
        mock_result = MagicMock()
        mock_result.all.return_value = mock_data
        mock_async_session.exec.return_value = mock_result

        result = await repo.list_Concerts(
            mock_async_session, limit=100, offset=0
        )

        assert result == mock_data
        mock_async_session.exec.assert_called_once()

        query = mock_async_session.exec.call_args[0][0]
        assert hasattr(query, "offset")
        assert hasattr(query, "limit")

    @pytest.mark.asyncio
    async def test_get_concert(self, mock_async_session, mock_concerts):
        mock_data = mock_concerts
        for i, concert in enumerate(mock_data):
            mock_async_session.get.return_value = concert

            result = await repo.get_Concerts(mock_async_session, Concerts_id=i + 1)

            assert result == concert
            assert result.id_concert == i + 1

    @pytest.mark.asyncio
    async def test_create_concert(self, mock_async_session, mock_concerts):
        mock_data = mock_concerts[0]
        mock_async_session.refresh = AsyncMock(side_effect=lambda x: None)

        result = await repo.create_Concerts(mock_async_session, mock_data)

        assert result.name == mock_data.name
        assert result.date == mock_data.date
        assert result.id_concert == mock_data.id_concert
        assert result.id_hall == mock_data.id_hall
        mock_async_session.add.assert_called_once()
        mock_async_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_concert(self, mock_async_session, mock_concerts):
        mock_data = mock_concerts[0]

        await repo.delete_Concerts(mock_async_session, mock_data)

        mock_async_session.delete.assert_called_once_with(mock_data)
        mock_async_session.commit.assert_called_once()

