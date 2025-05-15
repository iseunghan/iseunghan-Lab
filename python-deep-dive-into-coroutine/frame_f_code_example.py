import dis
import inspect


def func():
    global frame
    x = 10
    y = 20
    print(x + y)
    frame = inspect.currentframe()

func()

print(frame.f_code is func.__code__)

# by docs: 컴파일된 날 바이트 코드의 문자열
print(func.__code__.co_code)
# b'd\x01}\x00d\x02}\x01t\x00|\x00|\x01\x17\x00\x83\x01\x01\x00t\x01\xa0\x02\xa1\x00a\x03d\x00S\x00'
print(list(func.__code__.co_code))
# [100, 1, 125, 0, 100, 2, 125, 1, 116, 0, 124, 0, 124, 1, 23, 0, 131, 1, 1, 0, 116, 1, 160, 2, 161, 0, 97, 3, 100, 0, 83, 0]

dis.dis(func)

import opcode
print(f"100: {opcode.opname[100]}")
print(f"125: {opcode.opname[125]}")

############## f_code.co_const ###############
print("############## f_code.co_const ###############")
print(f"func.co_consts: {func.__code__.co_consts}")
# >> func.co_consts: (None, 10, 20)

def func2(arg2="world") -> str:
    return f"Hello, {arg2}"

print(f"func2.co_consts: {func2.__code__.co_consts}")
# >> func2.co_consts: (None, 'Hello, ')
############## f_code.co_const ###############

############## f_code.co_varnames ###############
print(f"func.co_varnames: {func.__code__.co_varnames}")
# >> func.co_varnames: ('x', 'y')
############## f_code.co_varnames ###############


############## f_code.co_names ###############
print(f"func.co_names: {func.__code__.co_names}")
# >> func.co_names: ('print', 'inspect', 'currentframe', 'frame')
############## f_code.co_names ###############

