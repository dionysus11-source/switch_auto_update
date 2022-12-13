import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread
from PyQt5 import uic
import qdarkstyle
import wmi
import logging
import pythoncom
from Downloader import Downloader
import json

os.environ['QT_API'] = 'pyqt5'

form_class = uic.loadUiType("switch_downloader.ui")[0]
class LogStringHandler(logging.Handler):
    def __init__(self, target_widget):
        super(LogStringHandler, self).__init__()
        self.target_widget=target_widget 

    def emit(self, record):
        self.target_widget.append(' -- ' + record.getMessage())
        
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #self.update_usb_drive()
        self.usbSelect.currentIndexChanged.connect(self.select_usb_drive)
        self.updaterButton.clicked.connect(self.update_cfw)
        self.progressBar.setValue(0)
        logger = logging.getLogger()
        logger.addHandler(LogStringHandler(self.testTextBrowser))
        logging.error('hekate/atmosphere make program')
        x = usbThread(self,parent=self)
        x.start()
        self.select_usb_drive()

    def update_cfw(self):
        with open('download_url.json', "r") as json_file:
            downloadlist = json.load(json_file)['url']
        #downloadlist = ['https://api.github.com/repos/THZoria/AtmoPack-Vanilla/releases/latest','https://api.github.com/repos/CTCaer/hekate/releases/latest']
        dl = Downloader(downloadlist)
        self.progressBar.setValue(0)
        print(self.__selected_drive)
        if self.__selected_drive == "":
            logging.error('선택된 드라이브가 없습니다.')
            return
        dl.run(self.__selected_drive, self.progressBar)
        self.progressBar.setValue(100)
    def update_usb_drive(self):
        self.usbSelect.clear()
        self.wmi = wmi.WMI()
        usb_devices = []
        for disk in self.wmi.Win32_LogicalDisk():
            if disk.Description == '이동식 디스크':
                usb_devices.append(disk.DeviceID )
        logging.error("==== 현재 연결된 usb 목록 ====")
        for index, value in enumerate(usb_devices):
            logging.error(str(index) + ": " + value)
            self.usbSelect.addItem(value)
        if len(usb_devices) > 1:
            self.__selected_drive = self.usbSelect.currentText()


    def select_usb_drive(self):
        self.__selected_drive = self.usbSelect.currentText()
        logging.error("선택된 드라이브: " + self.__selected_drive)

class usbThread(QThread):
    def __init__(self, app,parent=None):
        super().__init__(parent)
        self.app = app
    def run(self):
        raw_wql = "SELECT * FROM __InstanceCreationEvent WITHIN 2 WHERE TargetInstance ISA \'Win32_USBHub\'"
        pythoncom.CoInitialize()
        c = wmi.WMI()
        watcher = c.watch_for(raw_wql=raw_wql)
        while 1:
            self.app.usbSelect.clear()
            usb_devices = []
            for disk in c.Win32_LogicalDisk():
                if disk.Description == '이동식 디스크':
                    usb_devices.append(disk.DeviceID )
            logging.error("==== 현재 연결된 usb 목록 ====")
            for index, value in enumerate(usb_devices):
                logging.error(str(index) + ": " + value)
                self.app.usbSelect.addItem(value)
            if len(usb_devices) > 1:
                self.__selected_drive = self.app.usbSelect.currentText()
                self.app.update_usb_drive()
            usb = watcher()
        print('thread end')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    window = WindowClass()
    window.show()
    app.exec_()


