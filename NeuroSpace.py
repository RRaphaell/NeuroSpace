import sys
from PyQt5 import QtWidgets
from UI import NeuroSpace

"""
TODO : I need to search how this kind of functions are documented
"""
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = NeuroSpace()
    win.show()
    sys.exit(app.exec_())

