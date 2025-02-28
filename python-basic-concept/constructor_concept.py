class Point():
    def __new__(cls, *args, **kwargs):
        print(f"__new__, cls: {cls}, args: {args}, kwargs: {kwargs}")
        obj = super(Point, cls).__new__(cls)
        return obj

    def __init__(self, x=0, y=0):
        print(f"__init__, x: {x}, y: {y}")
        self.x = x
        self.y = y

p1 = Point(1, 4)
# __new__, cls: <class '__main__.Point'>, args: (1, 4), kwargs: {}
# __init__, x: 1, y: 4
