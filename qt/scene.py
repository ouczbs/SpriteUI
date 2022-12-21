import math
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsScene, QSlider
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QLine

from qt.item import GraphicItem


class GraphicScene(QGraphicsScene):

    def __init__(self, data, parent=None):
        super().__init__(parent)
        # settings
        self.data = data
        self.ui_rectList = None
        self.ui_sprite = None
        self.grid_size = 20
        self.grid_squares = 5

        self._color_background = QColor('#393939')
        self._color_light = QColor('#2f2f2f')
        self._color_dark = QColor('#292929')

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.setBackgroundBrush(self._color_background)
        self.setSceneRect(0, 0, 600, 600)

    def setSprite(self, ui_pixmap):
        self.ui_sprite.setPixmap(ui_pixmap)
        self.data.ui_pixmap = ui_pixmap

    def changeSelect(self, row):
        self.clearSelection()
        self.item_list[row].setSelected(True)
    def makeItemList(self):
        sub_list = self.data.sprite.sub_list
        item_list = self.data.item_list
        size = len(sub_list)
        self.clear()
        self.ui_sprite = self.addPixmap(self.data.ui_pixmap)
        self.ui_rectList = []
        scene_clip = self.sceneRect()
        for i in range(size):
            item = item_list[i]
            x, y, w, h = sub_list[i]
            rectItem = GraphicItem(item, QRectF(x, y, w, h), scene_clip)
            self.addItem(rectItem)
            self.ui_rectList.append(rectItem)
        pass

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mousePressEvent(event)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            if x % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if y % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        # draw the lines
        painter.setPen(self._pen_light)
        if lines_light:
            painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        if lines_dark:
            painter.drawLines(*lines_dark)
