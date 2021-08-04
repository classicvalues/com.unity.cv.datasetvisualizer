import sys
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QFileDialog, QWidget

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

dialog = QFileDialog()
dialog.setFileMode(QFileDialog.Directory)
dialog.setOption(QFileDialog.DontUseNativeDialog, True)
dialog.setWindowState(dialog.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
dialog.activateWindow()
dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
dialog.show()

if dialog.exec_():
    fileName = dialog.selectedFiles()
    print(fileName[0])