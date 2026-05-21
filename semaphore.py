import asyncio
from datetime import datetime


sem = asyncio.Semaphore(3)

async def worker(delay: float, name: str):
    for i in range(4):
        now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f'[{now}] {name} -> step {i}')

        async with sem:
            now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            active = 3 - sem._value
            print(f'sem._value: {sem._value}')
            print(f'[{now}] Active: {active}')
            print(f'[{now}] {name} -> step {i} under the Semaphore')
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
        worker(0.3, 'Task D'),
    ]
    results = await asyncio.gather(*tasks)
    print('All results', results)

if __name__ == '__main__':
    asyncio.run(main())
