import math
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsScene, QSlider
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QLine

from event import *
from item import GraphicItem


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
        self.initItemList()

    def initItemList(self):
        LabelItemEvent.SelectList.connect(self.SelectList)
        LabelItemEvent.ReNameItem.connect(self.ReNameItem)
        LabelItemEvent.DeleteItem.connect(self.DeleteItem)

    def ReNameItem(self, row, new_name):
        sprite = self.data.sprite
        sprite.ReNameItem(row, new_name)
        ui_rect = self.ui_rectList[row]
        if ui_rect.name == new_name:
            return
        ui_rect.name = new_name
        ui_rect.prepareGeometryChange()

    def SelectList(self, row):
        ui_rect = self.ui_rectList[row]
        if not ui_rect or ui_rect.isSelected():
            return
        self.clearSelection()
        ui_rect.setSelected(True)

    def setSprite(self, ui_pixmap):
        self.ui_sprite.setPixmap(ui_pixmap)
        self.data.ui_pixmap = ui_pixmap

    def AppendItem(self, drag_rect):
        sprite = self.data.sprite
        x, y, w, h = drag_rect.x(), drag_rect.y(), drag_rect.width(), drag_rect.height()
        name, loc = sprite.AppendItem([x, y, w, h])
        rectItem = GraphicItem(name, QRectF(x, y, w, h), self.sceneRect(), loc)
        self.addItem(rectItem)
        self.ui_rectList.append(rectItem)
        LabelItemEvent.AppendItem(rectItem)

    def DeleteItem(self, item):
        sprite = self.data.sprite
        row = item.row
        sprite.DeleteItem(row)
        self.removeItem(item)
        self.ui_rectList[row] = None
    def makeItemList(self):
        sub_list = self.data.sprite.sub_list
        name_list = self.data.sprite.name_list
        size = len(sub_list)
        self.clear()
        self.ui_sprite = self.addPixmap(self.data.ui_pixmap)
        self.ui_rectList = []
        scene_clip = self.sceneRect()
        for i in range(size):
            name = name_list[i]
            x, y, w, h = sub_list[i]
            rectItem = GraphicItem(name, QRectF(x, y, w, h), scene_clip, i)
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
