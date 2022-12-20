import sys
import cgitb
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QStringListModel
from sprite import *
from PIL import Image
import numpy as np
from PyQt5.QtWidgets import QApplication, QSlider, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QScrollArea, \
    QPushButton, QDockWidget, QLineEdit, QGridLayout, QFormLayout, QListView, QAbstractItemView
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QMainWindow

from scene import GraphicScene
from view import GraphicView
from item import GraphicItem, GraphicItemEvent
import sys

sys.path.append("../py")
import algorithm, merge

cgitb.enable(format("text"))
gWorld = None


def makeRectWidget(parent):
    ui_grid = QGridLayout()
    ui_x_tip = QLabel("X", parent)
    ui_x = QLineEdit(parent)
    ui_grid.addWidget(ui_x_tip, 0, 0)
    ui_grid.addWidget(ui_x, 0, 1)

    ui_y_tip = QLabel("Y", parent)
    ui_y = QLineEdit(parent)
    ui_grid.addWidget(ui_y_tip, 0, 2)
    ui_grid.addWidget(ui_y, 0, 3)

    ui_w_tip = QLabel("W", parent)
    ui_w = QLineEdit(parent)
    ui_grid.addWidget(ui_w_tip, 1, 0)
    ui_grid.addWidget(ui_w, 1, 1)

    ui_h_tip = QLabel("H", parent)
    ui_h = QLineEdit(parent)
    ui_grid.addWidget(ui_h_tip, 1, 2)
    ui_grid.addWidget(ui_h, 1, 3)
    return ui_grid, ui_x, ui_y, ui_w, ui_h


class LabelDetail(QDockWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.hide()
        self.setWindowTitle("Detail Panel")
        self.setFloating(True)
        self.setAllowedAreas(Qt.TopDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.item, self.ui_name = None, None
        self.isPreChangeItem = None
        self.ui_x, self.ui_y, self.ui_w, self.ui_h = None, None, None, None
        GraphicItemEvent.SelectItem.connect(self.SelectItem)
        GraphicItemEvent.ResizeItem.connect(self.ResizeItem)
        self.resize(200, 100)
        self.initWidget()
        self.bindItem()

    def ResizeItem(self, pos, size):
        self.isPreChangeItem = True
        x, y, w, h = str(pos.x() + size.x()), str(pos.y() + size.y()), str(size.width()), str(size.height())
        self.ui_x.setText(x)
        self.ui_y.setText(y)
        self.ui_w.setText(w)
        self.ui_h.setText(h)
        self.isPreChangeItem = None

    def SelectItem(self, item, show):
        if show == 1:
            self.item = item
            self.ResizeItem(item.pos(), item.size)
            self.isPreChangeItem = True
            self.ui_name.setText(item.name)
            self.isPreChangeItem = None
            self.show()
        else:
            self.item = None
            self.hide()

    def textChanged(self, value):
        if self.isPreChangeItem:
            return
        self.item.name = self.ui_name.text()
        if value == self.ui_name.text():
            self.item.prepareGeometryChange()
            return
        x, y = self.ui_x.text(), self.ui_y.text()
        w, h = self.ui_w.text(), self.ui_h.text()
        try:
            x, y, w, h = float(x), float(y), float(w), float(h)
        except:
            return
        pos = self.item.pos()
        self.item.tryChangeSize(QRectF(x - pos.x(), y - pos.y(), w, h))
        pass

    def bindItem(self):
        self.ui_name.textChanged.connect(self.textChanged)
        self.ui_x.textChanged.connect(self.textChanged)
        self.ui_y.textChanged.connect(self.textChanged)
        self.ui_w.textChanged.connect(self.textChanged)
        self.ui_h.textChanged.connect(self.textChanged)

    def initWidget(self):
        detail = QWidget(self)
        ui_form = QFormLayout()
        self.ui_name = QLineEdit(detail)
        ui_form.addRow("Name", self.ui_name)
        ui_pos, self.ui_x, self.ui_y, self.ui_w, self.ui_h = makeRectWidget(detail)
        ui_form.addRow("Position", ui_pos)
        detail.setLayout(ui_form)
        self.setWidget(detail)


class LabelImage(QWidget):
    def __init__(self, data, parent):
        super().__init__()
        self.ui_merge = None
        self.ui_split = None
        self.ui_mark = None
        self.threads = {}
        self.ui_list = None
        self.ui_detail = None
        self.ui_tips = None
        self.parent = parent
        self.data = data
        pixmap = QPixmap.fromImage(data.sprite.toQImage())
        self.width, self.height = pixmap.width(), pixmap.height()
        self.ui_bg = QLabel(self)
        self.ui_scene = GraphicScene(self.ui_bg)
        scene_clip = QRectF(0, 0, self.width, self.height)
        self.ui_scene.setSceneRect(scene_clip)
        self.ui_sprite = self.ui_scene.addPixmap(pixmap)
        self.ui_view = GraphicView(self.ui_scene, self.ui_bg)
        self.initScale(1)
        self.initWidget()

        rectItem = GraphicItem("label_item", QRectF(0, 0, 320, 240), scene_clip)
        rectItem.addToScene(self.ui_scene)
        self.isGray = False

    def initScale(self, scale):
        more_size, center_offset, border = 256, 128, 20
        width, height = int(self.width * scale), int(self.height * scale)
        self.ui_bg.resize(width + more_size, height + more_size)
        self.ui_view.resize(width + border, height + border)
        matrix = self.ui_view.transform()
        matrix.reset()
        matrix.scale(scale, scale)
        self.ui_view.setTransform(matrix)

    def ui_gray_clicked(self, button_gray):
        self.isGray = not self.isGray
        data = self.data
        if self.isGray:
            button_gray.setText("RGB")
            pixmap = QPixmap.fromImage(data.sprite.toGrayQImage())
            self.ui_sprite.setPixmap(pixmap)
            # self.sprite.setPixmap(self.img.set)
            pass
        else:
            button_gray.setText("alpha")
            pixmap = QPixmap.fromImage(data.sprite.toQImage())
            self.ui_sprite.setPixmap(pixmap)
            pass

    def thread_mark_then(self):
        self.ui_tips.setText("marking success")
        self.threads["mark"] = None
        self.ui_mark.setVisible(False)
        pass

    def thread_split_then(self):
        self.ui_tips.setText("split success")
        self.threads["split"] = None
        print(len(self.data.sprite.sub_list))
        self.ui_merge.setVisible(True)
        pass

    def ui_mark_clicked(self):
        if "mark" in self.threads and self.threads["mark"] is not None:
            return
        self.ui_tips.setText("is in marking")
        thread = PromiseThread(algorithm.markMaskBg, self.data.sprite, 3, -1, 100).then(self.thread_mark_then)
        thread.start()
        self.threads["mark"] = thread
        pass

    def ui_split_clicked(self):
        if "mark" not in self.threads:
            self.ui_mark_clicked()
            self.threads["mark"].then(self.ui_split_clicked)
            return
        self.ui_tips.setText("is in split")
        sprite = self.data.sprite
        rectGrow = algorithm.makeRegionRectGrow()
        seeds_generator = algorithm.seedsAll_yield(sprite)
        thread = PromiseThread(algorithm.run_all, rectGrow, sprite, seeds_generator).then(self.thread_split_then)
        thread.start()
        self.threads["split"] = thread
        pass

    def ui_merge_clicked(self):
        merge.checkMergeRects(self.data.sprite)
        self.ui_tips.setText("size = " + str(len(self.data.sprite.sub_list)))
        pass

    def initTitle(self):
        ui_tips = QLabel("", self)
        self.ui_tips = ui_tips
        ui_mark = QPushButton("mark", self)
        ui_mark.clicked.connect(self.ui_mark_clicked)

        ui_split = QPushButton("split", self)
        ui_split.clicked.connect(self.ui_split_clicked)

        ui_merge = QPushButton("merge", self)
        ui_merge.clicked.connect(self.ui_merge_clicked)
        ui_merge.setVisible(False)
        self.ui_mark = ui_mark
        self.ui_split = ui_split
        self.ui_merge = ui_merge

        ui_gray = QPushButton("Gray", self)
        ui_gray.clicked.connect(lambda: self.ui_gray_clicked(ui_gray))
        ui_title = QLabel("Sprite Zoom", self)
        ui_zoom = QSlider(Qt.Horizontal, ui_title)  # 1
        ui_zoom.setRange(0, 100)  # 2
        ui_zoom.valueChanged.connect(lambda: self.zoom(ui_zoom.value()))
        ui_hor = QHBoxLayout()
        ui_hor.addWidget(ui_tips)
        ui_hor.addStretch(1)
        ui_hor.addWidget(ui_mark)
        ui_hor.addWidget(ui_split)
        ui_hor.addWidget(ui_merge)
        ui_hor.addWidget(ui_gray)
        ui_hor.addWidget(ui_title)
        ui_hor.addWidget(ui_zoom)
        return ui_hor

    def initList(self):
        ui_list = QListView(self)
        item_list = ['item %s' % i for i in range(11)]  # 1
        model = QStringListModel(self)
        model.setStringList(item_list)
        self.data.item_list = item_list
        ui_list.setModel(model)
        ui_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        ui_list.clicked.connect(self.change_func)
        ui_list.setVisible(False)
        return ui_list

    def change_func(self, index):
        # print(self, index, self.data.item_list[index.row()])
        # self.ui_list.clearSelection()
        pass

    def initWidget(self):
        self.ui_detail = LabelDetail(self.parent)

        ui_scroll = QScrollArea(self)
        ui_scroll.setWidget(self.ui_bg)

        ui_ver = QVBoxLayout()
        ui_hor = QHBoxLayout()
        ui_title = self.initTitle()

        ui_ver.addLayout(ui_title)
        ui_ver.addWidget(ui_scroll)

        self.ui_list = self.initList()
        ui_hor.addLayout(ui_ver)
        ui_hor.addWidget(self.ui_list)
        self.setLayout(ui_hor)

    def zoom(self, value):
        self.initScale(1 + value / 10)
        pass


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.labelImage = LabelImage(app.data, self)
        self.setCentralWidget(self.labelImage)
        self.setMinimumHeight(600)
        self.setMinimumWidth(600)
        self.setWindowTitle("图集切割")


class SpriteApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        global gWorld
        gWorld = self
        self.data = type("Data", (), {})
        self.ui = type("UI", (), {})
        self.initData('./all.png')
        self.initWidget()

    def run(self):
        self.ui.main.show()
        sys.exit(self.exec_())

    def initData(self, path):
        image = Image.open(path)
        pixmap = np.array(image)
        self.data.sprite = SpriteUI(pixmap)

    def initWidget(self):
        main = MainWindow(self)
        # compatible with Mac Retina screen.
        self.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        self.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        main.show()
        self.ui.main = main

    pass


def demo_run():
    app = SpriteApp(sys.argv)
    app.run()


if __name__ == '__main__':
    demo_run()
