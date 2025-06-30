def gen_count(limit):
    print("Start")
    n = 1
    while n <= limit:
        print(f"Yield: {n}")
        yield n
        n += 1
    print("End")

# for-loop를 사용해 generator 순회
for value in gen_count(3):
    print(f"Received from gen: {value}")

# [ 실행결과 ]
# start
# Yield: 1
# Received from gen: 1
# Yield: 2
# Received from gen: 2
# Yield: 3
# Received from gen: 3
# end