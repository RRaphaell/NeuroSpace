import sys
import os
from PyQt5 import QtWidgets,QtCore, QtGui
from timeStamp_info import save_channel_info, plot_analog_stream_channel, draw_channel_spikes
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

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))  
        
        self.setGeometry(200,200,1000,500)
        self.setCentralWidget(self.tabs)
        
    def create_tab2(self):
        tab2_layout = QtWidgets.QGridLayout()
        self.statusBar()

        group_box_browse, self.browse_text_box_tab2 = self.create_group_open_from()

        group_box_channel_stream, self.channel_id_tab2, self.stream_id_tab2 = self.create_group_select_id()

        group_box_pre_post, self.extract_pre_tab2, self.extract_post_tab2, self.dead_time_tab2 = self.create_group_select_time_range_tab2()

        group_box_component_spike, self.component, self.spike = self.create_group_component_spike()

        plot_file_btn = QtWidgets.QPushButton(self)
        plot_file_btn.setFixedSize(300,40)
        plot_file_btn.setText("Plot Spike")
        plot_file_btn.clicked.connect(self.plot_spike)  

        plot_group_box, self.tab2_figure,self.tab2_canvas  = self.create_plot_grop_box("Spike") 

        tab2_layout.addWidget(group_box_browse,0,0)
        tab2_layout.addWidget(group_box_channel_stream,1,0)
        tab2_layout.addWidget(group_box_pre_post,2,0)
        tab2_layout.addWidget(group_box_component_spike,3,0)
        tab2_layout.setRowStretch(4,0)
        tab2_layout.addWidget(plot_file_btn,5,0)
        tab2_layout.addWidget(plot_group_box,0,2,6,1)
        self.tab2.setLayout(tab2_layout)

    def create_group_select_time_range_tab2(self):
        group_box_pre_post = QtWidgets.QGroupBox("Select time range")
        group_box_pre_post_layout = QtWidgets.QHBoxLayout()
        extract_pre_tab2 = QtWidgets.QLineEdit(self)
        extract_pre_tab2.setFixedWidth(50)
        extract_pre_label = QtWidgets.QLabel(self)
        extract_pre_label.setText("Pre: ")
        extract_post_tab2 = QtWidgets.QLineEdit(self)
        extract_post_tab2.setFixedWidth(50)
        extract_post_label = QtWidgets.QLabel(self)
        extract_post_label.setText("Post: ")
        dead_time_tab2 = QtWidgets.QLineEdit(self)
        dead_time_tab2.setFixedWidth(50)
        dead_time_label = QtWidgets.QLabel(self)
        dead_time_label.setText("Dead time: ")

        group_box_pre_post_layout.addWidget(extract_pre_label)
        group_box_pre_post_layout.addWidget(extract_pre_tab2)
        group_box_pre_post_layout.addWidget(extract_post_label)
        group_box_pre_post_layout.addWidget(extract_post_tab2)
        group_box_pre_post_layout.addWidget(dead_time_label)
        group_box_pre_post_layout.addWidget(dead_time_tab2)
        group_box_pre_post.setLayout(group_box_pre_post_layout)
        group_box_pre_post.setFixedSize(300,70)
        group_box_pre_post.setStatusTip("Choose particular time, leave empty for full time")
        return group_box_pre_post, extract_pre_tab2, extract_post_tab2, dead_time_tab2 

    def create_group_component_spike(self):
        group_box_component_spike = QtWidgets.QGroupBox("Select numbers")
        group_box_component_spike_layout = QtWidgets.QHBoxLayout()
        component = QtWidgets.QLineEdit(self)
        component.setFixedWidth(40)
        component.setStatusTip("Choose component number, leave empty for zero component")
        component_label = QtWidgets.QLabel(self)
        component_label.setText("Component number:")
        spike = QtWidgets.QLineEdit(self)
        spike.setFixedWidth(40)
        spike.setStatusTip("Choose spike number, leave empty for all spikes")
        spike_label = QtWidgets.QLabel(self)
        spike_label.setText("Spike number:")
        group_box_component_spike_layout.addWidget(component_label)
        group_box_component_spike_layout.addWidget(component)
        group_box_component_spike_layout.addWidget(spike_label)
        group_box_component_spike_layout.addWidget(spike)
        group_box_component_spike.setLayout(group_box_component_spike_layout)
        group_box_component_spike.setFixedSize(300,70)   
        return group_box_component_spike, component, spike

    def create_tab1(self):
        tab1_layout = QtWidgets.QGridLayout()
        self.statusBar()

        group_box_browse, self.browse_text_box_tab1 = self.create_group_open_from()
        group_box_channel_stream, self.channel_id_tab1, self.stream_id_tab1 = self.create_group_select_id()
        group_box_from_to, self.extract_from_tab1, self.extract_to_tab1 = self.create_group_select_time_range_tab1()

        plot_file_btn = QtWidgets.QPushButton(self)
        plot_file_btn.setFixedSize(300,40)
        plot_file_btn.setText("Plot Waveform")
        plot_file_btn.clicked.connect(self.plot_waveform)   

        space_between_plotbtn_extract = QtWidgets.QWidget()
        space_between_plotbtn_extract.setFixedSize(300,50)             

        group_box_extract = self.create_group_extract()

        plot_group_box, self.tab1_figure, self.tab1_canvas  = self.create_plot_grop_box("Waveform")

        tab1_layout.addWidget(group_box_browse,0,0)
        tab1_layout.addWidget(group_box_channel_stream,1,0)
        tab1_layout.addWidget(group_box_from_to,2,0)
        tab1_layout.addWidget(plot_file_btn,3,0)
        tab1_layout.setRowStretch(4,0)
        tab1_layout.addWidget(group_box_extract,5,0)
        tab1_layout.addWidget(plot_group_box,0,2,6,1)
        
        # tab1_layout.setContentsMargins(10,10,100,100)
        # tab1_layout.setSizeConstraint(100)
        self.tab1.setLayout(tab1_layout)

    def create_group_open_from(self):
        group_box_browse = QtWidgets.QGroupBox("Open from")
        group_box_browse_layout = QtWidgets.QHBoxLayout()
        browse_text_box = QtWidgets.QLineEdit(self)
        browse_text_box.setDisabled(True)
        browse = QtWidgets.QPushButton(self)
        browse.setText("Browse file")
        browse.clicked.connect(lambda x: self.getfiles(browse_text_box))
        group_box_browse_layout.addWidget(browse_text_box)
        group_box_browse_layout.addWidget(browse)
        group_box_browse.setLayout(group_box_browse_layout)
        group_box_browse.setFixedSize(300,70)
        group_box_browse.setStatusTip("Choose hf5 format file to open")
        return group_box_browse, browse_text_box
    
    def create_group_select_time_range_tab1(self):
        group_box_from_to = QtWidgets.QGroupBox("Select time range")
        group_box_from_to_layout = QtWidgets.QHBoxLayout()
        extract_from = QtWidgets.QLineEdit(self)
        extract_from.setFixedWidth(70)
        extract_from_label = QtWidgets.QLabel(self)
        extract_from_label.setText("From: ")
        extract_to = QtWidgets.QLineEdit(self)
        extract_to.setFixedWidth(70)
        extract_to_label = QtWidgets.QLabel(self)
        extract_to_label.setText("To: ")
        group_box_from_to_layout.addWidget(extract_from_label)
        group_box_from_to_layout.addWidget(extract_from)
        group_box_from_to_layout.addWidget(extract_to_label)
        group_box_from_to_layout.addWidget(extract_to)
        group_box_from_to.setLayout(group_box_from_to_layout)
        group_box_from_to.setFixedSize(300,70)
        group_box_from_to.setStatusTip("Choose particular time, leave empty for full time")
        return group_box_from_to, extract_from, extract_to

    def create_group_select_id(self):
        group_box_channel_stream = QtWidgets.QGroupBox("Select id")
        group_box_channel_stream_layout = QtWidgets.QHBoxLayout()
        channel_id = QtWidgets.QLineEdit(self)
        channel_id.setFixedWidth(70)
        channel_id.setStatusTip("Choose particular channel, leave empty for all Channels")
        channel_id_label = QtWidgets.QLabel(self)
        channel_id_label.setText("Channel_id:")
        stream_id = QtWidgets.QLineEdit(self)
        stream_id.setFixedWidth(70)
        stream_id.setStatusTip("Choose particular stream, leave empty for all Streams")
        stream_id_label = QtWidgets.QLabel(self)
        stream_id_label.setText("Stream_id:")
        group_box_channel_stream_layout.addWidget(channel_id_label)
        group_box_channel_stream_layout.addWidget(channel_id)
        group_box_channel_stream_layout.addWidget(stream_id_label)
        group_box_channel_stream_layout.addWidget(stream_id)
        group_box_channel_stream.setLayout(group_box_channel_stream_layout)
        group_box_channel_stream.setFixedSize(300,70)
        return group_box_channel_stream, channel_id, stream_id

    def create_group_extract(self):
        group_box_extract = QtWidgets.QGroupBox("Save to")
        group_box_extract_layout = QtWidgets.QHBoxLayout()
        self.extract_text_box = QtWidgets.QLineEdit(self)
        self.extract_text_box.setDisabled(True)
        extract = QtWidgets.QPushButton(self)
        extract.setText("Extract")
        extract.clicked.connect(self.extract_file)
        group_box_extract_layout.addWidget(self.extract_text_box)
        group_box_extract_layout.addWidget(extract)
        group_box_extract.setLayout(group_box_extract_layout)
        group_box_extract.setFixedSize(300,70)
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
        channel_id = self._check_value(self.channel_id_tab1.text(),None)
        from_in_s = self._check_value(self.extract_from_tab1.text(),0)
        to_in_s = self._check_value(self.extract_to_tab1.text(),None)
        if -1 in (stream_id,channel_id,from_in_s,to_in_s):
            self.error_popup("Please enter correct values")
            return
        plot_error, value = plot_analog_stream_channel(analog_stream_path,channel_id,from_in_s,to_in_s,self.tab1_canvas,self.tab1_figure)
        if plot_error:
            self.error_popup(value)
    
    def plot_spike(self):
        analog_stream_path = self.browse_text_box_tab2.text()
        stream_id = self._check_value(self.stream_id_tab2.text(),None)
        channel_id = self._check_value(self.channel_id_tab2.text(),None)
        
        pre = self._check_value(self.extract_pre_tab2.text(),0)
        post = self._check_value(self.extract_post_tab2.text(),None)
        dead_time = self._check_value(self.dead_time_tab2.text(),None)
        comp_number = self._check_value(self.component.text(),None)
        spike_number = self._check_value(self.spike.text(),None)
        
        if -1 in (stream_id,channel_id,pre,post,dead_time,comp_number,spike_number):
            self.error_popup("Please enter correct values")
            return
        plot_error, value = draw_channel_spikes(analog_stream_path,channel_id,comp_number,pre,post,dead_time,spike_number,
                                                self.tab2_canvas,self.tab2_figure)
        if plot_error:
            self.error_popup(value)

    def getfiles(self,text_box):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        text_box.setText(fileName)
    
    def extract_file(self):
        analog_stream_path = self.browse_text_box_tab1.text()
        stream_id = self._check_value(self.stream_id_tab1.text(),None)
        channel_id = self._check_value(self.channel_id_tab1.text(),None)
        from_in_s = self._check_value(self.extract_from_tab1.text(),0)
        to_in_s = self._check_value(self.extract_to_tab1.text(),None)
        if -1 in (stream_id,channel_id,from_in_s,to_in_s):
            self.error_popup("Please enter correct values")
            return
        name, _ = QtWidgets.QFileDialog.getSaveFileName(self,'Save File', options=QtWidgets.QFileDialog.DontUseNativeDialog)
        self.extract_text_box.setText(name)
        file_save_path = self.extract_text_box.text()
        save_error, value = save_channel_info(analog_stream_path, file_save_path, channel_id=channel_id, from_in_s=from_in_s, to_in_s=to_in_s)
        if save_error:
            self.error_popup(value)
        
    def _check_value(self,value,res):
        if value == "":
            return res
        try:
            return float(value)
        except ValueError:
            return -1

    def error_popup(self,txt):
        QtWidgets.QMessageBox.critical(self,"Unable to Extract",txt)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = all_together()
    win.show()
    sys.exit(app.exec_())