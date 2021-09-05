import sys
from PyQt5 import QtWidgets
from UI import NeuroSpace


def restart_program():
    import os
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, *sys.argv)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = NeuroSpace()
    win.show()

    answer = input("Do you want to restart this program ? ")
    if answer.lower().strip() in "y yes".split():
        restart_program()

    sys.exit(app.exec_())
