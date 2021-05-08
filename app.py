import sys
import os
from PyQt5 import QtWidgets,QtCore, QtGui
from timeStamp_info import *
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd
from functools import partial

style.use('fivethirtyeight')
matplotlib.use('Qt5Agg')
font = {'family' : 'Arial',
        'weight' : 'bold',
        'size'   : 8}
matplotlib.rc('font', **font)


GROUP_BOX_HEIGHT = 58
GROUP_BOX_WIDTH = 250

class MEA_app(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        
        self.tabs.addTab(self.tab1,"Waveform")
        self.tabs.addTab(self.tab2,"Spike")
        self.tabs.addTab(self.tab3,"Stimulus")
        
        self.create_tab1()
        self.create_tab2()
        self.create_tab3()

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))  

        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.dir_path,"images","app_icon.png")))
        # როცა აპლიკაციის სახეს მივცემთ ეს 3 ხაზი წესით აღარ დაჭირდება რომ ტასკბარზე აიქონ გამოჩნდეს
        import ctypes
        myappid = 'mycompany.myproduct.subproduct.version'                      
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        File = open(os.path.join(self.dir_path,"styles/main_style.qss"),"r")
        with File:
            qss = File.read()
            self.setStyleSheet(qss)
 
        desktop = QtWidgets.QApplication.desktop()
        screenRect = desktop.screenGeometry()
        height = screenRect.height()
        width = screenRect.width()
        self.setGeometry(0,30,width,height-30)
        self.setWindowTitle("MEA System Analyzer")
        self.setCentralWidget(self.tabs)
        self.showMaximized()
        
    def create_tab3(self):
        tab3_layout = QtWidgets.QGridLayout()
        self.statusBar()

        group_box_channel_stream, self.channel_id_tab3 = self.create_group_select_id()
        group_box_pre_post, self.extract_pre_tab3, self.extract_post_tab3, self.dead_time_tab3 = self.create_group_select_time_range_tab2()
        self.extract_pre_tab3.setText("0.001")
        self.extract_post_tab3.setText("0.001")
        self.dead_time_tab3.setText("0.02")
        self.extract_pre_tab3.setStatusTip("Recommended: 0.001 (s)")
        self.extract_post_tab3.setStatusTip("Recommended: 0.001 (s)")
        self.dead_time_tab3.setStatusTip("Recommended: 0.02 (s)")

        group_box_threshold_tab3, self.threshold_from_tab3, self.threshold_to_tab3 = self.create_group_threshold()
        self.threshold_from_tab3.setStatusTip("Default: -0.0003 (V)")
        group_box_threshold_tab3.toggled.connect(lambda : self.clear_qlines(self.threshold_from_tab3, self.threshold_to_tab3))
        self.threshold_to_tab3.setDisabled(True)

        # group_box_filter, self.filter_low_tab3, self.filter_high_tab3 = self.create_group_filter() 
        # group_box_filter.toggled.connect(lambda : self.clear_qlines(self.filter_low_tab3, self.filter_high_tab3))
        
        group_box_from_to, self.extract_from_tab3, self.extract_to_tab3 = self.create_group_select_time_range_tab1()
        group_box_from_to.toggled.connect(lambda : self.clear_qlines(self.extract_from_tab3, self.extract_to_tab3))

        group_box_extract, self.extract_text_box_tab3, self.extract_btn_tab3 = self.create_group_extract()   
        self.extract_btn_tab3.clicked.connect(self.save_stimulus)

        plot_file_btn = QtWidgets.QPushButton(self)
        plot_file_btn.setFixedSize(GROUP_BOX_WIDTH,35)
        plot_file_btn.setText("Plot Stimulus")
        plot_file_btn.clicked.connect(self.plot_stimulus)  

        plots_names = ["Average Stimulus","Stimulus", "Frequency"]
        self.tab3_is_plot_visible = [2]*len(plots_names)
        plot_group_box, self.tab3_canvas, self.tab3_plot_check_boxes  = self.create_plot_grop_box("Stimulus", False, plots_names)
        for i in range(len(self.tab3_plot_check_boxes)):
            self.tab3_plot_check_boxes[i].stateChanged.connect(partial(self.check_plotes_visibility, self.tab3_is_plot_visible, self.tab3_canvas, i)) 

        tab3_layout.addWidget(group_box_channel_stream,0,0)
        tab3_layout.addWidget(group_box_pre_post,1,0)
        tab3_layout.addWidget(group_box_from_to,2,0)
        tab3_layout.addWidget(group_box_threshold_tab3,3,0)
        # tab3_layout.addWidget(group_box_filter,5,0)
        tab3_layout.addWidget(plot_file_btn,4,0)
        tab3_layout.setRowStretch(5,0)
        tab3_layout.addWidget(group_box_extract,6,0)
        tab3_layout.addWidget(plot_group_box,0,2,7,1)
        self.tab3.setLayout(tab3_layout)

    def create_tab2(self):
        tab2_layout = QtWidgets.QGridLayout()
        self.statusBar()

        group_box_channel_stream, self.channel_id_tab2 = self.create_group_select_id()
        group_box_pre_post, self.extract_pre_tab2, self.extract_post_tab2, self.dead_time_tab2 = self.create_group_select_time_range_tab2()
        self.extract_pre_tab2.setText("0.001")
        self.extract_post_tab2.setText("0.001")
        self.dead_time_tab2.setText("0.003")
        self.extract_pre_tab2.setStatusTip("Recommended: 0.001 (s)")
        self.extract_post_tab2.setStatusTip("Recommended: 0.001 (s)")
        self.dead_time_tab2.setStatusTip("Recommended: 0.003 (s)")

        group_box_threshold_tab2, self.threshold_from_tab2, self.threshold_to_tab2 = self.create_group_threshold()
        group_box_threshold_tab2.setStatusTip("Select Threshold. Default: -0.00012 (V)")
        self.threshold_from_tab2.setStatusTip("Default: calculate std deviation. (V)")
        group_box_threshold_tab2.toggled.connect(lambda : self.clear_qlines(self.threshold_from_tab2, self.threshold_to_tab2))
        
        group_box_filter, self.filter_low_tab2, self.filter_high_tab2 = self.create_group_filter() 
        group_box_filter.toggled.connect(lambda : self.clear_qlines(self.filter_low_tab2, self.filter_high_tab2))
        
        group_box_from_to, self.extract_from_tab2, self.extract_to_tab2 = self.create_group_select_time_range_tab1()
        group_box_from_to.toggled.connect(lambda : self.clear_qlines(self.extract_from_tab2, self.extract_to_tab2))

        group_box_burst, self.tab2_max_start, self.tab2_max_end, self.tab2_min_interval, self.tab2_min_duration, self.tab2_min_number = self.create_group_burst()
        self.tab2_max_start.setStatusTip("Recommended: 0.01 (s)")
        self.tab2_max_end.setStatusTip("Recommended: 0.01 (s)")
        self.tab2_min_interval.setStatusTip("Recommended: 0.01 (s)")
        self.tab2_min_duration.setStatusTip("Recommended: 0.02 (s)")
        self.tab2_min_number.setStatusTip("Recommended: 4")
        group_box_burst.toggled.connect(lambda : self.clear_qlines(self.tab2_max_start, self.tab2_max_end, self.tab2_min_interval, 
                                                                    self.tab2_min_duration, self.tab2_min_number))

        group_box_bin, self.tab2_bin = self.create_group_bins()
        self.tab2_bin.setStatusTip("Recommended: 10 (s)")
        group_box_bin.toggled.connect(lambda : self.clear_qlines(self.tab2_bin))

        group_box_extract, self.extract_text_box_tab2, self.extract_btn_tab2 = self.create_group_extract() 
        self.extract_btn_tab2.clicked.connect(self.save_spike)

        plot_file_btn = QtWidgets.QPushButton(self)
        plot_file_btn.setFixedSize(GROUP_BOX_WIDTH,35)
        plot_file_btn.setText("Plot Spike")
        plot_file_btn.clicked.connect(self.plot_spike)  
        
        plots_names = ["Spike together","Spikes","Frequency"]
        self.tab2_is_plot_visible = [2]*len(plots_names)
        plot_group_box, self.tab2_canvas, self.tab2_plot_check_boxes  = self.create_plot_grop_box("Spike", True, plots_names)
        self.tab2_is_canvas_clicked = [False]
        for i in range(len(self.tab2_plot_check_boxes)):
            self.tab2_plot_check_boxes[i].stateChanged.connect(partial(self.check_plotes_visibility, self.tab2_is_plot_visible, self.tab2_canvas, i))

        tab2_layout.addWidget(group_box_channel_stream,0,0)
        tab2_layout.addWidget(group_box_pre_post,1,0)
        tab2_layout.addWidget(group_box_from_to,2,0)
        tab2_layout.addWidget(group_box_threshold_tab2,3,0)
        tab2_layout.addWidget(group_box_filter,4,0)
        tab2_layout.addWidget(plot_file_btn,5,0)
        tab2_layout.addWidget(group_box_burst,6,0)
        tab2_layout.addWidget(group_box_bin,7,0)
        tab2_layout.setRowStretch(8,0)
        tab2_layout.addWidget(group_box_extract,9,0)
        tab2_layout.addWidget(plot_group_box,0,2,10,1)
        self.tab2.setLayout(tab2_layout)

    def create_group_select_time_range_tab2(self):
        group_box_pre_post = QtWidgets.QGroupBox("Select time parameters")
        group_box_pre_post_layout = QtWidgets.QHBoxLayout()

        extract_pre_tab2 = QtWidgets.QLineEdit(self)
        extract_pre_tab2.setFixedWidth(35)
        extract_pre_label = QtWidgets.QLabel(self)
        extract_pre_label.setText("Pre")
        extract_pre_label.setFont(QtGui.QFont('Arial', 7))

        extract_post_tab2 = QtWidgets.QLineEdit(self)
        extract_post_tab2.setFixedWidth(35)
        extract_post_label = QtWidgets.QLabel(self)
        extract_post_label.setText("Post")
        extract_post_label.setFont(QtGui.QFont('Arial', 7))

        dead_time_tab2 = QtWidgets.QLineEdit(self)
        dead_time_tab2.setFixedWidth(35)
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
        group_box_pre_post.setFixedSize(GROUP_BOX_WIDTH,GROUP_BOX_HEIGHT)
        group_box_pre_post.setStatusTip("Choose particular time (second)")
        return group_box_pre_post, extract_pre_tab2, extract_post_tab2, dead_time_tab2 

    def create_group_burst(self):
        group_box_burst = QtWidgets.QGroupBox("Select Burst Parameters (ms)")
        group_box_burst_layout = QtWidgets.QGridLayout()
        group_box_burst.setCheckable(True)
        group_box_burst.setChecked(False)

        max_start = QtWidgets.QLineEdit(self)
        max_start.setFixedWidth(35)
        max_start.setStatusTip("Max. Interval to start burst (ms)")
        max_start_label = QtWidgets.QLabel(self)
        max_start_label.setText("Max: start")
        max_start_label.setFont(QtGui.QFont('Arial', 7))

        max_end = QtWidgets.QLineEdit(self)
        max_end.setFixedWidth(35)
        max_end.setStatusTip("Max. Interval ro end burst (ms)")
        max_end_label = QtWidgets.QLabel(self)
        max_end_label.setText("end")
        max_end_label.setFont(QtGui.QFont('Arial', 7))

        time_unit = QtWidgets.QLabel(self)
        time_unit.setText("ms")
        time_unit.setFont(QtGui.QFont('Arial', 7))

        min_interval = QtWidgets.QLineEdit(self)
        min_interval.setFixedWidth(35)
        min_interval.setStatusTip("Min. Interval between bursts (ms)")
        min_interval_label = QtWidgets.QLabel(self)
        min_interval_label.setText("Min: betw.")
        min_interval_label.setFont(QtGui.QFont('Arial', 7))

        min_duration = QtWidgets.QLineEdit(self)
        min_duration.setFixedWidth(35)
        min_duration.setStatusTip("Min. duration of bursts (ms)")
        min_duration_label = QtWidgets.QLabel(self)
        min_duration_label.setText("dur.")
        min_duration_label.setFont(QtGui.QFont('Arial', 7))
        
        min_number = QtWidgets.QLineEdit(self)
        min_number.setFixedWidth(35)
        min_number.setStatusTip("Min number of spikes")
        min_number_label = QtWidgets.QLabel(self)
        min_number_label.setText("numb.")
        min_number_label.setFont(QtGui.QFont('Arial', 7))

        group_box_burst_layout.addWidget(max_start_label,0,0)
        group_box_burst_layout.addWidget(max_start,0,1)
        group_box_burst_layout.addWidget(max_end_label,0,2)
        group_box_burst_layout.addWidget(max_end,0,3)
        group_box_burst_layout.addWidget(time_unit,0,4)
        group_box_burst_layout.addWidget(min_interval_label,1,0)
        group_box_burst_layout.addWidget(min_interval,1,1)
        group_box_burst_layout.addWidget(min_duration_label,1,2)
        group_box_burst_layout.addWidget(min_duration,1,3)
        group_box_burst_layout.addWidget(min_number_label,1,4)
        group_box_burst_layout.addWidget(min_number,1,5)
        group_box_burst.setLayout(group_box_burst_layout)
        group_box_burst.setFixedSize(GROUP_BOX_WIDTH,80)   
        return group_box_burst, max_start, max_end, min_interval, min_duration, min_number

    def create_group_bins(self):
        group_box_bin = QtWidgets.QGroupBox("Select Bin (s)")
        group_box_bin_layout = QtWidgets.QHBoxLayout()
        group_box_bin.setCheckable(True)
        group_box_bin.setChecked(False)

        bin_time = QtWidgets.QLineEdit(self)
        bin_time.setFixedWidth(35)
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
        group_box_bin.setFixedSize(GROUP_BOX_WIDTH,GROUP_BOX_HEIGHT)
        return group_box_bin, bin_time

    def create_group_threshold(self):
        group_box_threshold = QtWidgets.QGroupBox("Select Threshold (V)")
        group_box_threshold_layout = QtWidgets.QHBoxLayout()
        group_box_threshold.setCheckable(True)
        group_box_threshold.setChecked(False)

        threshold_from = QtWidgets.QLineEdit(self)
        threshold_from.setFixedWidth(40)
        threshold_from.setStatusTip("Choose threshold_from number, leave empty for one threshold_from")
        threshold_from_label = QtWidgets.QLabel(self)
        threshold_from_label.setText("Threshold  between:")

        threshold_to = QtWidgets.QLineEdit(self)
        threshold_to.setFixedWidth(40)
        threshold_to.setStatusTip("Choose threshold_to number, leave empty for all threshold_tos")
        threshold_to_label = QtWidgets.QLabel(self)
        threshold_to_label.setText("and")

        group_box_threshold_layout.addWidget(threshold_from_label)
        group_box_threshold_layout.addWidget(threshold_from)
        group_box_threshold_layout.addWidget(threshold_to_label)
        group_box_threshold_layout.addWidget(threshold_to)
        group_box_threshold.setLayout(group_box_threshold_layout)
        group_box_threshold.setFixedSize(GROUP_BOX_WIDTH,GROUP_BOX_HEIGHT)   
        return group_box_threshold, threshold_from, threshold_to

    def create_tab1(self):
        tab1_layout = QtWidgets.QGridLayout()
        self.statusBar()

        group_box_channel_stream, self.channel_id_tab1 = self.create_group_select_id()
        group_box_browse, self.browse_text_box_tab1 = self.create_group_open_from()
        group_box_from_to, self.extract_from_tab1, self.extract_to_tab1 = self.create_group_select_time_range_tab1()
        group_box_from_to.toggled.connect(lambda : self.clear_qlines(self.extract_from_tab1, self.extract_to_tab1))

        plot_file_btn = QtWidgets.QPushButton(self)
        plot_file_btn.setFixedSize(GROUP_BOX_WIDTH,35)
        plot_file_btn.setText("Plot Waveform")
        plot_file_btn.clicked.connect(self.plot_waveform)  

        space_between_plotbtn_extract = QtWidgets.QWidget()
        space_between_plotbtn_extract.setFixedSize(GROUP_BOX_WIDTH,50)  

        group_box_filter, self.filter_low_tab1, self.filter_high_tab1 = self.create_group_filter()  
        group_box_filter.toggled.connect(lambda : self.clear_qlines(self.filter_low_tab1,self.filter_high_tab1))

        group_box_extract, self.extract_text_box_tab1, self.extract_btn_tab1 = self.create_group_extract()
        self.extract_btn_tab1.clicked.connect(self.save_waveform)

        plots_names = ["Waveform","Frequeny"]
        self.tab1_is_plot_visible = [2]*len(plots_names)
        plot_group_box, self.tab1_canvas, self.tab1_plot_check_boxes  = self.create_plot_grop_box("Waveform", False, plots_names)
        self.tab1_is_canvas_clicked = [False]
        for i in range(len(self.tab1_plot_check_boxes)):
            self.tab1_plot_check_boxes[i].stateChanged.connect(partial(self.check_plotes_visibility, self.tab1_is_plot_visible, self.tab1_canvas, i))
        
        tab1_layout.addWidget(group_box_browse,0,0)
        tab1_layout.addWidget(group_box_channel_stream,1,0)
        tab1_layout.addWidget(group_box_from_to,2,0)
        tab1_layout.addWidget(group_box_filter,3,0)
        tab1_layout.addWidget(plot_file_btn,4,0)
        tab1_layout.setRowStretch(5,0)
        tab1_layout.addWidget(group_box_extract,6,0)
        tab1_layout.addWidget(plot_group_box,0,2,7,1)
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
        group_box_browse.setFixedSize(GROUP_BOX_WIDTH,GROUP_BOX_HEIGHT)
        group_box_browse.setStatusTip("Choose hf5 format file to open")
        return group_box_browse, browse_text_box
        
    def create_group_select_time_range_tab1(self):
        group_box_from_to = QtWidgets.QGroupBox("Select time range (s)")
        group_box_from_to_layout = QtWidgets.QHBoxLayout()
        group_box_from_to.setCheckable(True)
        group_box_from_to.setChecked(False)

        extract_from = QtWidgets.QLineEdit(self)
        extract_from.setFixedWidth(40)
        extract_from_label = QtWidgets.QLabel(self)
        extract_from_label.setText("Start time")
        
        extract_to = QtWidgets.QLineEdit(self)
        extract_to.setFixedWidth(40)
        extract_to_label = QtWidgets.QLabel(self)
        extract_to_label.setText("End time")
        
        group_box_from_to_layout.addWidget(extract_from_label)
        group_box_from_to_layout.addWidget(extract_from)
        group_box_from_to_layout.addWidget(extract_to_label)
        group_box_from_to_layout.addWidget(extract_to)
        group_box_from_to.setLayout(group_box_from_to_layout)
        group_box_from_to.setFixedSize(GROUP_BOX_WIDTH,GROUP_BOX_HEIGHT)
        group_box_from_to.setStatusTip("Choose particular time (second), leave empty for full time")
        return group_box_from_to, extract_from, extract_to

    def create_group_select_id(self):
        group_box_channel_stream = QtWidgets.QGroupBox("Select id")
        group_box_channel_stream_layout = QtWidgets.QHBoxLayout()
        
        channel_id = QtWidgets.QComboBox(self)
        channel_id.setFixedWidth(40)
        channel_id.setStatusTip("Choose particular channel, choose all to extract all Channels")
        channel_id_label = QtWidgets.QLabel(self)
        channel_id_label.setText("Channel_id")
        
        group_box_channel_stream_layout.addWidget(channel_id_label)
        group_box_channel_stream_layout.addWidget(channel_id)
        group_box_channel_stream_layout.addStretch(1)
        group_box_channel_stream.setLayout(group_box_channel_stream_layout)
        group_box_channel_stream.setFixedSize(GROUP_BOX_WIDTH,GROUP_BOX_HEIGHT)
        return group_box_channel_stream, channel_id

    def create_group_filter(self):
        group_box_filter = QtWidgets.QGroupBox("Set filter (Hz)")
        group_box_filter_layout = QtWidgets.QHBoxLayout()
        group_box_filter.setCheckable(True)
        group_box_filter.setChecked(False)
       
        filter_low = QtWidgets.QLineEdit(self)
        filter_low.setFixedWidth(40)
        filter_low_label = QtWidgets.QLabel(self)
        filter_low_label.setText("Low pass")
       
        filter_high = QtWidgets.QLineEdit(self)
        filter_high.setFixedWidth(40)
        filter_high_label = QtWidgets.QLabel(self)
        filter_high_label.setText("High pass")
        
        group_box_filter_layout.addWidget(filter_high_label)
        group_box_filter_layout.addWidget(filter_high)
        group_box_filter_layout.addWidget(filter_low_label)
        group_box_filter_layout.addWidget(filter_low)
        group_box_filter.setLayout(group_box_filter_layout)
        group_box_filter.setFixedSize(GROUP_BOX_WIDTH,GROUP_BOX_HEIGHT)
        group_box_filter.setStatusTip("Choose filter (Hz), low high or band pass")
        return group_box_filter, filter_low, filter_high
        
    def create_group_extract(self):
        group_box_extract = QtWidgets.QGroupBox("Save to")
        group_box_extract_layout = QtWidgets.QHBoxLayout()
        
        extract_text_box = QtWidgets.QLineEdit(self)
        extract_text_box.setDisabled(True)
        extract = QtWidgets.QPushButton(self)
        extract.setText("Extract")

        group_box_extract_layout.addWidget(extract_text_box)
        group_box_extract_layout.addWidget(extract)
        group_box_extract.setLayout(group_box_extract_layout)
        group_box_extract.setFixedSize(GROUP_BOX_WIDTH,GROUP_BOX_HEIGHT)
        group_box_extract.setStatusTip("Choose path to save csv file")
        return group_box_extract, extract_text_box, extract

    def create_plot_grop_box(self, title, add_component, plots_names):
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

        self.component = QtWidgets.QLineEdit(self)
        self.component.setFixedWidth(35)
        component_label = QtWidgets.QLabel(self)
        component_label.setText("Component number: ")

        figure, _ = plt.subplots(nrows=len(plots_names), ncols=1)
        figure.tight_layout()
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)
        
        # spacer = QtWidgets.QWidget(self)
        # spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        if add_component:
            toolbar.addWidget(component_label)
            toolbar.addWidget(self.component)
            toolbar.addSeparator()
            # toolbar.addWidget(spacer)
        
        check_boxes = []
        for plot_name in plots_names:
            check_box = QtWidgets.QCheckBox(plot_name)
            check_box.setChecked(True)
            toolbar.addWidget(check_box)
            check_boxes.append(check_box)
        # toolbar.addWidget(spacer)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        plot_group_box.setLayout(layout)
        return plot_group_box, canvas, check_boxes
  

    def plot_waveform(self):
        analog_stream_path = self.browse_text_box_tab1.text()
        channel_id = self._check_value(self.channel_id_tab1.currentText(), None)
        from_in_s = self._check_value(self.extract_from_tab1.text(), 0)
        to_in_s = self._check_value(self.extract_to_tab1.text(), None)
        high_pass = self._check_value(self.filter_high_tab1.text(), None)
        low_pass = self._check_value(self.filter_low_tab1.text(), None)
       
        if -1 in (channel_id,from_in_s,to_in_s,high_pass,low_pass):
            self.error_popup("Please enter correct values", "Value Error")
            return
        
        waveform_error, waveform_error_msg = plot_signal(analog_stream_path, channel_id, from_in_s, to_in_s,
                                                        self.tab1_canvas, 0, high_pass, low_pass)

        fourier_error, fourier_error_msg = plot_signal_frequencies(analog_stream_path, channel_id, self.tab1_canvas, 1, from_in_s, to_in_s)

        if waveform_error:
            self.error_popup(waveform_error_msg, "Plot Error")
        elif fourier_error:
            self.error_popup(fourier_error_msg, "Plot Error")
    
    def plot_spike(self):
        analog_stream_path = self.browse_text_box_tab1.text()
        channel_id = self._check_value(self.channel_id_tab2.currentText(), None)
        pre = self._check_value(self.extract_pre_tab2.text(), None)
        post = self._check_value(self.extract_post_tab2.text(), None)
        dead_time = self._check_value(self.dead_time_tab2.text(), None)
        comp_number = self._check_value(self.component.text(), 1)
        spike_number = None # because we want to plot all spikes
        from_in_s = self._check_value(self.extract_from_tab2.text(), 0)
        to_in_s = self._check_value(self.extract_to_tab2.text(), None)
        high_pass = self._check_value(self.filter_high_tab2.text(), None)
        low_pass = self._check_value(self.filter_low_tab2.text(), None)
        threshold_from = self._check_value(self.threshold_from_tab2.text(), None)
        threshold_to = self._check_value(self.threshold_to_tab2.text(), None)
        max_start = self._check_value(self.tab2_max_start.text(), None)
        max_end = self._check_value(self.tab2_max_end.text(), None)
        min_between = self._check_value(self.tab2_min_interval.text(), None)
        min_duration = self._check_value(self.tab2_min_duration.text(), None)
        min_number_spike = self._check_value(self.tab2_min_number.text(), None)
        
        if -1 in (channel_id,pre,post,dead_time,comp_number,from_in_s,to_in_s,high_pass,low_pass,
                    threshold_from,threshold_to,max_start,max_end,min_between,min_duration,min_number_spike):
            self.error_popup("Please enter correct values", "Value Error")
            return
        
        if (dead_time < (pre+post)):
            self.error_popup("Dead time must be more or equal than (pre + post)", "Intersection Error")
            return 

        spike_plot, spike_plot_error_msg = plot_all_spikes_together(analog_stream_path, channel_id, comp_number, pre, post, dead_time, spike_number,
                                                        self.tab2_canvas, 0, from_in_s, to_in_s, high_pass, low_pass, threshold_from, threshold_to)
        
        spike_plot_dots, spike_plot_dots_error_msg = plot_signal_with_spikes_or_stimulus(analog_stream_path, channel_id, self.tab2_canvas, 1, True, from_in_s, to_in_s, high_pass, low_pass, threshold_from, threshold_to, dead_time,
                                                                                        max_start, max_end, min_between, min_duration, min_number_spike)

        fourier, fourier_error_msg = plot_signal_frequencies(analog_stream_path, channel_id, self.tab2_canvas, 2, from_in_s, to_in_s)

        if spike_plot:
            self.error_popup(spike_plot_error_msg, "Plot Error")
        elif spike_plot_dots:
            self.error_popup(spike_plot_dots_error_msg, "Plot Error")
        elif fourier:
            self.error_popup(fourier_error_msg, "Plot Error")

    def plot_stimulus(self):
        analog_stream_path = self.browse_text_box_tab1.text()
        channel_id = self._check_value(self.channel_id_tab3.currentText(), None)
        pre = self._check_value(self.extract_pre_tab3.text(), None)
        post = self._check_value(self.extract_post_tab3.text(), None)
        dead_time = self._check_value(self.dead_time_tab3.text(), None)
        from_in_s = self._check_value(self.extract_from_tab3.text(), 0)
        to_in_s = self._check_value(self.extract_to_tab3.text(), None)
        threshold_from = self._check_value(self.threshold_from_tab3.text(), -0.0003)
        threshold_to = self._check_value(self.threshold_to_tab3.text(), None)
        high_pass = None
        low_pass = None
        
        if -1 in (channel_id, pre, post, dead_time, from_in_s, to_in_s, threshold_from, threshold_to):
            self.error_popup("Please enter correct values", "Value Error")
            return
        
        if (dead_time < (pre+post)):
            self.error_popup("Dead time must be more or equal than (pre + post)", "Intersection Error")
            return 

        stimule_error, stimule_error_msg = plot_stimulus_average(analog_stream_path, channel_id, from_in_s, to_in_s, dead_time, threshold_from, 
                                                                 pre, post, self.tab3_canvas, 0)

        stimule_dots_error, stimule_dots_error_msg = plot_signal_with_spikes_or_stimulus(analog_stream_path, channel_id, self.tab3_canvas, 1, False, 
                                                                                            from_in_s, to_in_s, high_pass, low_pass ,threshold_from, threshold_to, dead_time)

        fourier, fourier_error_msg = plot_signal_frequencies(analog_stream_path, channel_id, self.tab3_canvas, 2, from_in_s, to_in_s)

        if stimule_error:
             self.error_popup(stimule_error_msg, "Plot Error")       
        elif stimule_dots_error:
            self.error_popup(stimule_dots_error_msg, "Plot Error")
        elif fourier:
            self.error_popup(fourier_error_msg, "Plot Error")


    def save_waveform(self):
        analog_stream_path = self.browse_text_box_tab1.text()
        channel_id = self._check_value(self.channel_id_tab1.currentText(),None)
        from_in_s = self._check_value(self.extract_from_tab1.text(),0)
        to_in_s = self._check_value(self.extract_to_tab1.text(),None)
        high_pass = self._check_value(self.filter_high_tab1.text(), None)
        low_pass = self._check_value(self.filter_low_tab1.text(), None)
        
        if -1 in (channel_id, from_in_s, to_in_s, high_pass, low_pass):
            self.error_popup("Please enter correct values", "Value Error")
            return
        
        file_save_path = self.get_file_for_save(self.extract_text_box_tab1)
        if not file_save_path:
            return
        
        save_error, value = extract_waveform(analog_stream_path, file_save_path, channel_id, from_in_s, to_in_s, high_pass, low_pass)
        
        if save_error:
            self.error_popup(value, "Extract Error")
        else:
            self.info_popup("Data created successfully","Extract success")

    def save_spike(self):
        analog_stream_path = self.browse_text_box_tab1.text()
        channel_id = self._check_value(self.channel_id_tab2.currentText(), None)
        from_in_s = self._check_value(self.extract_from_tab2.text(), 0)
        to_in_s = self._check_value(self.extract_to_tab2.text(), None)
        threshold_from = self._check_value(self.threshold_from_tab2.text(), None)
        threshold_to = self._check_value(self.threshold_to_tab2.text(), None)
        high_pass = self._check_value(self.filter_high_tab2.text(), None)
        low_pass = self._check_value(self.filter_low_tab2.text(), None)
        dead_time = self._check_value(self.dead_time_tab2.text(), None)
        bin_width = self._check_value(self.tab2_bin.text(), None)

        max_start = self._check_value(self.tab2_max_start.text(), None)
        max_end = self._check_value(self.tab2_max_end.text(), None)
        min_between = self._check_value(self.tab2_min_interval.text(), None)
        min_duration = self._check_value(self.tab2_min_duration.text(), None)
        min_number_spike = self._check_value(self.tab2_min_number.text(), None)
        
        if -1 in (channel_id, from_in_s, to_in_s, threshold_from, threshold_to, high_pass, low_pass, 
                    dead_time, bin_width, max_start, max_end, min_between, min_duration, min_number_spike):
            self.error_popup("Please enter correct values", "Value Error")
            return
        
        file_save_path = self.get_file_for_save(self.extract_text_box_tab2)
        if not file_save_path:
            return
        
        save_error, value = extract_spike(analog_stream_path, file_save_path, channel_id, from_in_s, to_in_s, threshold_from, threshold_to, high_pass, low_pass, dead_time, bin_width,
                                            max_start, max_end, min_between, min_duration, min_number_spike)

        if save_error:
            self.error_popup(value, "Extract Error")
        else:
            self.info_popup("Data created successfully", "Extract success")

    def save_stimulus(self):
        analog_stream_path = self.browse_text_box_tab1.text()
        channel_id = self._check_value(self.channel_id_tab3.currentText(), None)
        from_in_s = self._check_value(self.extract_from_tab3.text(), 0)
        to_in_s = self._check_value(self.extract_to_tab3.text(), None)
        threshold_from = self._check_value(self.threshold_from_tab3.text(), -0.0003)
        dead_time = self._check_value(self.dead_time_tab3.text(), None)
        pre = self._check_value(self.extract_pre_tab3.text(), None)
        post = self._check_value(self.extract_post_tab3.text(), None)
        
        if -1 in (analog_stream_path, channel_id, from_in_s, to_in_s, threshold_from, dead_time, pre, post):
            self.error_popup("Please enter correct values", "Value Error")
            return

        if (dead_time < (pre+post)):
            self.error_popup("Dead time must be more or equal than (pre + post)", "Intersection Error")
            return 
        
        file_save_path = self.get_file_for_save(self.extract_text_box_tab3)
        if not file_save_path:
            return

        save_error, value = extract_stimulus(analog_stream_path, file_save_path, channel_id, from_in_s, to_in_s, threshold_from, dead_time, pre, post)
        if save_error:
            self.error_popup(value, "Extract Error")
        else:
            self.info_popup("Data created successfully", "Extract success")


    def get_file_for_open(self, text_box):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        if fileName:
            text_box.setText(fileName)
            error_message, message = get_all_channel_ids(fileName)

            if error_message:
                self.error_popup(message, "File Error")
                return

            message.insert(0,"all")
            for channel_id in [self.channel_id_tab1, self.channel_id_tab2, self.channel_id_tab3]:
                channel_id.clear()
                channel_id.addItems(message)
                channel_id.setStyleSheet("combobox-popup: 0")
    
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
        QtWidgets.QMessageBox.critical(self,title_text,txt)

    def info_popup(self, txt, title_text):
        QtWidgets.QMessageBox.information(self,title_text,txt)

    def clear_qlines(self, *args):
        for item in args:
            item.setText("")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MEA_app()
    win.show()
    sys.exit(app.exec_())