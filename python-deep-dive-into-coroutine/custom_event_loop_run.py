import asyncio
from custom_event_loop import CustomEventLoop


async def coroutine1():
    print("coro1 first entry point")
    await asyncio.sleep(1)
    print("coro1 second entry point")

async def coroutine2():
    print("coro2 first entry point")
    await asyncio.sleep(2)
    print("coro2 second entry point")

loop = CustomEventLoop()
asyncio.set_event_loop(loop)

loop.create_task(coroutine1())
loop.create_task(coroutine2())

loop.run_forever()
