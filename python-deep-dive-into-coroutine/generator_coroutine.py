import asyncio

"""
아래 코드는 동작하지 않습니다.
generator 기반 코루틴은 python 3.12 이후 버전부터 지원하지 않습니다. (ref. https://github.com/python/typeshed/issues/10116)
"""
# @asyncio.coroutine
def coroutine3():
    print("coroutine3 first entry point")
    yield from asyncio.sleep(1)
    print("coroutine3 second entry point")

import dis
dis.dis(coroutine3)