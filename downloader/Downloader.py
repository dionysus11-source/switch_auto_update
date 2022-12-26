import requests
import zipfile
import os
from subprocess import check_output, CalledProcessError
import shutil
import datetime
import sys
import wmi
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject

class Downloader(QObject):
    print_message = pyqtSignal(str)
    def __init__(self,download_list):
        super().__init__()
        if type(download_list) is list:
            self.__download_list = download_list
        else:
            raise Exception('Type must be list')
    def download(self, url, file_name):
        with open(file_name, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

    def download_url(self, url):
        header = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"}
        r = requests.get(url, headers=header)
        target_link = r.json()['assets'][0]['browser_download_url']
        target_filename = target_link.split('/')[-1]
        self.download(target_link,target_filename)
        return target_filename

    def createFolder(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            self.print_message.emit('Error: Creating directory. ' +  directory)
        
    def recursive_overwrite(self, src, dest, ignore=None):
        if os.path.isdir(src):
            if not os.path.isdir(dest):
                os.makedirs(dest)
            files = os.listdir(src)
            if ignore is not None:
                ignored = ignore(src, files)
            else:
                ignored = set()
            for f in files:
                if f not in ignored:
                    self.recursive_overwrite(os.path.join(src, f), 
                                    os.path.join(dest, f), 
                                    ignore)
        else:
            shutil.copyfile(src, dest)

    def select_usb_drive(self):
        c = wmi.WMI()
        usb_device = []
        for disk in c.Win32_LogicalDisk():
            if disk.Description == '이동식 디스크':
                usb_device.append(disk.DeviceID )


        self.print_message.emit("복사할 usb 드라이브를 선택하십시오")
        self.print_message.emit("==== 현재 연결된 usb 목록 ====")
        for index, value in enumerate(usb_device):
            self.print_message.emit(str(index) + ": " + value)
        input_cnt = len(usb_device)
        self.print_message.emit(str(input_cnt) + ": 종료" )
        while True:
            drive = input()
            int_drive = int(drive)
            if (int_drive == input_cnt):
                sys.exit()
            if ((int_drive >=0) and (int_drive < input_cnt)):
                return usb_device[int_drive]
            self.print_message.emit("잘못된 값을 입력하였습니다.")

    def extract_zip(self, folder_name, files):
        cwd = os.getcwd()
        folder_name = datetime.datetime.now().strftime('%Y-%m-%d')
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)
        self.createFolder(folder_name)
        for copy_file in files:
            if 'bin' in copy_file:
                shutil.move(copy_file, './' + folder_name + '/bootloader/payloads')
            else:
                fantasy_zip = zipfile.ZipFile(copy_file)
                fantasy_zip.extractall(cwd + '\\'+folder_name) 
                fantasy_zip.close()

    def copy_files(self, src, dst):
        self.recursive_overwrite('./'+ src, dst)

    def run(self, target_usb_device, progress_bar):
    #downloadlist = ['https://api.github.com/repos/THZoria/AtmoPack-Vanilla/releases/latest','https://api.github.com/repos/CTCaer/hekate/releases/latest']
        self.print_message.emit('설치할 파일을 다운로드 중입니다.')
        progress_bar.setValue(10)
        copy_file_list = []
        for i in range(len(self.__download_list)):
            copy_file_list.append(self.download_url(self.__download_list[i]))
        print(copy_file_list)
        self.print_message.emit('다운로드가 완료 되었습니다.')
        self.print_message.emit('===Download list====')
        for file in copy_file_list:
            self.print_message.emit(file)
        progress_bar.setValue(50)

        folder_name = datetime.datetime.now().strftime('%Y-%m-%d')
        self.extract_zip(folder_name, copy_file_list)
        #modify_ini_file(folder_name)
        progress_bar.setValue(80)
        self.copy_files(folder_name, target_usb_device)
        for copy_file in copy_file_list:
            if 'bin' in copy_file:
                continue
            else:
                os.remove(copy_file)
        self.print_message.emit("모든 복사가 끝났습니다. 다음에 할일")
        self.print_message.emit("=========================================================================================")
        self.print_message.emit("1. 리커버리 모드 진입 : 볼륨 업 + 전원 길게 누르기")
        self.print_message.emit("2. 컴퓨터에 usb 연결 후 TegraRCM GUI 실행")
        self.print_message.emit("3. 폴더 모양 아이콘 클릭 후 hekate_ctcaer_x.bin 선택 (날짜 폴더(ex. 2022-12-12)를 찾아보면 최신 hekae_ctcaer_x.bin가 있음)")
        self.print_message.emit("4. Inject payload 클릭하여 Hekate 부팅 후 나타나는 스위치 그림에서 세번째 아이콘(Payloads) 선택 -> fusee.bin 선택")
        self.print_message.emit("=========================================================================================")

    def modify_ini_file(self, folder_name):
        ini_file = folder_name + '/bootloader/hekate_ipl.ini'
        cwd = os.getcwd()
        with open(cwd + '\\'+ini_file, 'r') as f:
            lines = f.readlines()
            del_lines=[]
            for idx, line in enumerate(lines):
                if 'SYSNAND' in line:
                    del_lines.append(idx+1)
                if 'EMUMMC' in line:
                    del_lines.append(idx-2)
                    break
            del lines[del_lines[0]:del_lines[1]]
            lines.insert(del_lines[0], 'payload=bootloader/payloads/fusee.bin\n')
        with open(cwd + '\\'+ini_file, 'w') as f:
            f.writelines(lines)