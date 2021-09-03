import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from Widgets.WaveformWidget import WaveformWidget
from utils import path_valid, partial_dock_widget, get_default_widget


class NeuroSpace(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self._file = None
        self._parameters_dock = None
        self._parameters_widget = None
        self._toolbar = None

        self._add_menubar()
        self._add_toolbar()

        brush = QtGui.QBrush(QtGui.QColor(159, 159, 159))
        brush.setStyle(QtCore.Qt.Dense5Pattern)
        self.mdi = QtWidgets.QMdiArea()
        self.mdi.setBackground(brush)

        self._add_parameters_dock()
        self._add_properties_dock()

        desktop = QtWidgets.QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        height, width = screen_rect.height(), screen_rect.width()
        self.setGeometry(0, 30, width, height-30)
        self.setWindowTitle("NeuroSpace")
        self.showMaximized()
        self.setCentralWidget(self.mdi)

    def resizeEvent(self, event):
        self._properties_dock.setFixedSize(int(self.width()*0.2), int(self.height()*0.4))
        self._parameters_dock.setFixedWidth(int(self.width() * 0.2))

    def _add_menubar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        open_action = QtWidgets.QAction("&Open", self)
        open_action.triggered.connect(self._get_file_for_open)
        file_menu.addAction(open_action)

    def _add_toolbar(self):
        self._toolbar = QtWidgets.QToolBar(self)
        waveform = QtWidgets.QAction(QtGui.QIcon("icons/waveform.png"), "Waveform", self)
        waveform.triggered.connect(self._show_waveform_widget)
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        self._toolbar.addAction(waveform)
        self._toolbar.addWidget(spacer)
        self._toolbar.setDisabled(True)
        self.addToolBar(self._toolbar)

    def _add_parameters_dock(self):
        self._parameters_dock = QtWidgets.QDockWidget("", self)
        self._parameters_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1), self._parameters_dock)
        self._parameters_dock.setWidget(get_default_widget())

    def _add_properties_dock(self):
        self._properties_view = QtWidgets.QTreeWidget()
        self._properties_view.setHeaderLabels(["properties", "value"])

        self._properties_dock = QtWidgets.QDockWidget("", self)
        self._properties_dock.setWidget(self._properties_view)
        self._properties_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1), self._properties_dock)

    def _set_properties(self, properties: dict):
        for key, value in properties.items():
            item = QtWidgets.QTreeWidgetItem([str(key), str(value)])
            self._properties_view.addTopLevelItem(item)

    def _get_file_for_open(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        if not file_name:
            return

        self._file = path_valid(file_name)
        if not self._file:
            self.error_popup("File path is incorrect", "File Error")
            return

        property_dct = dict()
        property_dct['file name'] = self._file.__dict__["raw_data_path"]
        property_dct["clr date"] = self._file.__dict__["clr_date"]
        property_dct["duration"] = self._file.recordings[0].__dict__["duration"]
        self._set_properties(property_dct)
        self._toolbar.setEnabled(True)

    def _show_waveform_widget(self):
        self.setDisabled(True)
        dialog = QtWidgets.QDialog()
        self.waveform_widget = WaveformWidget(self._file, self.mdi, dialog=dialog)
        plot_partial = partial_dock_widget(self._parameters_dock, self.waveform_widget)
        close_partial = partial_dock_widget(self._parameters_dock, get_default_widget())
        self.waveform_widget.set_plot_window_clicked_func(plot_partial)
        self.waveform_widget.set_plot_window_close_func(close_partial)

        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.waveform_widget)
        dialog.setLayout(lay)
        dialog.show()
        res = dialog.exec_()
        if res == QtWidgets.QDialog.Accepted:
            self._parameters_dock.setWidget(self.waveform_widget)
        self.setEnabled(True)
