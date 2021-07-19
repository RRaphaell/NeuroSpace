import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from timeStamp_info import *
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from functools import partial

McsData.VERBOSE = False
style.use('seaborn-dark')
matplotlib.use('Qt5Agg')
plt.rcParams['legend.loc'] = "upper right"
font = {'weight' : 'bold',
        'size'   : 8}
matplotlib.rc('font', **font)


class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super().__init__()
        self._changed = False
        self.view().pressed.connect(self.handleItemPressed)
        self.last_was_ticked = True

    def setItemChecked(self, index, checked=False):
        item = self.model().item(index, self.modelColumn()) # QStandardItem object
        if checked:
            item.setCheckState(Qt.Checked)
        else:
            item.setCheckState(Qt.Unchecked)
        self.last_was_ticked = False

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
            self.last_was_ticked = False
        else:
            item.setCheckState(Qt.Checked)
            self.last_was_ticked = True
        self._changed = True

    def hidePopup(self):
        if not self._changed:
            super().hidePopup()
        self._changed = False
        if not self.last_was_ticked:
            for i in range(self.count()):
                if self.itemChecked(i):
                    self.setCurrentIndex(i)
                    break
            else:
                self.setCurrentIndex(1)

    def itemChecked(self, index):
	    item = self.model().item(index, self.modelColumn())
	    return item.checkState() == Qt.Checked



class MEA_app(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()

        self.tabs.addTab(self.tab1, "Waveform")
        self.tabs.addTab(self.tab2, "Spike")
        self.tabs.addTab(self.tab3, "Stimulus")

        self.create_tab1()
        self.create_tab2()
        self.create_tab3()

        # QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))

        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.dir_path, "images", "app_icon.png")))
        # როცა აპლიკაციის სახეს მივცემთ ეს 3 ხაზი წესით აღარ დაჭირდება რომ ტასკბარზე აიქონ გამოჩნდეს
        # import ctypes
        # myappid = 'mycompany.myproduct.subproduct.version'
        # ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        File = open(os.path.join(self.dir_path, "styles/main_style.qss"), "r")
        with File:
            qss = File.read()
            self.setStyleSheet(qss)

        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet("QStatusBar{color:blue;font-weight:bold;font-size:10}")

        self.add_toolbar()

        desktop = QtWidgets.QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        height = screen_rect.height()
        width = screen_rect.width()
        self.setGeometry(0, 30, width, height-30)
        self.setWindowTitle("MEA System Analyzer")
        self.setCentralWidget(self.tabs)
        self.showMaximized()

    def resizeEvent(self, event):
        self.group_box_browse_tab1.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_channel_stream_tab1.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_from_to_tab1.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_filter_tab1.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_algo.setFixedSize(int(self.width() * 0.2), int(self.height() * 0.08))
        self.group_box_reduced_by.setFixedSize(int(self.width() * 0.2), int(self.height() * 0.08))
        self.plot_file_btn_tab1.setFixedSize(int(self.width()*0.2), int(self.height()*0.05))
        self.group_box_extract_tab1.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))

        self.group_box_channel_stream_tab2.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_pre_post_tab2.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_from_to_tab2.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_threshold_tab2.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_filter_tab2.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.plot_file_btn_tab2.setFixedSize(int(self.width()*0.2), int(self.height()*0.05))
        self.group_box_burst_tab2.setFixedSize(int(self.width()*0.2), int(self.height()*0.11))
        self.group_box_bin_tab2.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_extract_tab2.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))

        self.group_box_channel_stream_tab3.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_pre_post_tab3.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_from_to_tab3.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_threshold_tab3.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.group_box_filter_tab3.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.plot_file_btn_tab3.setFixedSize(int(self.width()*0.2), int(self.height()*0.05))
        self.group_box_extract_tab3.setFixedSize(int(self.width()*0.2), int(self.height()*0.08))
        self.component.setFixedWidth(int(self.width()*0.05))

    def add_toolbar(self):
        toolbar = QtWidgets.QToolBar(self)

        btn_combine = QtWidgets.QAction(QtGui.QIcon("images/merge_icon.png"), "Merge files", self)
        btn_combine.setStatusTip("Choose folder to combine all files from it")
        btn_combine.triggered.connect(lambda x: self.combine_spikes())

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        btn_help = QtWidgets.QAction(QtGui.QIcon("images/help_icon.png"), "Help", self)
        btn_help.setStatusTip("Comming soon")
        # btn_combine.triggered.connect(lambda x: self.help()) coming soon

        toolbar.addAction(btn_combine)
        toolbar.addWidget(spacer)
        toolbar.addAction(btn_help)
        self.addToolBar(toolbar)

    def create_tab3(self):
        tab3_layout = QtWidgets.QGridLayout()
        self.statusBar()

        self.tab3_stimulus = []
        self.group_box_channel_stream_tab3, self.channel_id_tab3 = self.create_group_select_id()
        self.group_box_pre_post_tab3, self.extract_pre_tab3, self.extract_post_tab3, self.dead_time_tab3 = self.create_group_select_time_range_tab2()
        self.extract_pre_tab3.setText("0.001")
        self.extract_post_tab3.setText("0.001")
        self.dead_time_tab3.setText("0.02")
        self.extract_pre_tab3.setStatusTip("Recommended: 0.001 (s)")
        self.extract_post_tab3.setStatusTip("Recommended: 0.001 (s)")
        self.dead_time_tab3.setStatusTip("Recommended: 0.02 (s)")

        self.group_box_threshold_tab3, self.threshold_from_tab3, self.threshold_to_tab3 = self.create_group_threshold()
        self.threshold_from_tab3.setStatusTip("Default: -0.0003 (V)")
        self.group_box_threshold_tab3.toggled.connect(lambda : self.clear_qlines(self.threshold_from_tab3, self.threshold_to_tab3))
        self.threshold_to_tab3.setDisabled(True)

        self.group_box_from_to_tab3, self.extract_from_tab3, self.extract_to_tab3 = self.create_group_select_time_range_tab1()
        self.group_box_from_to_tab3.toggled.connect(lambda : self.clear_qlines(self.extract_from_tab3, self.extract_to_tab3))

        self.group_box_filter_tab3, self.filter_low_tab3, self.filter_high_tab3 = self.create_group_filter()
        self.group_box_filter_tab3.toggled.connect(lambda : self.clear_qlines(self.filter_low_tab3, self.filter_high_tab3))

        self.group_box_extract_tab3, self.extract_text_box_tab3, self.extract_btn_tab3 = self.create_group_extract()
        self.extract_btn_tab3.clicked.connect(self.save_stimulus)

        self.plot_file_btn_tab3 = QtWidgets.QPushButton(self)
        self.plot_file_btn_tab3.setText("Plot Stimulus")
        self.plot_file_btn_tab3.clicked.connect(self.plot_stimulus)

        plots_names = ["Average Stimulus", "Stimulus", "Frequency"]
        self.tab3_is_plot_visible = [2]*len(plots_names)
        plot_group_box, self.tab3_canvas, self.tab3_plot_check_boxes, _ = self.create_plot_grop_box("Stimulus", False, plots_names)
        for i in range(len(self.tab3_plot_check_boxes)):
            self.tab3_plot_check_boxes[i].stateChanged.connect(partial(self.check_plotes_visibility, self.tab3_is_plot_visible, self.tab3_canvas, i))
        self.tab3_plot_check_boxes[-1].setChecked(False)

        tab3_layout.addWidget(self.group_box_channel_stream_tab3, 0, 0)
        tab3_layout.addWidget(self.group_box_pre_post_tab3, 1, 0)
        tab3_layout.addWidget(self.group_box_from_to_tab3, 2, 0)
        tab3_layout.addWidget(self.group_box_threshold_tab3, 3, 0)
        tab3_layout.addWidget(self.group_box_filter_tab3, 4, 0)
        tab3_layout.addWidget(self.plot_file_btn_tab3, 5, 0)
        tab3_layout.setRowStretch(6, 0)
        tab3_layout.addWidget(self.group_box_extract_tab3, 7, 0)
        tab3_layout.addWidget(plot_group_box, 0, 2, 8, 1)
        self.tab3.setLayout(tab3_layout)

    def create_tab2(self):
        tab2_layout = QtWidgets.QGridLayout()
        self.statusBar()

        self.group_box_channel_stream_tab2, self.channel_id_tab2 = self.create_group_select_id(checkable_combo=True)
        self.group_box_pre_post_tab2, self.extract_pre_tab2, self.extract_post_tab2, self.dead_time_tab2 = self.create_group_select_time_range_tab2()
        self.extract_pre_tab2.setText("0.001")
        self.extract_post_tab2.setText("0.001")
        self.dead_time_tab2.setText("0.003")
        self.extract_pre_tab2.setStatusTip("Recommended: 0.001 (s)")
        self.extract_post_tab2.setStatusTip("Recommended: 0.001 (s)")
        self.dead_time_tab2.setStatusTip("Recommended: 0.003 (s)")

        self.group_box_threshold_tab2, self.threshold_from_tab2, self.threshold_to_tab2 = self.create_group_threshold()
        self.group_box_threshold_tab2.setStatusTip("Select Threshold. Recommended: -0.00012 (V)")
        self.threshold_from_tab2.setStatusTip("Default: calculate std deviation. (V)     Recommended: -0.00012 (V)")
        self.group_box_threshold_tab2.toggled.connect(lambda : self.clear_qlines(self.threshold_from_tab2, self.threshold_to_tab2))

        self.group_box_filter_tab2, self.filter_low_tab2, self.filter_high_tab2 = self.create_group_filter()
        self.group_box_filter_tab2.toggled.connect(lambda : self.clear_qlines(self.filter_low_tab2, self.filter_high_tab2))

        self.group_box_from_to_tab2, self.extract_from_tab2, self.extract_to_tab2 = self.create_group_select_time_range_tab1()
        self.group_box_from_to_tab2.toggled.connect(lambda : self.clear_qlines(self.extract_from_tab2, self.extract_to_tab2))

        self.group_box_burst_tab2, self.tab2_max_start, self.tab2_max_end, self.tab2_min_interval, self.tab2_min_duration, self.tab2_min_number = self.create_group_burst()
        self.tab2_max_start.setStatusTip("Recommended: 0.01 (s)")
        self.tab2_max_end.setStatusTip("Recommended: 0.01 (s)")
        self.tab2_min_interval.setStatusTip("Recommended: 0.01 (s)")
        self.tab2_min_duration.setStatusTip("Recommended: 0.02 (s)")
        self.tab2_min_number.setStatusTip("Recommended: 4")
        self.group_box_burst_tab2.toggled.connect(lambda : self.clear_qlines(self.tab2_max_start, self.tab2_max_end, self.tab2_min_interval,
                                                                    self.tab2_min_duration, self.tab2_min_number))

        self.group_box_bin_tab2, self.tab2_bin = self.create_group_bins()
        self.tab2_bin.setStatusTip("Recommended: 10 (s)")
        self.group_box_bin_tab2.toggled.connect(lambda : self.clear_qlines(self.tab2_bin))

        self.group_box_extract_tab2, self.extract_text_box_tab2, self.extract_btn_tab2 = self.create_group_extract()
        self.extract_btn_tab2.clicked.connect(self.save_spike)

        self.plot_file_btn_tab2 = QtWidgets.QPushButton(self)
        self.plot_file_btn_tab2.setText("Plot Spike")
        self.plot_file_btn_tab2.clicked.connect(self.plot_spike)

        plots_names = ["Spike together", "Spikes", "Bin Frequency"]
        self.tab2_is_plot_visible = [2]*len(plots_names)
        plot_group_box, self.tab2_canvas, self.tab2_plot_check_boxes, self.component  = self.create_plot_grop_box("Spike", True, plots_names)
        self.tab2_is_canvas_clicked = [False]
        for i in range(len(self.tab2_plot_check_boxes)):
            self.tab2_plot_check_boxes[i].stateChanged.connect(partial(self.check_plotes_visibility, self.tab2_is_plot_visible, self.tab2_canvas, i))

        tab2_layout.addWidget(self.group_box_channel_stream_tab2, 0, 0)
        tab2_layout.addWidget(self.group_box_pre_post_tab2, 1, 0)
        tab2_layout.addWidget(self.group_box_from_to_tab2, 2, 0)
        tab2_layout.addWidget(self.group_box_threshold_tab2, 3, 0)
        tab2_layout.addWidget(self.group_box_filter_tab2, 4, 0)
        tab2_layout.addWidget(self.plot_file_btn_tab2, 5, 0)
        tab2_layout.addWidget(self.group_box_burst_tab2, 6, 0)
        tab2_layout.addWidget(self.group_box_bin_tab2, 7, 0)
        tab2_layout.setRowStretch(8, 0)
        tab2_layout.addWidget(self.group_box_extract_tab2, 9, 0)
        tab2_layout.addWidget(plot_group_box, 0, 2, 10, 1)
        self.tab2.setLayout(tab2_layout)

    def create_group_select_time_range_tab2(self):
        group_box_pre_post = QtWidgets.QGroupBox("Select time parameters")
        group_box_pre_post_layout = QtWidgets.QHBoxLayout()

        extract_pre_tab2 = QtWidgets.QLineEdit(self)
        extract_pre_label = QtWidgets.QLabel(self)
        extract_pre_label.setText("Pre")
        extract_pre_label.setFont(QtGui.QFont('Arial', 7))

        extract_post_tab2 = QtWidgets.QLineEdit(self)
        extract_post_label = QtWidgets.QLabel(self)
        extract_post_label.setText("Post")
        extract_post_label.setFont(QtGui.QFont('Arial', 7))

        dead_time_tab2 = QtWidgets.QLineEdit(self)
        dead_time_label = QtWidgets.QLabel(self)
        dead_time_label.setText("Dead time")
        dead_time_label.setFont(QtGui.QFont('Arial', 7))

        group_box_pre_post_layout.addWidget(extract_pre_label)
        group_box_pre_post_layout.addWidget(extract_pre_tab2)
        group_box_pre_post_layout.addWidget(extract_post_label)
        group_box_pre_post_layout.addWidget(extract_post_tab2)
        group_box_pre_post_layout.addWidget(dead_time_label)
        group_box_pre_post_layout.addWidget(dead_time_tab2)
        group_box_pre_post.setLayout(group_box_pre_post_layout)
        group_box_pre_post.setStatusTip("Choose particular time (second)")
        return group_box_pre_post, extract_pre_tab2, extract_post_tab2, dead_time_tab2

    def create_group_burst(self):
        group_box_burst = QtWidgets.QGroupBox("Select Burst Parameters (s)")
        group_box_burst_layout = QtWidgets.QGridLayout()
        group_box_burst.setCheckable(True)

        max_start = QtWidgets.QLineEdit(self)
        max_start.setStatusTip("Max. Interval to start burst (s)")
        max_start_label = QtWidgets.QLabel(self)
        max_start_label.setText("Max: start")
        max_start_label.setFont(QtGui.QFont('Arial', 7))
        max_start.setText("0.01")

        max_end = QtWidgets.QLineEdit(self)
        max_end.setStatusTip("Max. Interval ro end burst (s)")
        max_end_label = QtWidgets.QLabel(self)
        max_end_label.setText("end")
        max_end_label.setFont(QtGui.QFont('Arial', 7))
        max_end.setText("0.01")

        time_unit = QtWidgets.QLabel(self)
        time_unit.setText("s")
        time_unit.setFont(QtGui.QFont('Arial', 7))

        min_interval = QtWidgets.QLineEdit(self)
        min_interval.setStatusTip("Min. Interval between bursts (s)")
        min_interval_label = QtWidgets.QLabel(self)
        min_interval_label.setText("Min: betw.")
        min_interval_label.setFont(QtGui.QFont('Arial', 7))
        min_interval.setText("0.01")

        min_duration = QtWidgets.QLineEdit(self)
        min_duration.setStatusTip("Min. duration of bursts (s)")
        min_duration_label = QtWidgets.QLabel(self)
        min_duration_label.setText("dur.")
        min_duration_label.setFont(QtGui.QFont('Arial', 7))
        min_duration.setText("0.02")

        min_number = QtWidgets.QLineEdit(self)
        min_number.setStatusTip("Min number of spikes")
        min_number_label = QtWidgets.QLabel(self)
        min_number_label.setText("numb.")
        min_number_label.setFont(QtGui.QFont('Arial', 7))
        min_number.setText("4")

        group_box_burst_layout.addWidget(max_start_label, 0, 0)
        group_box_burst_layout.addWidget(max_start, 0, 1)
        group_box_burst_layout.addWidget(max_end_label, 0, 2)
        group_box_burst_layout.addWidget(max_end, 0, 3)
        group_box_burst_layout.addWidget(time_unit, 0, 4)
        group_box_burst_layout.addWidget(min_interval_label, 1, 0)
        group_box_burst_layout.addWidget(min_interval, 1, 1)
        group_box_burst_layout.addWidget(min_duration_label, 1, 2)
        group_box_burst_layout.addWidget(min_duration, 1, 3)
        group_box_burst_layout.addWidget(min_number_label, 1, 4)
        group_box_burst_layout.addWidget(min_number, 1, 5)
        group_box_burst.setLayout(group_box_burst_layout)
        return group_box_burst, max_start, max_end, min_interval, min_duration, min_number

    def create_group_bins(self):
        group_box_bin = QtWidgets.QGroupBox("Select Bin (s)")
        group_box_bin_layout = QtWidgets.QHBoxLayout()
        group_box_bin.setCheckable(True)
        group_box_bin.setChecked(False)

        bin_time = QtWidgets.QLineEdit(self)
        bin_time.setStatusTip("Select Bin time")
        bin_time_label = QtWidgets.QLabel(self)
        bin_time_label.setText("Bin time")

        time_unit_label = QtWidgets.QLabel(self)
        time_unit_label.setText("s")

        group_box_bin_layout.addWidget(bin_time_label)
        group_box_bin_layout.addStretch(1)
        group_box_bin_layout.addWidget(bin_time)
        group_box_bin_layout.addWidget(time_unit_label)
        group_box_bin.setLayout(group_box_bin_layout)
        return group_box_bin, bin_time

    def create_group_threshold(self):
        group_box_threshold = QtWidgets.QGroupBox("Select Threshold (V)")
        group_box_threshold_layout = QtWidgets.QHBoxLayout()
        group_box_threshold.setCheckable(True)
        group_box_threshold.setChecked(False)

        threshold_from = QtWidgets.QLineEdit(self)
        threshold_from.setStatusTip("Choose threshold_from number, leave empty for one threshold_from")
        threshold_from_label = QtWidgets.QLabel(self)
        threshold_from_label.setText("Threshold  between:")

        threshold_to = QtWidgets.QLineEdit(self)
        threshold_to.setStatusTip("Choose threshold_to number, leave empty for all threshold_tos")
        threshold_to_label = QtWidgets.QLabel(self)
        threshold_to_label.setText("and")

        group_box_threshold_layout.addWidget(threshold_from_label)
        group_box_threshold_layout.addWidget(threshold_from)
        group_box_threshold_layout.addWidget(threshold_to_label)
        group_box_threshold_layout.addWidget(threshold_to)
        group_box_threshold.setLayout(group_box_threshold_layout)
        return group_box_threshold, threshold_from, threshold_to

    def create_tab1(self):
        tab1_layout = QtWidgets.QGridLayout()
        self.statusBar()

        self.group_box_channel_stream_tab1, self.channel_id_tab1 = self.create_group_select_id()
        self.group_box_browse_tab1, self.browse_text_box_tab1 = self.create_group_open_from()
        self.group_box_from_to_tab1, self.extract_from_tab1, self.extract_to_tab1 = self.create_group_select_time_range_tab1()
        self.group_box_from_to_tab1.toggled.connect(lambda : self.clear_qlines(self.extract_from_tab1, self.extract_to_tab1))

        self.plot_file_btn_tab1 = QtWidgets.QPushButton(self)
        self.plot_file_btn_tab1.setText("Plot Waveform")
        self.plot_file_btn_tab1.clicked.connect(self.plot_waveform)

        self.group_box_filter_tab1, self.filter_low_tab1, self.filter_high_tab1 = self.create_group_filter()
        self.group_box_filter_tab1.toggled.connect(lambda : self.clear_qlines(self.filter_low_tab1,self.filter_high_tab1))

        self.group_box_extract_tab1, self.extract_text_box_tab1, self.extract_btn_tab1 = self.create_group_extract()
        self.extract_btn_tab1.clicked.connect(self.save_waveform)

        self.group_box_algo, self.algo_speed = self.create_choose_algo_group_box()
        self.algo_speed.addItems(["Slow", "Fast"])

        self.group_box_reduced_by, self.reduced_by = self.create_reduced_by_group_box()
        self.group_box_reduced_by.toggled.connect(lambda : self.clear_qlines(self.reduced_by))
        self.reduced_by.textChanged.connect(lambda x: self.update_reduced_by(x))

        plots_names = ["", ""]
        self.tab1_is_plot_visible = [2]*len(plots_names)
        self.plot_group_box_tab1, self.tab1_canvas, *_ = self.create_plot_grop_box("Waveform", False, plots_names, add_lpot_check_boxes=False)
        self.tab1_plot_check_boxes = [True, False]

        tab1_layout.addWidget(self.group_box_browse_tab1, 0, 0)
        tab1_layout.addWidget(self.group_box_channel_stream_tab1, 1, 0)
        tab1_layout.addWidget(self.group_box_from_to_tab1, 2, 0)
        tab1_layout.addWidget(self.group_box_filter_tab1, 3, 0)
        tab1_layout.addWidget(self.group_box_algo, 4, 0)
        tab1_layout.addWidget(self.group_box_reduced_by, 5, 0)
        tab1_layout.addWidget(self.plot_file_btn_tab1, 6, 0)
        tab1_layout.setRowStretch(7, 0)
        tab1_layout.addWidget(self.group_box_extract_tab1, 8, 0)
        tab1_layout.addWidget(self.plot_group_box_tab1, 0, 2, 9, 1)
        self.tab1.setLayout(tab1_layout)

    def create_group_open_from(self):
        group_box_browse = QtWidgets.QGroupBox("Open from")
        group_box_browse_layout = QtWidgets.QHBoxLayout()

        browse_text_box = QtWidgets.QLineEdit(self)
        browse_text_box.setDisabled(True)
        browse = QtWidgets.QPushButton(self)
        browse.setText("Browse file")
        browse.clicked.connect(lambda x: self.get_file_for_open(browse_text_box))

        group_box_browse_layout.addWidget(browse_text_box)
        group_box_browse_layout.addWidget(browse)
        group_box_browse.setLayout(group_box_browse_layout)
        group_box_browse.setStatusTip("Choose hf5 format file to open")
        return group_box_browse, browse_text_box

    def create_group_select_time_range_tab1(self):
        group_box_from_to = QtWidgets.QGroupBox("Select time range (s)")
        group_box_from_to_layout = QtWidgets.QHBoxLayout()
        group_box_from_to.setCheckable(True)
        group_box_from_to.setChecked(False)

        extract_from = QtWidgets.QLineEdit(self)
        extract_from_label = QtWidgets.QLabel(self)
        extract_from_label.setText("Start time")

        extract_to = QtWidgets.QLineEdit(self)
        extract_to_label = QtWidgets.QLabel(self)
        extract_to_label.setText("End time")

        group_box_from_to_layout.addWidget(extract_from_label)
        group_box_from_to_layout.addWidget(extract_from)
        group_box_from_to_layout.addWidget(extract_to_label)
        group_box_from_to_layout.addWidget(extract_to)
        group_box_from_to.setLayout(group_box_from_to_layout)
        group_box_from_to.setStatusTip("Choose particular time (second), leave empty for full time")
        return group_box_from_to, extract_from, extract_to

    def create_group_select_id(self, checkable_combo=False):
        group_box_channel_stream = QtWidgets.QGroupBox("Select id")
        group_box_channel_stream_layout = QtWidgets.QHBoxLayout()

        if checkable_combo:
            channel_id = CheckableComboBox()
        else:
            channel_id = QtWidgets.QComboBox(self)

        channel_id.setStatusTip("Choose particular channel, choose all to extract all Channels")
        channel_id_label = QtWidgets.QLabel(self)
        channel_id_label.setText("Channel_id")

        group_box_channel_stream_layout.addWidget(channel_id_label)
        group_box_channel_stream_layout.addWidget(channel_id)
        group_box_channel_stream_layout.addStretch(1)
        group_box_channel_stream.setLayout(group_box_channel_stream_layout)
        return group_box_channel_stream, channel_id

    def create_group_filter(self):
        group_box_filter = QtWidgets.QGroupBox("Set filter (Hz)")
        group_box_filter_layout = QtWidgets.QHBoxLayout()
        group_box_filter.setCheckable(True)

        filter_low = QtWidgets.QLineEdit(self)
        filter_low_label = QtWidgets.QLabel(self)
        filter_low_label.setText("Low pass")

        filter_high = QtWidgets.QLineEdit(self)
        filter_high_label = QtWidgets.QLabel(self)
        filter_high_label.setText("High pass")
        filter_high.setText("200")

        group_box_filter_layout.addWidget(filter_high_label)
        group_box_filter_layout.addWidget(filter_high)
        group_box_filter_layout.addWidget(filter_low_label)
        group_box_filter_layout.addWidget(filter_low)
        group_box_filter.setLayout(group_box_filter_layout)
        group_box_filter.setStatusTip("Choose filter (Hz), low high or band pass")
        return group_box_filter, filter_low, filter_high

    def create_group_extract(self, group_title="Save to", btn_title="Extract", status="Choose path to save csv file"):
        group_box_extract = QtWidgets.QGroupBox(group_title)
        group_box_extract_layout = QtWidgets.QHBoxLayout()

        extract_text_box = QtWidgets.QLineEdit(self)
        extract_text_box.setDisabled(True)
        extract = QtWidgets.QPushButton(self)
        extract.setText(btn_title)

        group_box_extract_layout.addWidget(extract_text_box)
        group_box_extract_layout.addWidget(extract)
        group_box_extract.setLayout(group_box_extract_layout)
        group_box_extract.setStatusTip(status)
        return group_box_extract, extract_text_box, extract

    def create_plot_grop_box(self, title, add_component, plots_names, add_lpot_check_boxes=True):
        plot_group_box = QtWidgets.QGroupBox(title)
        plot_group_box.setStyleSheet('QGroupBox:title {'
                                    'subcontrol-origin: margin;'
                                    'subcontrol-position: top center;'
                                    'padding: 5px 8000px;'
                                    'background-color: #FF17365D;'
                                    'color: rgb(255, 255, 255);}'
                                    'QGroupBox {'
                                    'border: 1px solid gray;'
                                    'border-color: #FF17365D;'
                                    'margin-top: 27px;'
                                    'font-size: 20px;}')

        figure, _ = plt.subplots(nrows=len(plots_names), ncols=1)
        figure.tight_layout()
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)

        if add_component:
            component = QtWidgets.QLineEdit(self)
            component_label = QtWidgets.QLabel(self)
            component_label.setText("Component number: ")

            toolbar.addWidget(component_label)
            toolbar.addWidget(component)
            toolbar.addSeparator()
        else:
            component = 0 # bugi iyo da magitom

        check_boxes = []
        if add_lpot_check_boxes:
            for plot_name in plots_names:
                check_box = QtWidgets.QCheckBox(plot_name)
                check_box.setChecked(True)
                toolbar.addWidget(check_box)
                check_boxes.append(check_box)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        plot_group_box.setLayout(layout)
        return plot_group_box, canvas, check_boxes, component

    def create_choose_algo_group_box(self):
        group_box_algo = QtWidgets.QGroupBox("Choose algorithm type")
        group_box_algo_layout = QtWidgets.QHBoxLayout()

        algo_type = QtWidgets.QComboBox(self)

        algo_type.setStatusTip("Choose algorithm speed. note that fast one may lose some spikes")
        channel_id_label = QtWidgets.QLabel(self)
        channel_id_label.setText("Algorithm speed")

        group_box_algo_layout.addWidget(channel_id_label)
        group_box_algo_layout.addWidget(algo_type)
        group_box_algo_layout.addStretch(1)
        group_box_algo.setLayout(group_box_algo_layout)
        return group_box_algo, algo_type

    def create_reduced_by_group_box(self):
        group_box_reduce = QtWidgets.QGroupBox("Reduce signal")
        group_box_reduce_layout = QtWidgets.QHBoxLayout()
        group_box_reduce.setCheckable(True)
        group_box_reduce.setChecked(False)

        reduced_by = QtWidgets.QLineEdit(self)
        reduced_by_label = QtWidgets.QLabel(self)
        reduced_by_label.setText("Low pass")

        reduced_by.setStatusTip("Choose number to reduced by signal")
        channel_id_label = QtWidgets.QLabel(self)
        channel_id_label.setText("Signal reduced by")

        group_box_reduce_layout.addWidget(channel_id_label)
        group_box_reduce_layout.addStretch(1)
        group_box_reduce_layout.addWidget(reduced_by)
        group_box_reduce.setLayout(group_box_reduce_layout)
        return group_box_reduce, reduced_by

    def plot_waveform(self):
        self.statusBar.showMessage("Loading ........")
        channel_id = self._check_value(self.channel_id_tab1.currentText(), -1)
        from_in_s = self.round_to_closest(self._check_value(self.extract_from_tab1.text(), 0), 40/1000000)
        to_in_s = self.round_to_closest(self._check_value(self.extract_to_tab1.text(), None), 40/1000000)
        high_pass = self._check_value(self.filter_high_tab1.text(), None)
        low_pass = self._check_value(self.filter_low_tab1.text(), None)

        if -1 in (channel_id, from_in_s, to_in_s, high_pass, low_pass):
            self.error_popup("Please enter correct values", "Value Error")
            return

        if self.check_parameters(from_in_s, to_in_s, high_pass, low_pass):
            return

        waveform_error, waveform_error_msg = plot_tab1(self.file.recordings[0].analog_streams[0], channel_id, from_in_s, to_in_s, self.tab1_canvas, high_pass, low_pass, self.tab1_plot_check_boxes)

        if waveform_error:
            self.error_popup(waveform_error_msg, "Plot Error")
        self.statusBar.showMessage("")

    def plot_spike(self):
        self.statusBar.showMessage("Loading ........")
        channel_id =  self.get_value(self.channel_id_tab2)
        pre = self._check_value(self.extract_pre_tab2.text(), -1)
        post = self._check_value(self.extract_post_tab2.text(), -1)
        dead_time = self._check_value(self.dead_time_tab2.text(), -1)
        comp_number = self._check_value(self.component.text(), 1)
        spike_number = None # because we want to plot all spikes
        from_in_s = self.round_to_closest(self._check_value(self.extract_from_tab2.text(), 0), 40/1000000)
        to_in_s = self.round_to_closest(self._check_value(self.extract_to_tab2.text(), None), 40/1000000)
        high_pass = self._check_value(self.filter_high_tab2.text(), None)
        low_pass = self._check_value(self.filter_low_tab2.text(), None)
        threshold_from = self._check_value(self.threshold_from_tab2.text(), None)
        threshold_to = self._check_value(self.threshold_to_tab2.text(), None)
        max_start = self._check_value(self.tab2_max_start.text(), None)
        max_end = self._check_value(self.tab2_max_end.text(), None)
        min_between = self._check_value(self.tab2_min_interval.text(), None)
        min_duration = self._check_value(self.tab2_min_duration.text(), None)
        min_number_spike = self._check_value(self.tab2_min_number.text(), None)
        bin_width = self._check_value(self.tab2_bin.text(), None)
        reduce_num = self._check_value(self.reduced_by.text(), None)
        detecting_type = self.algo_speed.currentText()

        if "all" in channel_id:
            self.error_popup("Channel Id must not contain 'all'", "Value Error")
            return

        if -1 in (pre, post, dead_time, comp_number, from_in_s, to_in_s, high_pass, low_pass,
                    threshold_from, threshold_to, max_start, max_end, min_between, min_duration, min_number_spike):
            self.error_popup("Please enter correct values", "Value Error")
            return

        if not (all (x and x>0 for x in [pre,post,dead_time])):
            self.error_popup("'Select time parameters' is incorrect", "Parameter Error")
            return

        if dead_time < (pre+post):
            self.error_popup("Dead time must be more or equal than (pre + post)", "Intersection Error")
            return

        if any (x and x<0 for x in [max_start, max_end, min_between, min_duration, min_number_spike]):
            self.error_popup("Burst parameters must be positive", "Value Error")
            return

        if self.check_parameters(from_in_s, to_in_s, high_pass, low_pass):
            return

        spike_error, spike_error_msg = plot_tab2(self.file.recordings[0].analog_streams[0], channel_id, from_in_s, to_in_s, high_pass, low_pass, threshold_from, threshold_to, dead_time, self.tab2_plot_check_boxes,
                                            pre, post, self.tab2_canvas, comp_number, spike_number, self.tab3_stimulus, max_start, max_end, min_between, min_duration, min_number_spike, bin_width, reduce_num, detecting_type)

        if spike_error:
            self.error_popup(spike_error_msg, "Plot Error")
        self.statusBar.showMessage("")

    def plot_stimulus(self):
        self.statusBar.showMessage("Loading ........")
        channel_id = self._check_value(self.channel_id_tab3.currentText(), -1)
        pre = self._check_value(self.extract_pre_tab3.text(), -1)
        post = self._check_value(self.extract_post_tab3.text(), -1)
        dead_time = self._check_value(self.dead_time_tab3.text(), -1)
        from_in_s = self.round_to_closest(self._check_value(self.extract_from_tab3.text(), 0), 40/1000000)
        to_in_s = self.round_to_closest(self._check_value(self.extract_to_tab3.text(), None), 40/1000000)
        threshold_from = self._check_value(self.threshold_from_tab3.text(), -0.0003)
        threshold_to = self._check_value(self.threshold_to_tab3.text(), None)
        high_pass = self._check_value(self.filter_high_tab3.text(), None)
        low_pass = self._check_value(self.filter_low_tab3.text(), None)
        reduce_num = self._check_value(self.reduced_by.text(), None) 

        if -1 in (channel_id, pre, post, dead_time, from_in_s, to_in_s, threshold_from, threshold_to, high_pass, low_pass):
            self.error_popup("Please enter correct values", "Value Error")
            return

        if not (all (x and x>0 for x in [pre,post,dead_time])):
            self.error_popup("'Select time parameters' is incorrect", "Parameter Error")
            return

        if dead_time < (pre+post):
            self.error_popup("Dead time must be more or equal than (pre + post)", "Intersection Error")
            return

        if self.check_parameters(from_in_s, to_in_s, high_pass, low_pass):
            return

        error, error_msg = plot_tab3(self.file.recordings[0].analog_streams[0], channel_id, from_in_s, to_in_s, high_pass, low_pass, threshold_from, threshold_to,
                                    dead_time, self.tab3_plot_check_boxes, pre, post, self.tab3_canvas, reduce_num)
        if error:
            self.error_popup(error_msg, "Plot Error")
        else:
            self.tab3_stimulus = error_msg
        self.statusBar.showMessage("")

    def save_waveform(self):
        self.statusBar.showMessage("Loading ........")
        channel_id = self._check_value(self.channel_id_tab1.currentText(), None)
        from_in_s = self.round_to_closest(self._check_value(self.extract_from_tab1.text(),0), 40/1000000)
        to_in_s = self.round_to_closest(self._check_value(self.extract_to_tab1.text(),None), 40/1000000)
        high_pass = self._check_value(self.filter_high_tab1.text(), None)
        low_pass = self._check_value(self.filter_low_tab1.text(), None)
        reduce_num = self._check_value(self.reduced_by.text(), None) 

        if -1 in (channel_id, from_in_s, to_in_s, high_pass, low_pass):
            self.error_popup("Please enter correct values", "Value Error")
            return

        if self.check_parameters(from_in_s, to_in_s, high_pass, low_pass):
            return

        file_save_path = self.get_file_for_save(self.extract_text_box_tab1)
        if not file_save_path:
            return

        extract_waveform(self.file.recordings[0].analog_streams[0], file_save_path, channel_id, from_in_s, to_in_s, high_pass, low_pass, reduce_num)
        self.statusBar.showMessage("")
        self.info_popup("Data Created Succesfully", "Data saved")

    def save_spike(self):
        self.statusBar.showMessage("Loading ........")
        channel_id =  self.get_value(self.channel_id_tab2)
        from_in_s = self.round_to_closest(self._check_value(self.extract_from_tab2.text(), 0), 40/1000000)
        to_in_s = self.round_to_closest(self._check_value(self.extract_to_tab2.text(), None), 40/1000000)
        threshold_from = self._check_value(self.threshold_from_tab2.text(), None)
        threshold_to = self._check_value(self.threshold_to_tab2.text(), None)
        high_pass = self._check_value(self.filter_high_tab2.text(), None)
        low_pass = self._check_value(self.filter_low_tab2.text(), None)
        dead_time = self._check_value(self.dead_time_tab2.text(), -1)
        bin_width = self._check_value(self.tab2_bin.text(), None)
        max_start = self._check_value(self.tab2_max_start.text(), None)
        max_end = self._check_value(self.tab2_max_end.text(), None)
        min_between = self._check_value(self.tab2_min_interval.text(), None)
        min_duration = self._check_value(self.tab2_min_duration.text(), None)
        min_number_spike = self._check_value(self.tab2_min_number.text(), None)
        pre = self._check_value(self.extract_pre_tab2.text(), -1)
        post = self._check_value(self.extract_post_tab2.text(), -1)
        comp_number = self._check_value(self.component.text(), 1)
        reduce_num = self._check_value(self.reduced_by.text(), None) 

        if ("all" in channel_id) and (len(channel_id)>1):
            self.error_popup("Channel Id must not contain 'all'", "Value Error")
            return

        if -1 in (channel_id, from_in_s, to_in_s, threshold_from, threshold_to, high_pass, low_pass,
                    dead_time, bin_width, max_start, max_end, min_between, min_duration, min_number_spike, pre, post, comp_number):
            self.error_popup("Please enter correct values", "Value Error")
            return

        if not (all (x and x>0 for x in [pre,post,dead_time])):
            self.error_popup("'Select time parameters' is incorrect", "Parameter Error")
            return

        if dead_time < (pre+post):
            self.error_popup("Dead time must be more or equal than (pre + post)", "Intersection Error")
            return

        if any (x and x<0 for x in [max_start, max_end, min_between, min_duration, min_number_spike]):
            self.error_popup("Burst parameters must be positive", "Value Error")
            return

        if self.check_parameters(from_in_s, to_in_s, high_pass, low_pass):
            return

        file_save_path = self.get_file_for_save(self.extract_text_box_tab2)
        if not file_save_path:
            return

        extract_spike(self.browse_text_box_tab1.text(), self.file.recordings[0].analog_streams[0], file_save_path, channel_id, from_in_s, to_in_s, threshold_from, threshold_to, high_pass, low_pass, dead_time, bin_width,
                                            max_start, max_end, min_between, min_duration, min_number_spike, self.tab3_stimulus, pre, post, comp_number, reduce_num)
        self.statusBar.showMessage("")
        self.info_popup("Data Created Succesfully", "Data saved")

    def save_stimulus(self):
        self.statusBar.showMessage("Loading ........")
        channel_id = self._check_value(self.channel_id_tab3.currentText(), None)
        from_in_s = self.round_to_closest(self._check_value(self.extract_from_tab3.text(), 0), 40/1000000)
        to_in_s = self.round_to_closest(self._check_value(self.extract_to_tab3.text(), None), 40/1000000)
        threshold_from = self._check_value(self.threshold_from_tab3.text(), -0.0003)
        dead_time = self._check_value(self.dead_time_tab3.text(), -1)
        pre = self._check_value(self.extract_pre_tab3.text(), -1)
        post = self._check_value(self.extract_post_tab3.text(), -1)
        high_pass = self._check_value(self.filter_high_tab3.text(), None)
        low_pass = self._check_value(self.filter_low_tab3.text(), None)
        reduce_num = self._check_value(self.reduced_by.text(), None) 

        if -1 in (channel_id, from_in_s, to_in_s, threshold_from, dead_time, pre, post, high_pass, low_pass):
            self.error_popup("Please enter correct values", "Value Error")
            return

        if not(all (x and x>0 for x in [pre,post,dead_time])):
            self.error_popup("'Select time parameters' is incorrect", "Parameter Error")
            return

        if dead_time < (pre+post):
            self.error_popup("Dead time must be more or equal than (pre + post)", "Intersection Error")
            return

        if self.check_parameters(from_in_s, to_in_s, high_pass, low_pass):
            return

        file_save_path = self.get_file_for_save(self.extract_text_box_tab3)
        if not file_save_path:
            return

        extract_stimulus(self.file.recordings[0].analog_streams[0], file_save_path, channel_id, from_in_s, to_in_s, threshold_from, dead_time, pre, post, high_pass, low_pass, reduce_num)
        self.statusBar.showMessage("")
        self.info_popup("Data Created Succesfully", "Data saved")


    def update_reduced_by(self, reduced_by):
        self.tab1_plot_check_boxes[-1] = reduced_by

    def round_to_closest(self, value, time_stamp):
        if value and value>0:
            remainder = value % time_stamp
            if remainder > time_stamp / 2:
                value += time_stamp - remainder
            else:
                value -= remainder
        return value

    def check_parameters(self, from_in_s, to_in_s, high_pass, low_pass):
        if ((from_in_s is not None) and (to_in_s is not None)) and (from_in_s >= to_in_s):
            self.error_popup("'End time' must be greater than 'Start time'", "Value Error")
            return True

        if (high_pass is not None and low_pass is not None) and (high_pass<0 or low_pass<0 or low_pass<high_pass):
            self.error_popup("Incorrect Filter", "Value Error")
            return True
        elif (high_pass is None) and (low_pass is not None) and (low_pass<0):
            self.error_popup("Incorrect Filter", "Value Error")
            return True
        elif (low_pass is None) and (high_pass is not None) and (high_pass<0):
            self.error_popup("Incorrect Filter", "Value Error")
            return True

        return False

    def path_valid(self, fileName):
            try:
                _file = McsData.RawData(fileName)
            except:
                _file = 0
            return _file

    def combine_spikes(self, num_col=8):
        dir_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")

        if dir_name:
            if os.path.exists(os.path.join(dir_name, "combined.csv")):
                os.remove(os.path.join(dir_name, "combined.csv"))
            files = os.listdir(dir_name)
            if not len(files):
                return

            combined = None
            combined_columns = ["time", "signal", "spike", "burst", "stimulus", "channel", "stimulus_type", "file_name"]
            for file in files:
                temp_df = pd.read_csv(os.path.join(dir_name,file))
                if len(temp_df.columns) > num_col:
                    self.info_popup(f"some files columns quantity did not match so we combined only last {num_col} columns", "Columns length")
                temp_df = temp_df[temp_df.columns[-num_col:]]
                if combined is None:
                    combined = temp_df
                else:
                    combined = pd.DataFrame(np.concatenate([combined.values, temp_df.values]), columns = combined_columns)

            combined.to_csv(os.path.join(dir_name, "combined.csv"), index = False)
            self.info_popup("Data Created Succesfully", "Data saved")

    def get_file_for_open(self, text_box):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        if fileName:
            text_box.setText(fileName)

            self.file = self.path_valid(fileName)

            if not self.file:
                self.error_popup("File path is incorrect", "File Error")
                return

            message = [str(value.info['Label']) for key, value in self.file.recordings[0].analog_streams[0].channel_infos.items()]
            message.insert(0,"all")

            for channel_id in [self.channel_id_tab1, self.channel_id_tab2, self.channel_id_tab3]:
                channel_id.clear()
                channel_id.addItems(message)

            for i in range(self.channel_id_tab2.count()):
                self.channel_id_tab2.setItemChecked(i, False)
            self.channel_id_tab2.setItemChecked(1, True)
            self.channel_id_tab2.setCurrentIndex(1)

    def get_file_for_save(self, text_box):
        name, _ = QtWidgets.QFileDialog.getSaveFileName(self,'Save File', options=QtWidgets.QFileDialog.DontUseNativeDialog)
        if name:
            text_box.setText(name)
            file_save_path = text_box.text()
            return file_save_path

    def check_plotes_visibility(self, tab_is_plot_visible, tab_canvas, plot_idx, value):
        axes = tab_canvas.figure.get_axes()
        tab_is_plot_visible[plot_idx] = value
        axes[plot_idx].set_visible(value)

        num_visible_plots = tab_is_plot_visible.count(2)
        visible_plots = 0
        for idx, visible in enumerate(tab_is_plot_visible):
            if not visible:
                axes[idx].set_visible(False)
            else:
                axes[idx].change_geometry(num_visible_plots,1,visible_plots+1)
                visible_plots += 1

        tab_canvas.figure.tight_layout()
        tab_canvas.draw()

    def on_press(self, event, figure_canvas, is_canvas_clicked, canvas_number):
        if not event.dblclick:
            return

        if is_canvas_clicked[0]:
            for key, value in figure_canvas.items():
                if ("canvas" in key):
                    value.setVisible(True)
            is_canvas_clicked[0] = False
        else:
            for key, value in figure_canvas.items():
                if ("canvas" in key) and (key != "canvas"+str(canvas_number)):
                    value.setVisible(False)
            is_canvas_clicked[0] = True

    def _check_value(self, value, res):
        if value == "" or value == "all":
            return res
        try:
            return float(value)
        except ValueError:
            return -1

    def error_popup(self, txt, title_text):
        QtWidgets.QMessageBox.critical(self, title_text, txt)

    def info_popup(self, txt, title_text):
        QtWidgets.QMessageBox.information(self, title_text, txt)

    def clear_qlines(self, *args):
        for item in args:
            item.setText("")

    def get_value(self, combo):
        checked_channel = []
        for i in range(combo.count()):
            if  combo.itemChecked(i):
                checked_channel.append(combo.itemText(i))
        return checked_channel

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MEA_app()
    win.show()
    sys.exit(app.exec_())