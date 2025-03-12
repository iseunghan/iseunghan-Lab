from typing import Callable, Any


def register(func: Callable[..., Any]) -> Callable[..., Any]:
    results = []

    def wrapper(*args, **kwargs) -> Any:
        result = func(*args, **kwargs)
        results.append(result)
        print(f"Results: {results}")
        return result

    return wrapper

@register
def to_fahrenheit(celsius: float) -> float:
    return (celsius * 1.8) + 32

if __name__ == '__main__':
    """
    이게 어떻게 유지가 될까 궁금하다.
    자유변수와 클로저를 이용해 가능한 결과인데, 좀 더 개념을 파보자면..
    클로저(Closure)란 함수가 내부 함수를 포함하고 있는 형태를 의미하고, 내부 함수 밖에 있는 외부함수의 지역변수를 참조하는 형태이다.
    - 중첩 함수 형태
    - 내부 함수는 외부 함수의 지역변수를 참조하는 형태
    - 외부 함수는 내부 함수를 리턴하는 형태
    클로저를 사용하면 전역 변수 사용을 최소화하고 데이터 은닉 + 지속성을 보장 할 수 있다.
    """
    to_fahrenheit(10.0) # Results: [50.0]
    to_fahrenheit(20.0) # Results: [50.0, 68.0]
    to_fahrenheit(30.0) # Results: [50.0, 68.0, 86.0]

    """
    __closure__를 통해 자유 변수를 확인하는 방법
    클로저 속성은 cell 형태로 *scope에서 참조하는 변수를 보여줌
    (*scope란 정의된 변수가 보이는 유효범위를 의미)
    cell은 cell_contents를 통해서 자유변수의 값을 확인할 수 있다.
    """
    for cell in to_fahrenheit.__closure__:
        print(cell.cell_contents)
