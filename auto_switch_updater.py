import requests
from bs4 import BeautifulSoup
import lxml
import zipfile
import os
from glob import glob
from subprocess import check_output, CalledProcessError
import shutil
import datetime
import wmi
import sys

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

downloadlist = ['https://github.com/Atmosphere-NX/Atmosphere/releases', 'https://github.com/CTCaer/hekate/releases','https://github.com/Atmosphere-NX/Atmosphere/releases','https://github.com/ITotalJustice/patches/releases']
keywordlist = ['download','download','fusee.bin','fusee.zip']
print('설치할 파일을 다운로드 중입니다.')
copy_file_list = []
for i in range(len(downloadlist)):
  copy_file_list.append(download_url(downloadlist[i], keywordlist[i]))

print('다운로드가 완료 되었습니다.')
print('===Download list====')
for file in copy_file_list:
    print(file)


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
        target_usb_device = usb_device[int_drive]
        break
    print("잘못된 값을 입력하였습니다.")
print("파일을 usb 드라이브로 복사 중입니다.")
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
cwd = os.getcwd()
now = datetime.datetime.now().strftime('%Y-%m-%d')
if os.path.exists(now):
    shutil.rmtree(now)
createFolder(now)
#for copy_file in copy_file_list:
#   shutil.move(copy_file, './src')
for copy_file in copy_file_list:
    if 'bin' in copy_file:
        shutil.move(copy_file, './' + now + '/bootloader/payloads')
    else:
        fantasy_zip = zipfile.ZipFile(copy_file)
        fantasy_zip.extractall(cwd + '\\'+now) 
        fantasy_zip.close()
for copy_file in copy_file_list:
    if 'bin' in copy_file:
        continue
    else:
        os.remove(copy_file)

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
recursive_overwrite('./'+ now, target_usb_device)
print("모든 복사가 끝났습니다. 다음에 할일")
print("=========================================================================================")
print("1. 리커버리 모드 진입 : 볼륨 업 + 전원 + 지그")
print("2. TegraRCM GUI 실행 후 usb드라이브 최상후 폴더의 hekate_ctcaer_x.bin 을 넣을 파일로 선택")
print("3. Inject payload 클릭하여 Hekate 부팅 후 세번째 payloads 아이콘 클릭")
print("4. 제일 아래 fusee.bin 선택")
print("=========================================================================================")
os.system('pause')