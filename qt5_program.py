import sys
import os
from PyQt5.QtWidgets import *
from PyQt5 import uic
import qdarkstyle

os.environ['QT_API'] = 'pyqt5'

form_class = uic.loadUiType("switch_downloader.ui")[0]

class WindowClass(QMainWindow, form_class):
    __selected_drive = None
    def __init__(self):
        super().__init__()
        self.setupUi(self)
    
    def select_usb_drive(usb_drive):
        __selected_drive = usb_drive

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    window = WindowClass()
    window.show()
    app.exec_()