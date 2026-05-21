import asyncio
from asgiref.sync import sync_to_async
from datetime import datetime
import time


async def worker(delay: float, name: str):
    for i in range(4):
        now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f'[{now}] {name} -> step {i}')
        await asyncio.sleep(delay)
        print(f'Resources returns to {name}')
    now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    return f'[{now}] {name} finished by {delay} sec'

@sync_to_async
def sync_worker(delay: float, name: str):
    for i in range(4):
        now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f'[{now}] {name} -> step {i}')
        time.sleep(delay)
        print(f'Resources returns to {name}')
    now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    return f'[{now}] {name} finished by {delay} sec' 


async def main():
    tasks = [
        worker(1.5, 'Task A'),
        worker(0.8, 'Task B'),
        worker(2.6, 'Task C'),
        sync_worker(2.2, 'Task D')
    ]
    # res = sync_worker(2.2, 'Task D')
    results = await asyncio.gather(*tasks)
    # results.append(res)
    print('All results', results)

if __name__ == '__main__':
    asyncio.run(main())
