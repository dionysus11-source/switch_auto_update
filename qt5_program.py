import sys
import os
from PyQt5.QtWidgets import *
from PyQt5 import uic
import qdarkstyle
import wmi
import Deepsea
import updater

os.environ['QT_API'] = 'pyqt5'

form_class = uic.loadUiType("switch_downloader.ui")[0]

class WindowClass(QMainWindow, form_class):
    __selected_drive = None
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.update_usb_drive()
        self.usbSelect.currentIndexChanged.connect(self.select_usb_drive)
        self.deepseaButton.clicked.connect(self.deepsea_first)
        self.updaterButton.clicked.connect(self.update_cfw)
    

    def deepsea_first(self):
        self.progressBar.setValue(0)
        if self.__selected_drive is None:
            print('선택된 드라이브가 없습니다.')
            return
        Deepsea.run(self.__selected_drive, self.progressBar)
        self.progressBar.setValue(100)
    def update_cfw(self):
        self.progressBar.setValue(0)
        if self.__selected_drive is None:
            print('선택된 드라이브가 없습니다.')
            return
        updater.run(self.__selected_drive, self.progressBar)
        self.progressBar.setValue(100)
    def update_usb_drive(self):
        self.usbSelect.clear()
        c = wmi.WMI()
        usb_devices = []
        for disk in c.Win32_LogicalDisk():
            if disk.Description == '이동식 디스크':
                usb_devices.append(disk.DeviceID )
        print("==== 현재 연결된 usb 목록 ====")
        for index, value in enumerate(usb_devices):
            print(str(index) + ": " + value)
            self.usbSelect.addItem(value)
        if len(usb_devices) > 1:
            self.__selected_drive = self.usbSelect.currentText()


    def select_usb_drive(self):
        self.__selected_drive = self.usbSelect.currentText()
        print("선택된 드라이브: " + self.__selected_drive)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    window = WindowClass()
    window.show()
    app.exec_()