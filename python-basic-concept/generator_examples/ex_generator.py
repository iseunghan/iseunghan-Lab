from typing import Generator

def calculate(a: int, b: int) -> Generator[int | float, None, None]:
    """
    calculations는 Iteratable하기 때문에 for-loop으로 순회할 수 있다. 내부에 yield가 없을 때 까지 계속 생성기가 순회된다.
    next 함수로도 순회할 수 있지만, for-loop과 다르게 예외가 발생할 수 있다. (yield가 소진 되었을 때)
    """
    print(f"Starting calculations for {a} and {b}")

    print("Sum")
    yield a + b # yield가 있을 때, Generator는 잠시 멈추게 된다.

    print("Subtraction")
    yield a - b

    print("Multiplication")
    yield a * b

    print("Division")
    yield a / b

    print("Done calculating")


def run_generator_ex1():
    """
    [ console log ]
    <generator object calculate at 0x104e90660> <class 'generator'>
    Starting calculations for 10 and 5
    Sum
    Result:  15
    Subtraction
    Result:  5
    Multiplication
    Result:  50
    Division
    Result:  2.0
    Done calculating
    """
    calculations = calculate(10, 5)
    print(calculations, type(calculations))
    for result in calculations:
        print("----------------1")
        print("Result: ", result)
        print("----------------2")


def run_generator_ex2():
    """
    [ console log ]
    Starting calculations for 10 and 2
    Sum
    12
    Subtraction
    8
    Multiplication
    20
    Division
    5.0
    Done calculating
    Traceback (most recent call last):
      File "/Users/shlee/workspaces/study/iseunghan-Lab/python-basic-concept/generator_examples/ex_generator.py", line 39, in <module>
        run_generator_ex2()
      File "/Users/shlee/workspaces/study/iseunghan-Lab/python-basic-concept/generator_examples/ex_generator.py", line 34, in run_generator_ex2
        print(next(calculations))
    StopIteration
    """
    calculations = calculate(10, 2)
    print(next(calculations))
    print("----------------")
    print(next(calculations))
    print("----------------")
    print(next(calculations))
    print("----------------")
    print(next(calculations))
    print("----------------")
    print(next(calculations))
    print("----------------")


if __name__ == '__main__':
    # run_generator_ex1()
    run_generator_ex2()
