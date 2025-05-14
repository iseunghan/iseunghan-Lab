import inspect

def funcA():
    frame = inspect.currentframe()
    print(f"funcA: {frame.f_back}")
    x = 10
    y = 20
    z = x + y
    funcB(z)

def funcB(z):
    frame = inspect.currentframe()
    print(f"funcB: {frame.f_back}")
    print(z)


frame = inspect.currentframe()
print(f"main: {frame.f_back}")
funcA()