import requests
from bs4 import BeautifulSoup
import lxml
import zipfile
import os
from glob import glob
from subprocess import check_output, CalledProcessError
import shutil
import datetime
import sys
import wmi


def download(url, file_name):
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)

def download_url(url, target):
    header = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"}
    r = requests.get(url, headers=header)
    bs = BeautifulSoup(r.content,'lxml')
    links = bs.select('a')
    base_link='https://github.com/'
    for link in links:
        if target in link.attrs['href']:
            target_link = base_link + link.attrs['href']
            target_filename = target_link.split('/')[-1]
            break
    download(target_link,target_filename)
    return target_filename

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
        
def recursive_overwrite(src, dest, ignore=None):
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
                recursive_overwrite(os.path.join(src, f), 
                                    os.path.join(dest, f), 
                                    ignore)
    else:
        shutil.copyfile(src, dest)

def select_usb_drive():
    c = wmi.WMI()
    usb_device = []
    for disk in c.Win32_LogicalDisk():
        if disk.Description == '이동식 디스크':
            usb_device.append(disk.DeviceID )


    print("복사할 usb 드라이브를 선택하십시오")
    print("==== 현재 연결된 usb 목록 ====")
    for index, value in enumerate(usb_device):
        print(str(index) + ": " + value)
    input_cnt = len(usb_device)
    print(str(input_cnt) + ": 종료" )
    while True:
        drive = input()
        int_drive = int(drive)
        if (int_drive == input_cnt):
            sys.exit()
        if ((int_drive >=0) and (int_drive < input_cnt)):
            return usb_device[int_drive]
        print("잘못된 값을 입력하였습니다.")

def extract_zip(folder_name, files):
    cwd = os.getcwd()
    folder_name = datetime.datetime.now().strftime('%Y-%m-%d')
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    createFolder(folder_name)
    for copy_file in files:
        if 'bin' in copy_file:
            shutil.move(copy_file, './' + folder_name + '/bootloader/payloads')
        else:
            fantasy_zip = zipfile.ZipFile(copy_file)
            fantasy_zip.extractall(cwd + '\\'+folder_name) 
            fantasy_zip.close()

def copy_files(src, dst):
    recursive_overwrite('./'+ src, dst)

downloadlist = ['https://github.com/Team-Neptune/DeepSea/releases','https://github.com/ITotalJustice/patches/releases','https://github.com/Atmosphere-NX/Atmosphere/releases']
keywordlist = ['normal','fusee.zip', 'fusee.bin']
print('설치할 파일을 다운로드 중입니다.')
copy_file_list = []
for i in range(len(downloadlist)):
  copy_file_list.append(download_url(downloadlist[i], keywordlist[i]))

print('다운로드가 완료 되었습니다.')
print('===Download list====')
for file in copy_file_list:
    print(file)

target_usb_device = select_usb_drive()
folder_name = datetime.datetime.now().strftime('%Y-%m-%d')
extract_zip(folder_name, copy_file_list)
copy_files(folder_name, target_usb_device)