import inspect

def func():
    global frame
    x = 10
    y = 20
    print(x + y)
    frame = inspect.currentframe()

func()

print(f"frame.f_locals: {frame.f_locals}")
print(f"frame.f_lasti: {frame.f_lasti}")
print(f"frame.f_back: {frame.f_back}")
print(f"frame.f_code: {frame.f_code}")

print(frame.f_code is func.__code__)