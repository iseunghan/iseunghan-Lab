def generator():
    recv = yield 1
    return recv

import dis
dis.dis(generator)

gen = generator()
print(gen.send(None)) # 1
# print(gen.send(2)) # StopInteration: 2 (with Exception)

lasti = gen.gi_frame.f_lasti
print(f">> f_lasti: {lasti}")

code = gen.gi_code.co_code
op = code[lasti]

import opcode
print(f">> op: {op}, opname: {opcode.opname[op]}")
