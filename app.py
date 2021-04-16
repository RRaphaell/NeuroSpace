import sys
import os
from PyQt5 import QtWidgets,QtCore, QtGui
from timeStamp_info import save_channel_info, plot_analog_stream_channel, draw_channel_spikes, get_channel_ids, filter_base_freqeuncy
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style
style.use('fivethirtyeight')
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd

class all_together(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        
        self.tabs.addTab(self.tab1,"Extract")
        self.tabs.addTab(self.tab2,"Plot")

        self.create_tab1()
        self.create_tab2()

        self.stream_id_tab1.setDisabled(True)
        self.stream_id_tab2.setDisabled(True)

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))  

        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.dir_path,"images","app_icon.png")))
        # როცა აპლიკაციის სახეს მივცემთ ეს 3 ხაზი წესით აღარ დაჭირდება რომ ტასკბარზე აიქონ გამოჩნდეს
        import ctypes
        myappid = 'mycompany.myproduct.subproduct.version'                      
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # File = open(os.path.join(self.dir_path,"styles/font_style.qss"),"r")
        # with File:
        #     qss = File.read()
        #     self.setStyleSheet(qss)

        self.setGeometry(200,100,1000,550)
        self.setWindowTitle("MEA System Analyzer")
        self.setCentralWidget(self.tabs)
        
    def create_tab2(self):
        tab2_layout = QtWidgets.QGridLayout()
        self.statusBar()

        group_box_channel_stream, self.channel_id_tab2, self.stream_id_tab2 = self.create_group_select_id()
        group_box_browse, self.browse_text_box_tab2 = self.create_group_open_from(self.channel_id_tab2,self.stream_id_tab2)
        group_box_pre_post, self.extract_pre_tab2, self.extract_post_tab2, self.dead_time_tab2 = self.create_group_select_time_range_tab2()
        group_box_component_spike, self.component, self.spike = self.create_group_component_spike()
        group_box_filter, self.filter_low_tab2, self.filter_high_tab2 = self.create_group_filter() 
        group_box_filter.toggled.connect(lambda : self.clear_qlines(self.filter_low_tab2, self.filter_high_tab2))
        group_box_from_to, self.extract_from_tab2, self.extract_to_tab2 = self.create_group_select_time_range_tab1()
        group_box_from_to.setCheckable(True)
        group_box_from_to.setChecked(False)
        group_box_from_to.toggled.connect(lambda : self.clear_qlines(self.extract_from_tab2, self.extract_to_tab2))

        plot_file_btn = QtWidgets.QPushButton(self)
        plot_file_btn.setFixedSize(235,35)
        plot_file_btn.setText("Plot Spike")
        plot_file_btn.clicked.connect(self.plot_spike)  
        plot_file_btn.setStyleSheet("QPushButton::hover"
                                    "{"
                                    "background-color : lightblue;"
                                    "}") 

        plot_group_box, self.tab2_figure,self.tab2_canvas  = self.create_plot_grop_box("Spike") 

        tab2_layout.addWidget(group_box_browse,0,0)
        tab2_layout.addWidget(group_box_channel_stream,1,0)
        tab2_layout.addWidget(group_box_pre_post,2,0)
        tab2_layout.addWidget(group_box_from_to,3,0)
        tab2_layout.addWidget(group_box_component_spike,4,0)
        tab2_layout.addWidget(group_box_filter,5,0)
        tab2_layout.setRowStretch(6,0)
        tab2_layout.addWidget(plot_file_btn,7,0)
        tab2_layout.addWidget(plot_group_box,0,2,8,1)
        self.tab2.setLayout(tab2_layout)

    def create_group_select_time_range_tab2(self):
        group_box_pre_post = QtWidgets.QGroupBox("Select time range")
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
        group_box_pre_post.setFixedSize(235,60)
        group_box_pre_post.setStatusTip("Choose particular time (second)")
        return group_box_pre_post, extract_pre_tab2, extract_post_tab2, dead_time_tab2 

    def create_group_component_spike(self):
        group_box_component_spike = QtWidgets.QGroupBox("Select numbers")
        group_box_component_spike_layout = QtWidgets.QHBoxLayout()
        component = QtWidgets.QLineEdit(self)
        component.setFixedWidth(40)
        component.setStatusTip("Choose component number, leave empty for one component")
        component_label = QtWidgets.QLabel(self)
        component_label.setText("Component")
        spike = QtWidgets.QLineEdit(self)
        spike.setFixedWidth(40)
        spike.setStatusTip("Choose spike number, leave empty for all spikes")
        spike_label = QtWidgets.QLabel(self)
        spike_label.setText("Spike")
        group_box_component_spike_layout.addWidget(component_label)
        group_box_component_spike_layout.addWidget(component)
        group_box_component_spike_layout.addWidget(spike_label)
        group_box_component_spike_layout.addWidget(spike)
        group_box_component_spike.setLayout(group_box_component_spike_layout)
        group_box_component_spike.setFixedSize(235,60)   
        return group_box_component_spike, component, spike

    def create_tab1(self):
        tab1_layout = QtWidgets.QGridLayout()
        self.statusBar()

        group_box_channel_stream, self.channel_id_tab1, self.stream_id_tab1 = self.create_group_select_id()
        group_box_browse, self.browse_text_box_tab1 = self.create_group_open_from(self.channel_id_tab1,self.stream_id_tab1)
        group_box_from_to, self.extract_from_tab1, self.extract_to_tab1 = self.create_group_select_time_range_tab1()

        plot_file_btn = QtWidgets.QPushButton(self)
        plot_file_btn.setFixedSize(235,35)
        plot_file_btn.setText("Plot Waveform")
        plot_file_btn.clicked.connect(self.plot_waveform) 
        plot_file_btn.setStyleSheet("QPushButton::hover"
                                    "{"
                                    "background-color : lightblue;"
                                    "}")  

        space_between_plotbtn_extract = QtWidgets.QWidget()
        space_between_plotbtn_extract.setFixedSize(235,50)  

        group_box_filter, self.filter_low_tab1, self.filter_high_tab1 = self.create_group_filter()  
        group_box_filter.toggled.connect(lambda : self.clear_qlines(self.filter_low_tab1,self.filter_high_tab1))

        group_box_extract = self.create_group_extract()
        plot_group_box, self.tab1_figure, self.tab1_canvas  = self.create_plot_grop_box("Waveform")

        tab1_layout.addWidget(group_box_browse,0,0)
        tab1_layout.addWidget(group_box_channel_stream,1,0)
        tab1_layout.addWidget(group_box_from_to,2,0)
        tab1_layout.addWidget(group_box_filter,3,0)
        tab1_layout.addWidget(plot_file_btn,4,0)
        tab1_layout.setRowStretch(5,0)
        tab1_layout.addWidget(group_box_extract,6,0)
        tab1_layout.addWidget(plot_group_box,0,2,7,1)
        
        # tab1_layout.setContentsMargins(10,10,100,100)
        # tab1_layout.setSizeConstraint(100)
        self.tab1.setLayout(tab1_layout)

    def create_group_open_from(self,channel_id,stream_id):
        group_box_browse = QtWidgets.QGroupBox("Open from")
        group_box_browse_layout = QtWidgets.QHBoxLayout()
        browse_text_box = QtWidgets.QLineEdit(self)
        browse_text_box.setDisabled(True)
        browse = QtWidgets.QPushButton(self)
        browse.setText("Browse file")
        browse.clicked.connect(lambda x: self.getfiles(browse_text_box,channel_id,stream_id))
        browse.setStyleSheet("QPushButton::hover"
                                    "{"
                                    "background-color : lightblue;"
                                    "}") 
        group_box_browse_layout.addWidget(browse_text_box)
        group_box_browse_layout.addWidget(browse)
        group_box_browse.setLayout(group_box_browse_layout)
        group_box_browse.setFixedSize(235,60)
        group_box_browse.setStatusTip("Choose hf5 format file to open")
        return group_box_browse, browse_text_box
    
    def create_group_select_time_range_tab1(self):
        group_box_from_to = QtWidgets.QGroupBox("Select time range")
        group_box_from_to_layout = QtWidgets.QHBoxLayout()
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
        group_box_from_to.setFixedSize(235,60)
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
        stream_id = QtWidgets.QLineEdit(self)
        stream_id.setFixedWidth(40)
        stream_id.setStatusTip("Choose particular stream, leave empty for all Streams")
        stream_id_label = QtWidgets.QLabel(self)
        stream_id_label.setText("Stream_id")
        group_box_channel_stream_layout.addWidget(channel_id_label)
        group_box_channel_stream_layout.addWidget(channel_id)
        group_box_channel_stream_layout.addWidget(stream_id_label)
        group_box_channel_stream_layout.addWidget(stream_id)
        group_box_channel_stream.setLayout(group_box_channel_stream_layout)
        group_box_channel_stream.setFixedSize(235,60)
        return group_box_channel_stream, channel_id, stream_id

    def create_group_filter(self):
        group_box_filter = QtWidgets.QGroupBox("Set filter")
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
        group_box_filter.setFixedSize(235,60)
        group_box_filter.setStatusTip("Choose filter (Hz), low high or band pass")
        return group_box_filter, filter_low, filter_high
        
    def create_group_extract(self):
        group_box_extract = QtWidgets.QGroupBox("Save to")
        group_box_extract_layout = QtWidgets.QHBoxLayout()
        self.extract_text_box = QtWidgets.QLineEdit(self)
        self.extract_text_box.setDisabled(True)
        extract = QtWidgets.QPushButton(self)
        extract.setText("Extract")
        extract.clicked.connect(self.extract_file)
        extract.setStyleSheet("QPushButton::hover"
                                    "{"
                                    "background-color : lightblue;"
                                    "}") 
        group_box_extract_layout.addWidget(self.extract_text_box)
        group_box_extract_layout.addWidget(extract)
        group_box_extract.setLayout(group_box_extract_layout)
        group_box_extract.setFixedSize(235,60)
        group_box_extract.setStatusTip("Choose path to save csv file")
        return group_box_extract

    def create_plot_grop_box(self,title):
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

        figure = plt.figure()
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        plot_group_box.setLayout(layout)
        return plot_group_box, figure, canvas
    
    def plot_waveform(self):
        analog_stream_path = self.browse_text_box_tab1.text()
        stream_id = self._check_value(self.stream_id_tab1.text(),None)
        channel_id = self._check_value(self.channel_id_tab1.currentText(),None)
        from_in_s = self._check_value(self.extract_from_tab1.text(),0)
        to_in_s = self._check_value(self.extract_to_tab1.text(),None)
        high_pass = self._check_value(self.filter_high_tab1.text(),None)
        low_pass = self._check_value(self.filter_low_tab1.text(),None)
        if -1 in (stream_id,channel_id,from_in_s,to_in_s):
            self.error_popup("Please enter correct values", "Value Error")
            return
        
        plot_error, value = plot_analog_stream_channel(analog_stream_path, channel_id, from_in_s, to_in_s,
                                                        self.tab1_canvas, self.tab1_figure, high_pass, low_pass)
        if plot_error:
            self.error_popup(value, "Plot Error")
    
    def plot_spike(self):
        analog_stream_path = self.browse_text_box_tab2.text()
        stream_id = self._check_value(self.stream_id_tab2.text(),None)
        channel_id = self._check_value(self.channel_id_tab2.currentText(),None)
        
        pre = self._check_value(self.extract_pre_tab2.text(),0)
        post = self._check_value(self.extract_post_tab2.text(),None)
        dead_time = self._check_value(self.dead_time_tab2.text(),None)
        comp_number = self._check_value(self.component.text(),None)
        spike_number = self._check_value(self.spike.text(),None)
        from_in_s = self._check_value(self.extract_from_tab2.text(),0)
        to_in_s = self._check_value(self.extract_to_tab2.text(),None)
        high_pass = self._check_value(self.filter_high_tab2.text(),None)
        low_pass = self._check_value(self.filter_low_tab2.text(),None)
        
        if -1 in (stream_id,channel_id,pre,post,dead_time,comp_number,spike_number):
            self.error_popup("Please enter correct values", "Value Error")
            return
        plot_error, value = draw_channel_spikes(analog_stream_path, channel_id, comp_number, pre, post, dead_time, spike_number,
                                                self.tab2_canvas, self.tab2_figure, from_in_s, to_in_s, high_pass, low_pass)
        if plot_error:
            self.error_popup(value, "Plot Error")

    def getfiles(self,text_box,channel_id,stream_id):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        text_box.setText(fileName)
        error_message, message = get_channel_ids(fileName)
        if error_message:
            self.error_popup(message, "File Error")
            return
        message.insert(0,"all")
        channel_id.clear()
        channel_id.addItems(message)
        channel_id.setStyleSheet("combobox-popup: 0")
        
    def extract_file(self):
        analog_stream_path = self.browse_text_box_tab1.text()
        stream_id = self._check_value(self.stream_id_tab1.text(),None)
        channel_id = self._check_value(self.channel_id_tab1.currentText(),None)
        from_in_s = self._check_value(self.extract_from_tab1.text(),0)
        to_in_s = self._check_value(self.extract_to_tab1.text(),None)
        if -1 in (stream_id,channel_id,from_in_s,to_in_s):
            self.error_popup("Please enter correct values", "Value Error")
            return
        name, _ = QtWidgets.QFileDialog.getSaveFileName(self,'Save File', options=QtWidgets.QFileDialog.DontUseNativeDialog)
        self.extract_text_box.setText(name)
        file_save_path = self.extract_text_box.text()
        save_error, value = save_channel_info(analog_stream_path, file_save_path, channel_id=channel_id, from_in_s=from_in_s, to_in_s=to_in_s)
        if save_error:
            self.error_popup(value, "Extract Error")
        else:
            self.info_popup("Data created successfully","Extract success")
        
    def _check_value(self,value,res):
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

    def clear_qlines(self,*args):
        for item in args:
            item.setText("")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = all_together()
    win.show()
    sys.exit(app.exec_())