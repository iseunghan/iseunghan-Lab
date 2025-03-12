import functools
from typing import Any, Callable


def announcer(func: Callable[..., Any]) -> Callable[..., Any]:
    print(f"Decorating {func.__name__}")
    
    @functools.wraps(func) # this active at call_2_with_functools; functools.wraps는 warpper 함수가 실제로 wrapped 된 함수처럼 보이도록 업데이트 합니다.
    def wrapper(*args, **kwargs) -> Any:
        print(f"Calling {func.__name__} with {args} and {kwargs}")
        result = func(*args, **kwargs)
        print(f"The result is {result}")
        return result
    return wrapper

@announcer
def to_fahrenheit(celsius: float) -> float:
    return (celsius * 1.8) / 32

def to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) / 1.8

to_celsius = announcer(to_celsius)


def call_1():
    """
    [ console log ]
    Decorating to_fahrenheit
    Decorating to_celsius
    Calling to_fahrenheit with (42.0,) and {}
    The result is 2.3625000000000003
    Calling to_fahrenheit with () and {'celsius': 11.0}
    The result is 0.61875
    Calling to_celsius with (452.0,) and {}
    The result is 233.33333333333331
    Calling to_celsius with () and {'fahrenheit': 111.0}
    The result is 43.888888888888886
    """
    to_fahrenheit(42.0)
    to_fahrenheit(celsius=11.0)
    to_celsius(452.0)
    to_celsius(fahrenheit=111.0)


def call_2():
    """
    [ console log ]
    Decorating to_fahrenheit
    Decorating to_celsius
    ****************  여기서 문제점  **************
    실제 fahrenheit, celsius 함수의 타입 어노테이션 정보가 아닌 wrapper의 타입 어노테이션 정보가 출력된다.
    이는 wrapper로 감싸져 이러한 현상이 발생하는 것이다.
    ********************************************
    <function announcer.<locals>.wrapper at 0x104e5fb50>
    {'return': typing.Any}
    <function announcer.<locals>.wrapper at 0x104f044c0>
    {'return': typing.Any}
    """
    print(to_fahrenheit)
    print(to_fahrenheit.__annotations__) # __annotations__는 `함수의 파라미터, 리턴타입`에 붙은 `타입 어노테이션`을 확인할 수 있다.
    print(to_celsius)
    print(to_celsius.__annotations__)


def call_2_with_functools():
    """
    [ console log ]
    Decorating to_fahrenheit
    Decorating to_celsius
    ******** 원래의 함수의 타입 어노테이션 정보가 정상적으로 출력된다! ***************
    <function to_fahrenheit at 0x1025cbb50>
    {'celsius': <class 'float'>, 'return': <class 'float'>}
    <function to_celsius at 0x102670550>
    {'fahrenheit': <class 'float'>, 'return': <class 'float'>}
    """
    print(to_fahrenheit)
    print(to_fahrenheit.__annotations__) # __annotations__는 `함수의 파라미터, 리턴타입`에 붙은 `타입 어노테이션`을 확인할 수 있다.
    print(to_celsius)
    print(to_celsius.__annotations__)

if __name__ == '__main__':
    # call_1()
    # call_2()
    call_2_with_functools()
