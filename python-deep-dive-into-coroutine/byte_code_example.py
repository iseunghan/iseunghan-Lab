import inspect

def func():
    global frame
    x = 10
    y = 20
    print(x + y)
    frame = inspect.currentframe()

func()

print(f"frame.f_lasti: {frame.f_lasti}")

import dis
dis.dis(func)
""" 실행결과 (console log)
30
frame.f_lasti: 30
6           0 LOAD_CONST               1 (10)
            2 STORE_FAST               0 (x)

7           4 LOAD_CONST               2 (20)
            6 STORE_FAST               1 (y)

8           8 LOAD_GLOBAL              0 (print)
            10 LOAD_FAST                0 (x)
            12 LOAD_FAST                1 (y)
            14 BINARY_ADD
            16 CALL_FUNCTION            1
            18 POP_TOP

9          20 LOAD_GLOBAL              1 (inspect)
            22 LOAD_METHOD              2 (currentframe)
            24 CALL_METHOD              0
            26 STORE_GLOBAL             3 (frame)
            28 LOAD_CONST               0 (None)
            30 RETURN_VALUE
"""