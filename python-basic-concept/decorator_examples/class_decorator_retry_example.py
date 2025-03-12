from typing import TypeAlias, Callable, Any

DecoratedFunc: TypeAlias = Callable[..., Any]

class Retry:
    def __init__(self, max_tries: int = 3) -> None:
        self.max_tries = max_tries

    def __call__(self, fn: DecoratedFunc) -> DecoratedFunc:
        def wrapper(*args, **kwargs) -> Any:
            for i in range(self.max_tries):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if i + 1 == self.max_tries:
                        raise e
                    print(f"{fn.__name__} failed with {e}, retrying..")
        return wrapper

@Retry(max_tries=2)
def my_calc(x: float) -> float:
    print(f"Calling my_calc with {x}")
    return (x - 32) * 10

if __name__ == '__main__':
    """
    Calling my_calc with 11.1
    Calling my_calc with 21.1
    Calling my_calc with 31.1 ### 첫 번째 시도 ###
    my_calc failed with unsupported operand type(s) for -: 'str' and 'int', retrying..
    Calling my_calc with 31.1 ### 두 번째 시도 ###
    ### max_tries에 도달하여 exception 발생 ###
    Traceback (most recent call last):
      File "/Users/shlee/workspaces/study/iseunghan-Lab/python-basic-concept/decorator_examples/decorator_retry_example.py", line 26, in <module>
        my_calc("31.1")
      File "/Users/shlee/workspaces/study/iseunghan-Lab/python-basic-concept/decorator_examples/decorator_retry_example.py", line 13, in wrapper
        raise e
      File "/Users/shlee/workspaces/study/iseunghan-Lab/python-basic-concept/decorator_examples/decorator_retry_example.py", line 10, in wrapper
        return fn(*args, **kwargs)
      File "/Users/shlee/workspaces/study/iseunghan-Lab/python-basic-concept/decorator_examples/decorator_retry_example.py", line 21, in my_calc
        return (x - 32) * 10
    TypeError: unsupported operand type(s) for -: 'str' and 'int'
    """
    my_calc(11.1)
    my_calc(21.1)
    my_calc("31.1")


