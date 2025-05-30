from asyncio import AbstractEventLoop, Future, Task, TimerHandle
from collections import deque
from heapq import heappop, heappush
import time


class CustomEventLoop(AbstractEventLoop):
    def __init__(self):
        self._scheduled = []
        self._ready = deque()

    def call_later(self, delay, callback, *args, context=None):
        return self.call_at(self.time() + delay, callback, *args, context=context)

    def call_at(self, when, callback, *args, context=None):
        timer = TimerHandle(when, callback, args, self, context=context)
        heappush(self._scheduled, timer)
        return timer
        
    def create_future(self):
        return Future(loop=self)

    def create_task(self, coro, *, name=None, context=None):
        return Task(coro, loop=self, name=name, context=context)

    def time(self):
        return time.monotonic()

    def get_debug(self):
        pass
    
    def _timer_handle_cancelled(self, handle):
        pass
    
    def call_exception_handler(self, context):
        pass
    
    def run_forever(self):
        while True:
            self._run_once()
    
    def _run_once(self):
        while self._scheduled and self._scheduled[0]._when <= self.time():
            timer: TimerHandle = heappop(self._scheduled)
            self._ready.append(timer)
        
        len_ready = len(self._ready)
        for _ in range(len_ready):
            handle: TimerHandle = self._ready.popleft()
            handle._run() # 내부적으로 Task의 _step()도 함께 호출된다.

        timeout = 0
        if self._scheduled and not self._ready:
            timeout = max(0, self._scheduled[0]._when - self.time())
        
        time.sleep(timeout) # <- 무한루프에 빠질 위험이 있다
