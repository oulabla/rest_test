import asyncio
import janus
import time
import random
from concurrent.futures import ThreadPoolExecutor

def queue_task(queue):
    for i in range(5):
        time.sleep(1)
        queue.sync_q.put(i)
        print(f'Thread Put {i}')
    queue.sync_q.put(None)

async def main():
    print('Start main')
    loop = asyncio.get_running_loop()
    queue = janus.Queue()
    executor = ThreadPoolExecutor()
    future = loop.run_in_executor(executor, queue_task, queue)
    print("Start looping")
    while (data := await queue.async_q.get()) is not None:
        print(f'Got {data} ')
    # while(data := await queue.async_q.get()) is not None:
    #     print(f'Got data: {data}')
    print('Done cycle')
    await future
    queue.close()
    print('Closing queue ...')
    await queue.wait_closed()
    print('Done')

if __name__ == '__main__':
    asyncio.run(main())