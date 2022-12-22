class EventBase:
    def __init__(self):
        self.funcs = []
        self.active = False

    def connect(self, func):
        self.funcs.append(func)

    def __call__(self, *params):
        if self.active:
            return
        self.active = True
        for func in self.funcs:
            func(*params)
        self.active = False


class LabelItemEvent:
    SelectItem = EventBase()  # item , int 1 or 0
    ResizeItem = EventBase()  # pos, size
    SelectList = EventBase()  # row
    ReNameItem = EventBase()  # row, name
    DeleteItem = EventBase()  # item
    AppendItem = EventBase()  # item


class ConfigEvent:
    OpenSprite = EventBase()  # path
