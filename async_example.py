import asyncio


async def fetch_data(endpoint: str):
    print(f'{endpoint} fetching started!')
    await asyncio.sleep(1.2)
    print(f'{endpoint} fetching ended!')
    return f'Data from {endpoint}'


def sync_call_data(endpoint: str):
    print(f'{endpoint} fetching started!')
    print(f'{endpoint} fetching ended!')
    return f'Data from {endpoint}'


async def main():
    print('Main function run')
    result1 = await fetch_data('API1')
    result2 = await fetch_data('API2')
    result3 = sync_call_data('API3')
    print('Results:', result1, result2, result3)


if __name__ == '__main__':
    asyncio.run(main())
