> 목표
> - 코루틴에 동작방식을 이해할 수 있다.
> - 간단한 파이썬 바이트 코드를 다룰 수 있다.
> - `Value Stack`, `Call Stack`, `Frame` 객체에 대해서 얇고 넓게 배운다.


# Coroutine이란 무엇인가?

다음은 간단한 코루틴 예제가 있습니다. 실행 결과는 어떻게 될까요?
```python
import asyncio

async def coroutine1():
    print("coroutine1 first entry point")
    await asyncio.sleep(1)
    print("coroutine1 second entry point")

async def coroutine2():
    print("coroutine2 first entry point")
    await asyncio.sleep(2)
    print("coroutine2 second entry point")

loop = asyncio.get_event_loop()
loop.create_task(coroutine1())
loop.create_task(coroutine2())
loop.run_forever()
```
실행결과:
```bash
# coroutine1 first entry point
# coroutine2 first entry point
# coroutine1 second entry point
# coroutine2 second entry point
```
실행결과를 보면 coroutine1과 coroutine2가 섞여서(?) 출력이 되었습니다. 왜 이렇게 동작하는지에 대해서 완벽하게 이해하는게 목표입니다!

## Resuming & Suspending
코루틴을 알기 위해서는 실행(또는 이전 지점 재개)과 일시중지로 작동하는 것을 알아야 합니다.
이전 예제를 다시 살펴봅시다.
```python
async def coroutine1():
->  print("coroutine1 first entry point")
<-  await asyncio.sleep(1)
->  print("coroutine1 second entry point")

async def coroutine2():
->  print("coroutine2 first entry point")
<-  await asyncio.sleep(2)
->  print("coroutine2 second entry point")
```
- `->`: Resuming (실행 또는 재개)
- `<-`: Suspending (일시중지)

실행결과를 보면, coroutine1 함수의 첫 번째 print문이 실행되고, 그 다음 라인에 await를 만나 1초동안 일시정지 상태가 됩니다. 마찬가지로 coroutine2 함수의 첫 번째 print문이 실행되고, await를 만나 2초 일시정지 되는 동안 coroutine1의 마지막 print -> coroutine2의 마지막 print가 실행되고 종료되게 됩니다.

그렇다면 여기서 의문이 들 수 있습니다. await를 만나면 일시정지 상태가 되는가? 반은 맞고 반은 틀립니다. await는 일시정지가 될 가능성이 있다는 `힌트`일 뿐입니다. 


# REFERENCES
- [Deep Dive into Coroutine - 김대희](https://youtu.be/NmSeLspQoAA?feature=shared)