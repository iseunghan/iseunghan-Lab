from typing import Generator

large_numbers_dataset = list(range(1,11))
print(large_numbers_dataset)

def square_even(numbers: list[int]) -> Generator[int, None, None]:
    for n in numbers:
        if n % 2 == 0:
            yield n**2


def client_1():
    """
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    <generator object square_even at 0x1029385f0>
    [4, 16, 36, 64, 100]
    """
    squared = square_even(large_numbers_dataset)
    print(squared)
    print(list(squared))

    # list(squared) 를 풀어서 쓰면 다음과 같다.
    # for square in squared:
    #     print(square)

def client_2():
    """
    컴프리헨션 표현식이지만 괄호로 묶으면 제네레이터 표현식이 된다. generator 함수와 유사한 generator 객체를 반환한다.
    """
    squared_exp = (n ** 2 for n in large_numbers_dataset if n % 2 == 0)
    print(squared_exp)
    print(list(squared_exp))

def client_3_memory_good():
    """
    220 출력, generator를 이용하여 중간 변수를 만들지 않고 처리하기 때문에 메모리 효율적이다.
    """
    print(sum(n ** 2 for n in large_numbers_dataset if n % 2 == 0))

client_3_memory_good()
