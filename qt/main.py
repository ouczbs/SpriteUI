import cgitb
import sys
from PIL import Image
from PyQt5.QtCore import QStringListModel, QModelIndex
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSlider, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QScrollArea, \
    QPushButton, QDockWidget, QLineEdit, QGridLayout, QFormLayout, QListView, QAbstractItemView, QGraphicsPixmapItem
from PyQt5.QtWidgets import QMainWindow

from event import *
from scene import GraphicScene
from sprite import *
from view import GraphicView

sys.path.append("../py")
import py.algorithm as algorithm, py.merge as merge

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
        self.isInitItem = None
        self.ui_x, self.ui_y, self.ui_w, self.ui_h = None, None, None, None
        LabelItemEvent.SelectItem.connect(self.SelectItem)
        LabelItemEvent.ResizeItem.connect(self.ResizeItem)
        LabelItemEvent.ReNameItem.connect(self.ReNameItem)
        self.resize(200, 100)
        self.initWidget()
        self.bindItem()

    def ReNameItem(self, _, new_name):
        self.name_changed(new_name)
        pass

    def ResizeItem(self, pos, size):
        self.isInitItem = True
        x, y, w, h = str(pos.x() + size.x()), str(pos.y() + size.y()), str(size.width()), str(size.height())
        self.ui_x.setText(x)
        self.ui_y.setText(y)
        self.ui_w.setText(w)
        self.ui_h.setText(h)
        self.isInitItem = None

    def SelectItem(self, item, show):
        if show == 1:
            self.item = item
            self.ResizeItem(item.pos(), item.size)
            self.isInitItem = True
            self.ui_name.setText(item.name)
            self.isInitItem = None
            self.show()
        else:
            self.item = None
            self.hide()

    def size_changed(self, value):
        if self.isInitItem:
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

    def name_changed(self, value):
        if self.isInitItem:
            return
        self.ui_name.setText(value)
        LabelItemEvent.ReNameItem(self.item.row, value)

    def bindItem(self):
        self.ui_name.textChanged.connect(self.name_changed)
        self.ui_x.textChanged.connect(self.size_changed)
        self.ui_y.textChanged.connect(self.size_changed)
        self.ui_w.textChanged.connect(self.size_changed)
        self.ui_h.textChanged.connect(self.size_changed)

    def initWidget(self):
        detail = QWidget(self)
        ui_form = QFormLayout()
        self.ui_name = QLineEdit(detail)
        ui_form.addRow("Name", self.ui_name)
        ui_pos, self.ui_x, self.ui_y, self.ui_w, self.ui_h = makeRectWidget(detail)
        ui_form.addRow("Position", ui_pos)
        detail.setLayout(ui_form)
        self.setWidget(detail)


class LabelList(QListView):
    def __init__(self, data, parent):
        super().__init__(parent)
        self.data = data
        self.isInitItem = False
        LabelItemEvent.SelectItem.connect(self.SelectItem)
        LabelItemEvent.ReNameItem.connect(self.ReNameItem)
        LabelItemEvent.AppendItem.connect(self.AppendItem)
        LabelItemEvent.DeleteItem.connect(self.DeleteItem)
        self.clicked.connect(self.item_clicked)
        pass

    def AppendItem(self, item):
        model = self.model()
        if not model:
            return
        model.insertRow(item.row)
        index = self.model().index(item.row)
        model.setData(index, item.name, 0)
        pass

    def DeleteItem(self, item):
        model = self.model()
        if not model:
            return
        model.removeRow(item.row)

    def makeList(self):
        sprite = self.data.sprite
        model = QStringListModel(self)
        model.setStringList(sprite.name_list)
        model.dataChanged.connect(self.name_changed)
        self.setModel(model)
        self.setVisible(True)

    def SelectItem(self, item, show):
        if not self.model():
            return
        if show == 1:
            index = self.currentIndex()
            if index.row() != item.row:
                index = self.model().index(item.row)
                self.setCurrentIndex(index)
        pass

    def item_clicked(self, index):
        LabelItemEvent.SelectList(index.row())

    def ReNameItem(self, row, new_name):
        sprite = self.data.sprite
        sprite.ReNameItem(row, new_name)
        model = self.model()
        if not model:
            return
        if self.isInitItem:
            return
        index = model.index(row)
        model.setData(index, new_name, 0)
        pass

    def name_changed(self, index):
        new_name = self.model().data(index, 0)
        self.isInitItem = True
        LabelItemEvent.ReNameItem(index.row(), new_name)
        self.isInitItem = False
        pass


class LabelImage(QWidget):
    def __init__(self, data, parent):
        super().__init__()
        self.ui_merge = None
        self.ui_split = None
        self.ui_mark = None
        self.ui_detail = None
        self.ui_tips = None
        self.threads = {}
        self.parent = parent
        self.data = data
        self.ui_list = LabelList(data, self)
        ui_pixmap = QPixmap.fromImage(data.sprite.toQImage())
        data.ui_pixmap = ui_pixmap
        self.width, self.height = ui_pixmap.width(), ui_pixmap.height()
        self.ui_bg = QLabel(self)
        self.ui_scene = GraphicScene(data, self.ui_bg)
        self.ui_scene.setSceneRect(QRectF(0, 0, self.width, self.height))
        self.ui_scene.makeItemList()
        self.ui_view = GraphicView(self.ui_scene, self.ui_bg)
        self.initScale(1)
        self.initWidget()
        self.isGray = False

    def initScale(self, scale):
        more_size, center_offset, border = 256, 128, 20
        width, height = int(self.width * scale), int(self.height * scale)
        self.ui_bg.resize(width + more_size, height + more_size)
        self.ui_view.resize(width + border, height + border)
        self.ui_view.initScale(scale, border / 2)

    def ui_gray_clicked(self, button_gray):
        self.isGray = not self.isGray
        data = self.data
        if self.isGray:
            button_gray.setText("RGB")
            ui_pixmap = QPixmap.fromImage(data.sprite.toGrayQImage())
            self.ui_scene.setSprite(ui_pixmap)
            pass
        else:
            button_gray.setText("alpha")
            ui_pixmap = QPixmap.fromImage(data.sprite.toQImage())
            self.ui_scene.setSprite(ui_pixmap)
            pass

    def ui_mark_clicked(self):
        self.ui_tips.setText("is in marking")
        algorithm.markMaskBg(self.data.sprite, 3, -1, 100)
        self.ui_mark.setVisible(False)
        self.threads["mark"] = True
        self.ui_tips.setText("marking success")
        pass

    def ui_split_clicked(self):
        if "mark" not in self.threads:
            self.ui_mark_clicked()
        self.ui_tips.setText("is in split")
        sprite = self.data.sprite
        rectGrow = algorithm.makeRegionRectGrow()
        seeds_generator = algorithm.seedsAll_yield(sprite)
        algorithm.run_all(rectGrow, sprite, seeds_generator)
        self.ui_list.makeList()
        self.ui_scene.makeItemList()
        self.ui_merge.setVisible(True)
        self.threads["split"] = True
        pass

    def ui_merge_clicked(self):
        merge.checkMergeRects(self.data.sprite)
        self.ui_tips.setText("size = " + str(len(self.data.sprite.sub_list)))
        self.ui_list.makeList()
        self.ui_scene.makeItemList()
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

    def initWidget(self):
        self.ui_detail = LabelDetail(self.parent)

        ui_scroll = QScrollArea(self)
        ui_scroll.setWidget(self.ui_bg)

        ui_ver = QVBoxLayout()
        ui_hor = QHBoxLayout()
        ui_title = self.initTitle()

        ui_ver.addLayout(ui_title)
        ui_ver.addWidget(ui_scroll)

        ui_list = self.ui_list
        ui_hor.addLayout(ui_ver)
        ui_hor.addWidget(ui_list)
        ui_hor.setStretchFactor(ui_ver, 3)
        ui_hor.setStretchFactor(ui_list, 1)
        ui_list.setVisible(False)
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
        self.data.pixmap = pixmap
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
