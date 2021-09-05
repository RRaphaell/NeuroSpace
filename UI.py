from PyQt5 import QtWidgets, QtGui, QtCore
from utils import path_valid, get_default_widget
from functools import partial
from Controllers.WaveformController import WaveformController
from Controllers.SpikeController import SpikeController


class NeuroSpace(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        # initialize parameters
        self._file = None
        self.parameters_dock = None
        self.parameters_widget = None
        self.toolbar = None
        self.mdi = None
        self.window_key = 0
        self.open_windows_dict = {}

        self._add_menubar()
        self._add_toolbar()
        self._add_mdi()
        self._add_parameters_dock()
        self._add_properties_dock()

        self._set_geometry()
        self.setWindowTitle("NeuroSpace")
        self.showMaximized()
        self.setCentralWidget(self.mdi)

    def _set_geometry(self):
        desktop = QtWidgets.QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        height, width = screen_rect.height(), screen_rect.width()
        self.setGeometry(0, 30, width, height - 30)

    def _add_mdi(self):
        brush = QtGui.QBrush(QtGui.QColor(159, 159, 159))
        brush.setStyle(QtCore.Qt.Dense5Pattern)
        self.mdi = QtWidgets.QMdiArea()
        self.mdi.setBackground(brush)

    def resizeEvent(self, event):
        self._properties_dock.setFixedSize(int(self.width()*0.15), int(self.height()*0.4))
        self.parameters_dock.setFixedWidth(int(self.width() * 0.15))

    def _add_menubar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        open_action = QtWidgets.QAction("&Open", self)
        open_action.triggered.connect(self._get_file_for_open)
        file_menu.addAction(open_action)

    def _add_toolbar(self):
        self.toolbar = QtWidgets.QToolBar(self)
        waveform = QtWidgets.QAction(QtGui.QIcon("icons/waveform.png"), "Waveform", self)
        waveform.triggered.connect(self._on_waveform_icon_clicked)
        spike = QtWidgets.QAction(QtGui.QIcon("icons/spike.png"), "Spike", self)
        spike.triggered.connect(self._on_spike_icon_clicked)
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        self.toolbar.addAction(waveform)
        self.toolbar.addAction(spike)
        self.toolbar.addWidget(spacer)
        self.toolbar.setDisabled(True)
        self.addToolBar(self.toolbar)

    def _add_parameters_dock(self):
        self.parameters_dock = QtWidgets.QDockWidget("", self)
        self.parameters_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.parameters_dock)
        self.parameters_dock.setWidget(get_default_widget())

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
        self.toolbar.setEnabled(True)

    def _on_icon_clicked(self, obj, dialog_title):
        self.setDisabled(True)
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(dialog_title)
        controller = obj(dialog)
        self.open_windows_dict[self.window_key] = controller
        self.window_key += 1
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(controller.view)
        dialog.setLayout(lay)
        dialog.show()
        res = dialog.exec_()
        if res == QtWidgets.QDialog.Accepted:
            self.parameters_dock.setWidget(controller.view)
        self.setEnabled(True)

    def _on_waveform_icon_clicked(self):
        waveform_controller = partial(WaveformController, self._file, self.window_key, self.open_windows_dict,
                                      self.mdi, self.parameters_dock)
        self._on_icon_clicked(waveform_controller, dialog_title="Waveform")

    def _on_spike_icon_clicked(self):
        spike_controller = partial(SpikeController, self._file, self.window_key, self.open_windows_dict,
                                   self.mdi, self.parameters_dock)
        self._on_icon_clicked(spike_controller, dialog_title="Spike")
