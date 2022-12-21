from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt, QRectF

from item import GraphicItem
from event import *


class GraphicView(QGraphicsView):

    def __init__(self, ui_scene, parent=None):
        super().__init__(parent)
        self.mode = None
        self.ui_scene = ui_scene
        self.parent = parent
        self.isDrag = False
        self.drag_pos = None
        self.drag_rect = QRectF(0, 0, 0, 0)
        self.init_ui()
        self.offset = 0
        self.zoom_scale = 1

    def init_ui(self):
        self.setScene(self.ui_scene)
        self.setDragMode(self.RubberBandDrag)

    def initScale(self, scale, offset):
        self.zoom_scale = scale
        self.offset = offset / scale
        matrix = self.transform()
        matrix.reset()
        matrix.scale(scale, scale)
        self.setTransform(matrix)

    def mousePressEvent(self, event):
        pos = event.pos()
        item = self.itemAt(pos)
        if item is None or not isinstance(item, GraphicItem):
            self.isDrag = True
            self.drag_pos = pos
        if event.button() == Qt.RightButton:
            if isinstance(item, GraphicItem):
                LabelItemEvent.DeleteItem(item)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def deal_drag(self):
        if self.mode is None:
            self.ui_scene.AppendItem(self.drag_rect)

    def getZoomAxis(self, x1, x2):
        zoom_scale = self.zoom_scale
        if x1 > x2:
            x1, x2 = x2, x1
        return x1 / zoom_scale, x2 / zoom_scale

    def mouseReleaseEvent(self, event):
        if self.isDrag:
            pos = event.pos()
            drag_pos = self.drag_pos
            drag_rect = self.drag_rect
            left, right = self.getZoomAxis(drag_pos.x(), pos.x())
            top, bottom = self.getZoomAxis(drag_pos.y(), pos.y())
            drag_rect.setCoords(left, top, right, bottom)
            drag_rect.translate(-self.offset, -self.offset)
            self.deal_drag()
        self.isDrag = False
        super().mouseReleaseEvent(event)
