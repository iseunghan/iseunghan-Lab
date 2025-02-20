import threading
import time
from threading import current_thread


class Worker(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name            # thread 이름 지정

    def run(self):
        print(f"sub thread start {current_thread().name}")
        time.sleep(3)
        print(f"sub thread end {current_thread().name}")


print("main thread start")
threads = []
for i in range(5):
    t = Worker(f"thread {i}")       # sub thread 생성
    t.start()                       # sub thread의 run 메서드를 호출
    threads.append(t)

for th in threads:
    th.join()

print("main thread end")

# [ console log ]
# main thread start
# sub thread start thread 0
# sub thread start thread 1
# sub thread start thread 2
# sub thread start thread 3
# sub thread start thread 4
# sub thread end thread 3
# sub thread end thread 1
# sub thread end thread 0
# sub thread end thread 2
# sub thread end thread 4
# main thread end