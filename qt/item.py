from PyQt5.QtGui import QBrush, QColor, QPen, QPainter
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem
from PyQt5.QtCore import Qt, QRectF, QPointF
from event import *


# 继承枚举类
class Config:
    TOP = 1
    RIGHT = 2
    BOTTOM = 3
    LEFT = 4
    RIGHT_TOP = 5
    RIGHT_BOTTOM = 6
    LEFT_BOTTOM = 7
    LEFT_TOP = 8
    radius = 8
    Cursors = {
        TOP: Qt.SizeVerCursor,
        RIGHT: Qt.SizeHorCursor,
        BOTTOM: Qt.SizeVerCursor,
        LEFT: Qt.SizeHorCursor,
        RIGHT_TOP: Qt.SizeBDiagCursor,
        RIGHT_BOTTOM: Qt.SizeFDiagCursor,
        LEFT_BOTTOM: Qt.SizeBDiagCursor,
        LEFT_TOP: Qt.SizeFDiagCursor,
    }


_radius = Config.radius



class GraphicItem(QGraphicsRectItem):

    def __init__(self, name, size, clip, row=0):
        rect = QRectF(size.x() - _radius / 2, size.y() - _radius / 2, size.width() + _radius, size.height() + _radius)
        super().__init__(rect)
        self.size_dir = None
        self.mouse_pos = self.pos()
        self.size = size
        self.clip = clip
        self.row = row
        self.name = name or ""
        self.setPen(Qt.red)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.handles = {}
        self.updateHandles()

    def updateHandles(self):
        # _radius = Config.radius
        size, rect = self.size, self.rect()
        w, h = size.width() / 2, size.height() / 2
        x, y = w + rect.left(), h + rect.top()  # center

        self.handles[Config.TOP] = QRectF(x, y - h, _radius, _radius)
        self.handles[Config.RIGHT] = QRectF(x + w, y, _radius, _radius)
        self.handles[Config.LEFT] = QRectF(x - w, y, _radius, _radius)
        self.handles[Config.BOTTOM] = QRectF(x, y + h, _radius, _radius)

        self.handles[Config.RIGHT_TOP] = QRectF(x + w, y - h, _radius, _radius)
        self.handles[Config.RIGHT_BOTTOM] = QRectF(x + w, y + h, _radius, _radius)
        self.handles[Config.LEFT_BOTTOM] = QRectF(x - w, y + h, _radius, _radius)
        self.handles[Config.LEFT_TOP] = QRectF(x - w, y - h, _radius, _radius)

    def handleAt(self, point):
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, event):
        if self.isSelected():
            handle = self.handleAt(event.pos())
            cursor = handle and Config.Cursors[handle] or Qt.ArrowCursor
            self.size_dir = handle
            self.setCursor(cursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self.mouse_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.size_dir:
            self.interactiveResize(event.pos())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.size_dir = None
        self.update()

    def calcu_size(self, dx, dy):
        size, size_dir = QRectF(self.size), self.size_dir
        if size_dir == Config.TOP:
            size.setTop(size.top() + dy)
        elif size_dir == Config.RIGHT:
            size.setRight(size.right() + dx)
        elif size_dir == Config.BOTTOM:
            size.setBottom(size.bottom() + dy)
        elif size_dir == Config.LEFT:
            size.setLeft(size.left() + dx)
        elif size_dir == Config.RIGHT_TOP:
            size.setRight(size.right() + dx)
            size.setTop(size.top() + dy)
        elif size_dir == Config.RIGHT_BOTTOM:
            size.setRight(size.right() + dx)
            size.setBottom(size.bottom() + dy)
        elif size_dir == Config.LEFT_BOTTOM:
            size.setLeft(size.left() + dx)
            size.setBottom(size.bottom() + dy)
        elif size_dir == Config.LEFT_TOP:
            size.setLeft(size.left() + dx)
            size.setTop(size.top() + dy)
        return size

    def interactiveResize(self, mouse_pos):
        diff = mouse_pos - self.mouse_pos
        self.mouse_pos = mouse_pos
        dx, dy = diff.x(), diff.y()
        size = self.calcu_size(dx, dy)
        if size.width() < _radius or size.height() < _radius:
            size = QRectF(self.size)
            size.translate(dx, dy)
        self.tryChangeSize(size)

    def tryChangeSize(self, size):
        pos = QPointF(size.x(), size.y())
        if self.limit_rect_clip(size, self.pos(), pos):
            return
        LabelItemEvent.ResizeItem(self.pos(), size)
        self.prepareGeometryChange()
        self.size = size
        self.setRect(size.x() - _radius / 2, size.y() - _radius / 2, size.width() + _radius, size.height() + _radius)
        self.updateHandles()
        return True

    def paint(self, painter, option, widget=None):
        selected = self.isSelected()
        if selected:
            painter.setBrush(QBrush(QColor(255, 0, 0, 100)))
        painter.setPen(QPen(QColor(255, 255, 255), 1.0, Qt.SolidLine))
        painter.drawRect(self.size)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(QColor(0, 0, 0), 1.0, Qt.SolidLine))
        font, center = painter.fontMetrics(), self.size.center()
        width, height = font.width(self.name), font.height()
        painter.drawText(center.x() - width / 2, center.y() + height / 2, self.name)

        if not selected:
            return
        painter.setBrush(QBrush(QColor(0, 255, 0, 255)))
        painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        handles = self.handles
        for size_dir in range(1, 5):
            painter.drawRect(handles[size_dir])
        painter.setBrush(QBrush(QColor(0, 0, 255, 255)))
        for size_dir in range(5, 9):
            painter.drawEllipse(handles[size_dir])

    def limit_rect_clip(self, size, offset, pos):
        rect = QRectF(self.clip)
        rect.translate(- offset.x(), - offset.y())
        rect.setWidth(rect.width() - size.width())
        rect.setHeight(rect.height() - size.height())
        isClip = False
        if not rect.contains(pos):
            pos.setX(min(rect.right(), max(pos.x(), rect.left())))
            pos.setY(min(rect.bottom(), max(pos.y(), rect.top())))
            isClip = True
        return isClip

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            size = self.size
            self.limit_rect_clip(size, QPointF(size.x(), size.y()), value)
            LabelItemEvent.ResizeItem(value, size)
            return value
        if change == QGraphicsItem.ItemSelectedChange:
            LabelItemEvent.SelectItem(self, value)
        return super().itemChange(change, value)
