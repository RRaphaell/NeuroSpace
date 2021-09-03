from PyQt5 import QtCore, QtGui, QtWidgets


class UiDialog(QtWidgets.QMainWindow):
    def setupUI(self, dialog):
        dialog.setObjectName("AAAAAAAAAAAAAA")
        dialog.resize(100, 100)
        self.verticalLayout = QtWidgets.QVBoxLayout(dialog)
        self.retranslateUI(dialog)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslateUI(self, dialog):
        _translate = QtCore.QCoreApplication.translate
        dialog.setWindowTitle(_translate("Dialog", "Dialog"))