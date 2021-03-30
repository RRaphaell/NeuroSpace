import sys
import os
from PyQt5 import QtWidgets,QtCore, QtGui
from timeStamp_info import save_channel_info

class all_together(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        
        self.tabs.addTab(self.tab1,"Extract")
        self.tabs.addTab(self.tab2,"Plot")
        self.create_tab1()

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))  
        
        self.setGeometry(200,200,600,400)
        self.setCentralWidget(self.tabs)
        
    def create_tab1(self):
        tab1_layout = QtWidgets.QVBoxLayout()
        self.statusBar()
        group_box_browse = QtWidgets.QGroupBox("Open from")
        group_box_browse_layout = QtWidgets.QHBoxLayout()
        self.browse_text_box = QtWidgets.QLineEdit(self)
        self.browse_text_box.setDisabled(True)
        browse = QtWidgets.QPushButton(self)
        browse.setText("Browse file")
        browse.clicked.connect(self.getfiles)
        group_box_browse_layout.addWidget(self.browse_text_box)
        group_box_browse_layout.addWidget(browse)
        group_box_browse.setLayout(group_box_browse_layout)
        group_box_browse.setFixedSize(300,70)
        group_box_browse.setStatusTip("Choose hf5 format file to open")

        group_box_from_to = QtWidgets.QGroupBox("Select time range")
        group_box_from_to_layout = QtWidgets.QHBoxLayout()
        self.extract_from = QtWidgets.QLineEdit(self)
        self.extract_from.setFixedWidth(70)
        extract_from_label = QtWidgets.QLabel(self)
        extract_from_label.setText("From: ")
        self.extract_to = QtWidgets.QLineEdit(self)
        self.extract_to.setFixedWidth(70)
        extract_to_label = QtWidgets.QLabel(self)
        extract_to_label.setText("To: ")
        group_box_from_to_layout.addWidget(extract_from_label)
        group_box_from_to_layout.addWidget(self.extract_from)
        group_box_from_to_layout.addWidget(extract_to_label)
        group_box_from_to_layout.addWidget(self.extract_to)
        group_box_from_to.setLayout(group_box_from_to_layout)
        group_box_from_to.setFixedSize(300,70)
        group_box_from_to.setStatusTip("Choose particular time, leave empty for full time")

        group_box_channel_stream = QtWidgets.QGroupBox("Select id")
        group_box_channel_stream_layout = QtWidgets.QHBoxLayout()
        self.channel_id = QtWidgets.QLineEdit(self)
        self.channel_id.setFixedWidth(70)
        self.channel_id.setStatusTip("Choose particular channel, leave empty for all Channels")
        channel_id_label = QtWidgets.QLabel(self)
        channel_id_label.setText("Channel_id:")
        self.stream_id = QtWidgets.QLineEdit(self)
        self.stream_id.setFixedWidth(70)
        self.stream_id.setStatusTip("Choose particular stream, leave empty for all Streams")
        stream_id_label = QtWidgets.QLabel(self)
        stream_id_label.setText("Stream_id:")
        group_box_channel_stream_layout.addWidget(channel_id_label)
        group_box_channel_stream_layout.addWidget(self.channel_id)
        group_box_channel_stream_layout.addWidget(stream_id_label)
        group_box_channel_stream_layout.addWidget(self.stream_id)
        group_box_channel_stream.setLayout(group_box_channel_stream_layout)
        group_box_channel_stream.setFixedSize(300,70)

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

        tab1_layout.addWidget(group_box_browse)
        tab1_layout.addWidget(group_box_from_to)
        tab1_layout.addWidget(group_box_channel_stream)
        tab1_layout.addWidget(group_box_extract)
        tab1_layout.addStretch(1)
        tab1_layout.setContentsMargins(10,10,100,100)
        tab1_layout.setSizeConstraint(100)

        self.tab1.setLayout(tab1_layout)

    def getfiles(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        self.browse_text_box.setText(fileName)
    
    def extract_file(self):
        analog_stream_path = self.browse_text_box.text()
        stream_id = self._check_value(self.stream_id.text(),None)
        channel_id = self._check_value(self.channel_id.text(),None)
        from_in_s = self._check_value(self.extract_from.text(),0)
        to_in_s = self._check_value(self.extract_to.text(),None)
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