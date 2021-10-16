import sys
from PyQt5 import QtWidgets
from UI import NeuroSpace


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = NeuroSpace()
    win.show()
    sys.exit(app.exec_())

