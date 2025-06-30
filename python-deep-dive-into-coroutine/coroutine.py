import asyncio

# native-coroutine 함수
async def coroutine1():
    print("coro1 first entry point")
    await asyncio.sleep(1)
    print("coro1 second entry point")

async def coroutine2():
    print("coro2 first entry point")
    await asyncio.sleep(1)
    print("coro2 second entry point")

loop = asyncio.get_event_loop()
loop.create_task(coroutine1())
loop.create_task(coroutine2())
loop.run_forever()

# [ 실행 결과 ]
# coro1 first entry point
# coro2 first entry point
# coro1 second entry point
# coro2 second entry point

#-----------------------------------------
import dis
dis.dis(coroutine1)