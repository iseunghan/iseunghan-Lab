import time
from threading import Thread


def worker(start: int, end: int, _result: list):
    total = 0
    for i in range(start, end):
        total += i # <-- 이때 GIL이 개입한다.
    _result.append(total)


def run_multi_thread(start: int, end: int) -> int:
    _result = []
    _threads = [Thread(target=worker, name="half-calc-1", args=(start, end // 2, _result), daemon=True),
                Thread(target=worker, name="half-calc-2", args=(end // 2, end, _result), daemon=True)]

    _start = time.time()

    for th in _threads:
        th.start()
    for th in _threads:
        th.join()

    print(f"[run_multi_thread] elapsed time: {time.time() - _start}")
    return sum(_result, 0)


def run_single_thread(start: int, end: int) -> int:
    total = 0
    _start = time.time()
    for i in range(start, end):
        total += i
    print(f"[run_single_thread] elapsed time: {time.time() - _start}")
    return total


if __name__ == '__main__':
    START, END = 0, 1_000_000_000
    run_single_thread(START, END)   # [run_single_thread] elapsed time: 22.495970249176025
    run_multi_thread(START, END)    # [run_multi_thread] elapsed time: 22.594977140426636
