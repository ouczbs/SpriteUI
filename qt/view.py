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

    def init_ui(self):
        self.setScene(self.ui_scene)
        self.setDragMode(self.RubberBandDrag)

    def mousePressEvent(self, event):
        pos = event.pos()
        item = self.itemAt(pos)
        if item is None:
            self.isDrag = True
            self.drag_pos = pos
        if event.button() == Qt.RightButton:
            if isinstance(item, GraphicItem):
                LabelItemEvent.DeleteItem(item)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        print("mouseReleaseEvent")
        if self.isDrag:
            pos = event.pos()
            drag_pos = self.drag_pos
            drag_rect = self.drag_rect
            drag_rect.setLeft(min(drag_pos.x(), pos.x()))
            drag_rect.setRight(max(drag_pos.x(), pos.x()))
            drag_rect.setTop(min(drag_pos.y(), pos.y()))
            drag_rect.setBottom(max(drag_pos.y(), pos.y()))b
        self.isDrag = False
        super().mouseReleaseEvent(event)
