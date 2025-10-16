import aiohttp
import pytest
import asyncio
import http


class TestConcerts:
    @pytest.mark.asyncio
    async def test_get_all_concerts(self, skip: int = 0, limit: int = 100):
        url = f"http://127.0.0.1:8000/concerts/?skip={skip}&limit={limit}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(await response.text())


async def main():
    test = TestConcerts()
    await asyncio.gather(
        *[test.test_get_all_concerts(limit=5) for _ in range(3)]
    )


asyncio.run(main())