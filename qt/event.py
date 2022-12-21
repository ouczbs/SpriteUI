class EventBase:
    def __init__(self):
        self.funcs = []

    def connect(self, func):
        self.funcs.append(func)

    def __call__(self, *params):
        for func in self.funcs:
            func(*params)


class LabelItemEvent:
    SelectItem = EventBase()  # item , int 1 or 0
    ResizeItem = EventBase()  # pos, size
    ReName = EventBase()  # pos, size