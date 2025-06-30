# Generator에 대해서
다음 코드(gen_next_send_ex.py)를 살펴봅시다.
```python
def generator():
    print("start")
    val = yield "pause"
    print(val)
```

간단한 제네레이터 함수가 있습니다. 맨 처음 start를 출력하고, pause를 yield하고 마지막에 val에 들어온 값을 출력하고 종료가 되는 간단한 제네레이터 함수입니다.

다음 코드를 실행하면 어떻게 동작할까요?
```python
g = generator()
print(g.__next__())
print(next(g))
```
한줄 한줄 살펴보겠습니다.
- `g = generator()`: 제네레이터가 생성되고 콘솔엔 아무것도 출력되지 않습니다.
- `print(g.__next__())`: 다음 yield까지 진행합니다. 콘솔에는 "start"와 "pause"가 출력됩니다.
- `print(next(g))`: 다음 yield까지 진행합니다. 콘솔에는 None이 출력되고 다음 yield가 존재하지 않아 StopIteration 예외가 발생하고 종료됩니다.

또 다른 예제를 살펴보겠습니다.
```python
g = generator()
print(next(g))
print(g.send("hello"))
```
- `g = generator()`: 이전 예제와 동일합니다.
- `print(next(g))`: 이전 예제와 동일합니다.
- `print(g.send("hello"))`: 다음 yield까지 진행합니다. send를 통해 보낸 "hello" 값이 yield에 전달되고 val에 담기게 됩니다. 콘솔에는 "hello"가 출력되고 StopIteration 예외 발생하고 종료됩니다.

> send()만 단독으로 사용해도 되는가?
> 결론적으로 가능하다! 하지만 

## 제네레이터를 진행시키는 3가지 방법
1. `next(g)` 또는 `g.__next__()`
2. `g.send(any)`
3. `for-loop`을 활용한 방법

1,2 방법은 제네레이터의 다음 `yield`까지 진행시킨다는 점에서 동일한 행위를 수행합니다. 

차이점은 무엇일까요? 바로 g.send 함수는 `yield 표현식에 값을 밀어넣어주는 행위`까지 수행합니다. 즉, 위에서 본 `g.send("hello")` 처럼 hello 값이 val로 전달되었고 콘솔에 출력된 것까지 살펴볼 수 있었습니다.

next(g)를 기억하시나요? next는 내부적으로 [genobject.`gen_iternext()`](https://github.com/python/cpython/blob/fd6c5fe7869fd0519f2a222e769553b91815ff1a/Objects/genobject.c#L599)를 실행합니다. 다음 코드를 살펴보시죠.
```c
static PyObject *
gen_iternext(PyGenObject *gen)
{
    PyObject *result;
    assert(PyGen_CheckExact(gen) || PyCoro_CheckExact(gen));
    if (gen_send_ex2(gen, NULL, &result, 0, 0) == PYGEN_RETURN) {
        if (result != Py_None) {
            _PyGen_SetStopIterationValue(result);
        }
        Py_CLEAR(result);
    }
    return result;
}
```
함수 내부에 if 조건문을 보시면 gen_send_ex2에 arg 변수에 NULL을 전달하고 있습니다. 이로써 next 또는 __next__는 결국 send(None)를 수행한다고 이해할 수 있습니다.

### 그렇다면 next없이 send만 사용할 수 있는건가요?
우린 역시 예제 코드를 살펴보는게 가장 빠르기 때문에 다음 코드를 보겠습니다.
```python
g = generator()

print(g.send("one"))
print(g.send("two"))
```
위 코드를 실행하면 어떻게 될까요?
```python
print(g.send("one"))
      ^^^^^^^^^^^^^
TypeError: can't send non-None value to a just-started generator
```
generator를 시작하는 경우에는 None이 아닌 값을 send할 수 없다고 합니다! 위에서 next()는 내부적으로 send(None)을 한다고 말씀드렸죠? 그렇다면 예제를 다음과 같이 바꾸면 정상 작동할까요?
```python
g = generator()

print(g.send(None))
print(g.send("two"))
```
네 정상 작동하는 것을 확인할 수 있습니다. 이로써 더더욱 next()와 send(None)이 동일하다는 것을 확인할 수 있었습니다.
```python
start
pause
two
Traceback (most recent call last):
  File "/Users/shlee/workspaces/study/iseunghan-Lab/python-deep-dive-into-coroutine/gen_next_send_ex.py", line 13, in <module>
    print(g.send("two"))
          ^^^^^^^^^^^^^
StopIteration
```


3.for-loop을 활용한 방법은 다음 예제(gen_for_loop_ex.py)를 통해서 알아보겠습니다.
```python
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
```

for-loop generator 예제는 다음 코드와 동일하게 수행됩니다.
```python
gen = gen_count(3)
iterator = iter(gen)             # gen.__iter__()
while True:
    try:
        value = next(iterator)   # gen.__next__()
    except StopIteration:
        break
    print(value)
```

for-loop을 이용하면 좋은 점은 StopIteration 예외 처리를 자동으로 해준다는 점과 내부적으로 next를 자동으로 호출해준다는 점이 있습니다.
하지만 단점으로는 generator 내부에 값을 전달(send) 시키지는 못한다는 점이 있습니다. 단순 반복해야 하는 로직인 경우에는 for-loop을 사용하면 좋을 듯 합니다!

정리해보자면, 
- `next()` (`= send(None)`): generator 내부에 값을 전달하지 않아도 되는 경우, StopIteration 예외 처리를 클라이언트에서 해줘야 한다.
- `send(any)`: generator 내부에 값을 전달해야 하는 경우, 마찬가지로 StopIteration 예외 처리를 클라이언트에서 해줘야 한다.
- `for-loop`: generator 내부에 값을 전달하지 않아도 되고, 단순 반복 작업인 경우 StopIteration 에외 처리는 자동으로 해준다!
