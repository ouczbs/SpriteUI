import threading
import numpy as np

from PyQt5.QtGui import QImage

class PromiseThread(threading.Thread):

    def __init__(self, func, *params):
        super().__init__()
        self.func = func
        self.next_funcs = []
        self.params = params

    def then(self, next_func):
        self.next_funcs.append(next_func)
        return self

    def run(self) -> None:
        self.func(*self.params)
        for func in self.next_funcs:
            func()


class SpriteUI():
    def __init__(self, pixmap):
        h, w, c = pixmap.shape
        self.h = h
        self.w = w
        self.c = c
        self.pixmap = pixmap
        self.mask = np.zeros(shape=(h, w), dtype="int64")
        self.sub_list = []

    def add_rect(self, rect):
        self.sub_list.append(rect)
        pass

    def toQImage(self):
        return self._QImage(self.pixmap)

    def _QImage(self, pixmap):
        shape = pixmap.shape
        w, h = shape[0], shape[1]
        c = len(shape) > 2 and shape[2] or 1
        bGray = c == 1
        bits_format = c == 4 and QImage.Format_RGBA8888 or QImage.Format_RGB888
        bits_format = bGray and QImage.Format_Grayscale8 or bits_format
        qImage = QImage(pixmap.tobytes(), w, h, w * c, bits_format)
        return qImage

    def toGrayQImage(self):
        pixmap = self.pixmap[:, :, 3]
        return self._QImage(pixmap)
