# 💬READ ME : 사용 전 읽어주세요.
> 데이터라벨링 프리랜서를 지원하기 위한 roboflow 사용 경험을 기술한 프로젝트로서 '메이플랜드'게임은 더이상 플레이하지 않습니다. 이 프로젝트로 타 유저에게 피해를 주지마세요.

# 🔨기술 개요
## 데이타 라벨링
### 몬스터와 캐릭터 인식
![roboflow](https://github.com/choi-yeong/AI_Labeling/blob/main/DATA/Label.gif)

* ROBOFLOW를 통해 약 66장의 스크린샷으로 부터 돼지(pig)와 내캐릭터(me)를 라벨링하여 A.I에게 인식


![mobsearch](https://github.com/choi-yeong/AI_Labeling/blob/main/DATA/M2.gif)


* 지형에 가려진 몬스터의 일부분도 인식할 수 있게 됨.

### Tkinter 및 멀티쓰레드
![mobsearch2](https://github.com/choi-yeong/AI_Labeling/blob/main/DATA/m1.gif)

* Tkinter창을 통해 구현된 설정창으로 현재 HP와 MP의 픽셀을 감지하여 RGB(177,177,177)가 되면 포션을 사용하도록 설정함.
* Tkinter창과 mss창은 같은 쓰레드로 사용시 mss창이 멈추는 현상이 발생하여 멀티쓰레드를 사용함.
```
# UI와 캡처 스레드 실행
ui_thread = threading.Thread(target=run_ui, daemon=True)
capture_thread = threading.Thread(target=run_combined)
```
- 여기서 tkinter창은 옵션창이므로 화면캡쳐를 종료할때 같이 종료되도록 daemon=True로 서브설정 완료.


# 🔨종합적인 기술 스택
```
* 프로그래밍: Python
* GUI: Tkinter
* 컴퓨터 비전: OpenCV, NumPy, YOLOv8 (Ultralytics)
* 화면 캡처: mss, Screeninfo
* 윈도우 제어: PyWin32 (win32gui, win32con)
* 입력 자동화: PyAutoGUI
* 멀티스레딩: Threading
* 파일/시간 관리: os, time
```



# 패치노트
## 2025년 03월 08일 16시
### 💪best.pt 버전 2 사용
* 더 확실하게 내 캐릭터와 타유저 캐릭터를 구분하게 됨.
* 더 확실하게 돼지 몬스터를 찾게 됨.

### 🎞README용 GIF파일 첨부
* 트리구조 첨부
* GIF 첨부
* 사용기술 설명
* 개발과정 기술
* 깃허브 비공개 &rarr; 공개 변경

## 2025년 02월 24일 01시
### 📽실시간 화면캡처 모니터링 구현
* 해당 기능으로 캡쳐될 HP,MP,미니맵을 확인 가능.
* 코드수정 및 버그개선에 도움이 될 예정
* 중복된 코드 제거 (trainer, haarcascade 등 파일을 2번 불러오고 있었음.)

### 🥤HP,MP 자동회복 물약사용 기능 구현
* HP와 MP를 회복할 구간을 설정하면 설정한 구간 이하로 %가 내려갈시 자동으로 물약을 사용함.
* 물약의 위치는 HP는 Home키이고, MP는 PageUp키에 둬야함.
* 입는 피해량(damage)보다 회복량이 큰 물약을 세팅해두는걸 추천함.(한번밖에 안 마심.)
