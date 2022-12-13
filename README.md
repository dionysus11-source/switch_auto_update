# switch_auto_update

Tool for making atmosphere/hekate booting SD card.

## How to use

1. 마이크로 sd를 usb 리더기에 넣은 후 pc에 연결합니다.

2. 프로그램을 실행

3. pc에 연결한 usb 드라이버 선택

4. 처음 사용자인 경우 "Update hekate/atmospere' 클릭

![SWITCH_AUTO](https://user-images.githubusercontent.com/52480056/207198477-1716eb6e-f5d7-4ec1-a243-81ebd41d34b8.gif)

5. usb를 뽑고 sd 카드를 스위치에 넣는다

6. 리커버리 모드 진입 : 지그 장착 후 볼륨 업 + 전원 길게 누른 이후 TegraRCM GUI.EXE 실행 

7. TegraRCM Gui에서 최신 버전 hekae_ctcaer_x.bin을 선택 후 Inject payload 클릭하여 Hekate로 부팅

**최신버전 BIN 파일은 프로그램을 실행시킨 폴더에 날짜 이름의 폴더 하위에 있음**
<img width="630" alt="HEKATE_1" src="https://user-images.githubusercontent.com/52480056/207199026-02603355-590f-4ade-b913-27a312413cbc.PNG">


8. 부팅 이후의 세번째 아이콘 - payloads 클릭-> fusee.bin 선택하여 부팅

---------------------------------------------------------------------------------


1. Insert usd drive including micro sd card

2. run program

3. select usb driver

4. if you are first user, select "Make Deepsea Firsttime", just for update, select "Update hekate/atmospere'

5. after copy is completed, follow guide in text viewer
