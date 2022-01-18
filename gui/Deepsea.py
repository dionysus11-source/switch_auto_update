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
import logging


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
        logging.error ('Error: Creating directory. ' +  directory)
        
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


    logging.error("복사할 usb 드라이브를 선택하십시오")
    logging.error("==== 현재 연결된 usb 목록 ====")
    for index, value in enumerate(usb_device):
        logging.error(str(index) + ": " + value)
    input_cnt = len(usb_device)
    logging.error(str(input_cnt) + ": 종료" )
    while True:
        drive = input()
        int_drive = int(drive)
        if (int_drive == input_cnt):
            sys.exit()
        if ((int_drive >=0) and (int_drive < input_cnt)):
            return usb_device[int_drive]
        logging.error("잘못된 값을 입력하였습니다.")

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

def run(target_usb_device, progress_bar):
    downloadlist = ['https://github.com/Team-Neptune/DeepSea/releases','https://github.com/ITotalJustice/patches/releases','https://github.com/Atmosphere-NX/Atmosphere/releases']
    keywordlist = ['normal','fusee.zip', 'fusee.bin']
    logging.error('설치할 파일을 다운로드 중입니다.')
    progress_bar.setValue(10)
    copy_file_list = []
    for i in range(len(downloadlist)):
      copy_file_list.append(download_url(downloadlist[i], keywordlist[i]))

    logging.error('다운로드가 완료 되었습니다.')
    logging.error('===Download list====')
    for file in copy_file_list:
        logging.error(file)
    progress_bar.setValue(50)

    folder_name = datetime.datetime.now().strftime('%Y-%m-%d')
    extract_zip(folder_name, copy_file_list)
    modify_ini_file(folder_name)
    progress_bar.setValue(80)
    copy_files(folder_name, target_usb_device)
    ("모든 복사가 끝났습니다. 다음에 할일")
    logging.error("=========================================================================================")
    logging.error("1. 리커버리 모드 진입 : 볼륨 업 + 전원 + 지그")
    logging.error("2. TegraRCM GUI 실행 후 usb드라이브 최상위 폴더를 찾아보면 hekae_ctcaer_x.bin 을 넣을 파일로 선택")
    logging.error("3. Inject payload 클릭하여 Hekate 부팅 후 첫번째 아이콘 선택")
    logging.error("=========================================================================================")

def modify_ini_file(folder_name):
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
