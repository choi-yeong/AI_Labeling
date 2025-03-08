import win32gui
import win32con
import cv2
import numpy as np
import time
import screeninfo
from mss import mss
from ultralytics import YOLO
import pyautogui
import math

# 훈련된 모델 로드
model = YOLO("runs/detect/train4/weights/best.pt")

# 게임 창 설정
game_window_title = "MapleStory Worlds-Mapleland (빅토리아)"
monitors = screeninfo.get_monitors()

if len(monitors) < 2:
    print("2번째 모니터가 없습니다.")
    exit()
else:
    print("2번째 모니터가 감지되어, 게임화면을 2번째 모니터로 옮깁니다.")
    second_monitor = monitors[1]
    monitor_width = second_monitor.width
    monitor_x = second_monitor.x

hwnd = win32gui.FindWindow(None, game_window_title)
if not hwnd:
    print("게임 창을 찾을 수 없습니다.")
    exit()

def active_window(hwnd):
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    window_width = 1026
    window_height = 566
    x_pos = monitor_x + monitor_width - window_width + 10
    y_pos = 0
    win32gui.MoveWindow(hwnd, x_pos, y_pos, window_width, window_height, True)
    time.sleep(1)
    return x_pos, y_pos, window_width, window_height

# 두 번째 모니터로 게임 창 이동
x_pos, y_pos, width, height = active_window(hwnd)
print(f"캡처 영역: x={x_pos}, y={y_pos}, width={width}, height={height}")

def get_window_rect(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x_pos, y_pos, x_end, y_end = rect
    width = x_end - x_pos
    height = y_end - y_pos
    return {"left": x_pos, "top": y_pos, "width": width, "height": height}

sct = mss()
monitor = get_window_rect(hwnd)

# 사거리 (픽셀 단위, 게임에 맞게 조정 필요)
ATTACK_RANGE = 260  # 100px 이내로 공격

while True:
    # 화면 캡처
    screenshot = sct.grab(monitor)
    frame = np.array(screenshot)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

    # YOLOv8로 예측
    results = model.predict(frame_rgb, conf=0.5)
    me_center = None  # "me"의 중앙 좌표
    pig_centers = []  # "pig"의 중앙 좌표 목록

    for result in results:
        boxes = result.boxes.xyxy
        confidences = result.boxes.conf
        classes = result.boxes.cls
        for box, conf, cls in zip(boxes, confidences, classes):
            class_name = ["me", "pig"][int(cls)]
            if conf > 0.5:
                x1, y1, x2, y2 = map(int, box)
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                cv2.rectangle(frame_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame_rgb, f"{class_name}: {conf:.2f}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                if class_name == "me":
                    me_center = (center_x, center_y)
                elif class_name == "pig":
                    pig_centers.append((center_x, center_y))

    # "me"와 "pig" 간 거리 계산 및 방향별 공격
    if me_center and pig_centers:
        for pig_center in pig_centers:
            distance = math.sqrt((me_center[0] - pig_center[0])**2 + (me_center[1] - pig_center[1])**2)
            if distance <= ATTACK_RANGE:
                if pig_center[0] < me_center[0]:  # pig가 왼쪽에 있으면
                    pyautogui.press('left')
                    time.sleep(0.1)  # 방향키 후 간격
                    pyautogui.press('ctrlleft')
                    print(f"거리: {distance:.2f}px - 돼지가 왼쪽! 왼쪽으로 방향 전환 후 공격 실행!")
                elif pig_center[0] > me_center[0]:  # pig가 오른쪽에 있으면
                    pyautogui.press('right')
                    time.sleep(0.1)  # 방향키 후 간격
                    pyautogui.press('ctrlleft')
                    print(f"거리: {distance:.2f}px - 돼지가 오른쪽! 오른쪽으로 방향 전환 후 공격 실행!")

    # 화면 표시 시도 (GUI 오류 무시)
    try:
        cv2.imshow("Game Screen with Detection", frame_rgb)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except cv2.error:
        print("GUI 표시가 지원되지 않습니다. 이미지를 확인하세요.")
        time.sleep(0.1)  # 0.1초 대기

cv2.destroyAllWindows()