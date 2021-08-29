import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from Widgets.WaveformWidget import WaveformWidget


class NeuroSpace(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.add_toolbar()

        self.mdi = QtWidgets.QMdiArea()
        brush = QtGui.QBrush(QtGui.QColor(159, 159, 159))
        brush.setStyle(QtCore.Qt.Dense5Pattern)
        self.mdi.setBackground(brush)

        self.widget = QtWidgets.QDockWidget("Parameters", self)
        self.waveform_widget = WaveformWidget()
        self.widget.setWidget(self.waveform_widget)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.widget)

        self.properties = QtWidgets.QDockWidget("Properties", self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.properties)
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.addItem("item1")
        self.listWidget.addItem("item2")
        self.listWidget.addItem("item3")
        self.properties.setWidget(self.listWidget)
        self.properties.setFeatures(QtWidgets.QDockWidget.DockWidgetClosable)

        self.setCentralWidget(self.mdi)

        desktop = QtWidgets.QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        height = screen_rect.height()
        width = screen_rect.width()
        self.setGeometry(0, 30, width, height-30)
        self.setWindowTitle("NeuroSpace")
        self.showMaximized()

    def add_toolbar(self):
        toolbar = QtWidgets.QToolBar(self)

        waveform = QtWidgets.QAction(QtGui.QIcon("icons/waveform.png"), "Waveform", self)
        waveform.triggered.connect(self.show_waveform_widget)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        toolbar.addAction(waveform)
        toolbar.addWidget(spacer)
        self.addToolBar(toolbar)

    def show_waveform_widget(self):
        self.waveform_widget = WaveformWidget()
        sub = QtWidgets.QMdiSubWindow()
        sub.setWidget(self.waveform_widget)
        sub.setWindowTitle("Waveform")
        self.mdi.addSubWindow(sub)
        self.waveform_widget.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = NeuroSpace()
    win.show()
    sys.exit(app.exec_())