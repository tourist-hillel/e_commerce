import asyncio
from datetime import datetime


lock = asyncio.Lock()

async def worker(delay: float, name: str):
    for i in range(4):
        now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f'[{now}] {name} -> step {i}')

        async with lock:
            now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            print(f'[{now}] {name} -> step {i} under the Lock')
            await asyncio.sleep(delay)
            print(f'Resources returns to {name}')
        await asyncio.sleep(delay)
    now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    return f'[{now}] {name} finished by {delay} sec'


async def main():
    tasks = [
        worker(1.5, 'Task A'),
        worker(0.8, 'Task B'),
        worker(2.6, 'Task C'),
    ]
    results = await asyncio.gather(*tasks)
    print('All results', results)

if __name__ == '__main__':
    asyncio.run(main())
