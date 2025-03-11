from typing import Generator

numbers_board = [
    [1,2,3],
    [4,5,6],
    [7,8,9]
]


def for_loop(board: list[list[int]]):
    for row in board:
        for cell in row:
            print(cell)


for_loop(numbers_board)
print("--------------------")

def cells(board: list[list[int]]) -> Generator[int, None, None]:
    for row in board:
        yield from columns(row)
        # 아래 for-loop을 위 한줄로 표현할 수 있다.
        # for cell in row:
            # yield cell


def columns(row: list[int]) -> Generator[int, None, None]:
    for column in row:
        yield column


cells_generator = cells(numbers_board)
print(cells_generator)
print(list(cells_generator))