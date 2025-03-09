import random
from typing import Generator


def send_message(message: str) -> str:
    print(f"Sending: {message}")
    return str(random.randint(1, 1000))

def chat(message: str) -> Generator[str, str, None]:
    print("Starting a new chat")
    history = []

    while True:
        print(f">> message: {message}")
        history.append(message)
        response = send_message(message)
        history.append(response)
        print("before yield")
        message = yield response
        print("after yield")

if __name__ == '__main__':
    """
    Starting a new chat              <-- 최초 1회 실행
    >> message: hello
    Sending: hello
    before yield
    > Before Use Yield Field
    215                             <-- yield에서 일시 정지 되어 있는 것이다. 
    < After Use Yield Field
    ---------------
    after yield                     <-- 다음 next()로 인해 실행
    >> message: how are you doing?
    Sending: how are you doing?
    before yield
    > Before Use Yield Field
    87
    < After Use Yield Field
    after yield                    <-- 다음 next()로 인해 실행
    >> message: oh, that is nice!
    Sending: oh, that is nice!
    before yield
    > Before Use Yield Field
    789
    < After Use Yield Field
    """
    quick_chat = chat("hello")
    res1 = next(quick_chat)
    print("> Before Use Yield Field")
    print(res1)
    print("< After Use Yield Field")
    print("---------------")

    res2 = quick_chat.send("how are you doing?")
    print("> Before Use Yield Field")
    print(res2)
    print("< After Use Yield Field")

    res3 = quick_chat.send("oh, that is nice!")
    print("> Before Use Yield Field")
    print(res3)
    print("< After Use Yield Field")
