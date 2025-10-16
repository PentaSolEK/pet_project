import random
import time

import aiohttp
import asyncio
from asyncio import Semaphore


async def get_all_records(table: str, semaphore: Semaphore, skip: int = 0, limit: int = 100):
    url = f"http://127.0.0.1:8000/{table}/?skip={skip}&limit={limit}"
    async with semaphore:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(await response.text())
                        return True
                    else:
                        print(f'Ошибка: {response.status}')
        except Exception as e:
            print(f'Ошибка запроса: {e}')


async def main():
    t = time.time()
    semaphore = Semaphore(100)
    res = await asyncio.gather(
        *[get_all_records(random.choice(
            ['concerts', 'musicgroups', 'halls', 'sales', 'tickets']),
            semaphore)
            for _ in range(1000)
        ]
    )
    print(f"Успешных запросов: {len([successful_res for successful_res in res if successful_res is not None])}")
    print(f"Время выполнения: {time.time() - t:.5f}seconds")

asyncio.run(main())