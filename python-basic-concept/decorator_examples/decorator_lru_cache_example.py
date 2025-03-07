from functools import lru_cache


@lru_cache(maxsize=3)
def my_calc(x: float) -> float:
    print(f"Calling my_calc with {x}")
    return (x * 10) + 32

if __name__ == '__main__':
    """
    Calling my_calc with 10.1
    Calling my_calc with 20.1
    Calling my_calc with 30.1
    Calling my_calc with 40.1
    Calling my_calc with 10.1
    """
    my_calc(10.1)
    my_calc(20.1)
    my_calc(20.1)
    my_calc(30.1)
    my_calc(20.1)
    my_calc(40.1)
    my_calc(30.1)
    my_calc(40.1) # cache size overflow -> remove cache: `my_calc(10.1)`
    my_calc(10.1)