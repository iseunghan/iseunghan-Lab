def generator():
    print("start")
    val = yield "pause"
    print(val)

import dis
dis.dis(generator)

g = generator()

print(next(g)) # 또는 print(g.__next__())
print(g.send("hello?"))

# 실행결과
# start
# pause
# hello?
# Traceback (most recent call last):
#   File "/Users/shlee/workspaces/study/iseunghan-Lab/python-deep-dive-into-coroutine/gen_next_send_ex.py", line 12, in <module>
#     print(g.send("hello?"))
#           ^^^^^^^^^^^^^^^^
# StopIteration