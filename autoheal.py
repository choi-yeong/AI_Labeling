import win32gui
import win32con
import cv2
import numpy as np
import time
import screeninfo
import pyautogui
import tkinter as tk
from tkinter import ttk
import threading
from mss import mss
import os

# 전역 변수로 퍼센트 및 상태 관리
hp_threshold = 50
mp_threshold = 50
auto_hp = False  # HP 자동 물약 사용 여부
auto_mp = False  # MP 자동 물약 사용 여부
save_screenshots = False  # 스크린샷 저장 여부
last_screenshot_time = 0  # 마지막 스크린샷 저장 시간

# screenshot 폴더 생성
screenshot_dir = "screenshots"
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

# Tkinter UI (항상 열려있음)
def run_ui():
    global hp_threshold, mp_threshold, auto_hp, auto_mp, save_screenshots
    root = tk.Tk()
    root.title("연습용 윈도우")
    root.geometry("300x500")

    # HP 설정
    tk.Label(root, text="HP 회복 퍼센트 (0-100):").pack(pady=5)
    hp_entry = ttk.Entry(root)
    hp_entry.insert(0, str(hp_threshold))
    hp_entry.pack()
    hp_var = tk.BooleanVar()
    hp_checkbox = ttk.Checkbutton(root, text="자동HP물약", variable=hp_var, 
                                  command=lambda: toggle_auto_hp(hp_var.get()))
    hp_checkbox.pack(pady=5)

    # MP 설정
    tk.Label(root, text="MP 회복 퍼센트 (0-100):").pack(pady=5)
    mp_entry = ttk.Entry(root)
    mp_entry.insert(0, str(mp_threshold))
    mp_entry.pack()
    mp_var = tk.BooleanVar()
    mp_checkbox = ttk.Checkbutton(root, text="자동MP물약", variable=mp_var, 
                                  command=lambda: toggle_auto_mp(mp_var.get()))
    mp_checkbox.pack(pady=5)

    # 스크린샷 저장 체크박스
    screenshot_var = tk.BooleanVar()
    screenshot_checkbox = ttk.Checkbutton(root, text="스크린샷 저장 (5초 간격)", variable=screenshot_var, 
                                         command=lambda: toggle_screenshots(screenshot_var.get()))
    screenshot_checkbox.pack(pady=5)

    status_label = tk.Label(root, text="현재 설정: HP {}%, MP {}%".format(hp_threshold, mp_threshold))
    status_label.pack(pady=5)

    def toggle_auto_hp(state):
        global auto_hp, hp_threshold
        try:
            hp_val = int(hp_entry.get())
            if 0 <= hp_val <= 100:
                hp_threshold = hp_val
                auto_hp = state
                update_status(status_label)
            else:
                status_label.config(text="HP: 0~100 사이 값을 입력하세요!", fg="red")
        except ValueError:
            status_label.config(text="HP: 숫자를 입력하세요!", fg="red")

    def toggle_auto_mp(state):
        global auto_mp, mp_threshold
        try:
            mp_val = int(mp_entry.get())
            if 0 <= mp_val <= 100:
                mp_threshold = mp_val
                auto_mp = state
                update_status(status_label)
            else:
                status_label.config(text="MP: 0~100 사이 값을 입력하세요!", fg="red")
        except ValueError:
            status_label.config(text="MP: 숫자를 입력하세요!", fg="red")

    def toggle_screenshots(state):
        global save_screenshots
        save_screenshots = state
        update_status(status_label)

    def update_status(label):
        status_text = f"현재 설정: HP {hp_threshold}%{' (자동)' if auto_hp else ''}, MP {mp_threshold}%{' (자동)' if auto_mp else ''}"
        if save_screenshots:
            status_text += " | 스크린샷 저장 ON"
        label.config(text=status_text, fg="black")

    root.mainloop()

# 게임 창 설정
game_window_title = "MapleStory Worlds-Mapleland (빅토리아)"
monitors = screeninfo.get_monitors()
if len(monitors) < 2:
    print("2번째 모니터가 없습니다.")
    exit()
elif len(monitors) >= 2:
    print("2번째 모니터가 감지되어, 게임화면을 2번째 모니터로 옮깁니다.")
    second_monitor = monitors[1]
monitor_width = second_monitor.width
monitor_x = second_monitor.x

hwnd = win32gui.FindWindow(None, game_window_title)
if not hwnd:
    print("게임 창을 찾을 수 없습니다.")
    exit()

def active_window():
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    window_width = 1026
    window_height = 566
    x_pos = monitor_x + monitor_width - window_width + 10
    y_pos = 0
    win32gui.MoveWindow(hwnd, x_pos, y_pos, window_width, window_height, True)
    time.sleep(1)
    return x_pos, y_pos, window_width, window_height

# 창 활성화 및 위치 설정
x_pos, y_pos, width, height = active_window()
print(f"캡처 영역: x={x_pos}, y={y_pos}, width={width}, height={height}")

# 캡처 영역 설정
monitor = {"left": x_pos, "top": y_pos, "width": width, "height": height}

# HP, MP, 미니맵의 상대 좌표
bounding_boxes = {
    "HP": {"x": 220, "y": 540, "w": 100, "h": 12},
    "MP": {"x": 325, "y": 540, "w": 100, "h": 12},
    "Minimap": {"x": 10, "y": 35, "w": 150, "h": 200}
}

# 초기 픽셀값 저장
prev_pixels = {
    "HP": {"25": None, "50": None, "75": None},
    "MP": {"25": None, "50": None, "75": None}
}

# 타겟 RGB 값 (빈 바 색상)
target_rgb = (177, 177, 177)

# 키 입력 쿨다운
last_key_time = {"HP": 0, "MP": 0}
cooldown = 1

# 실시간 캡처 및 감지 함수
def run_capture():
    global last_screenshot_time
    sct = mss()
    while True:
        # 실시간 창 위치 업데이트
        rect = win32gui.GetWindowRect(hwnd)
        x_pos, y_pos, x_end, y_end = rect
        width = x_end - x_pos
        height = y_end - y_pos
        monitor = {"left": x_pos, "top": y_pos, "width": width, "height": height}

        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

        for label, box in bounding_boxes.items():
            if label in ["HP", "MP"]:
                x, y, w, h = box["x"], box["y"], box["w"], box["h"]
                cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame_rgb, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                y_mid = y + h // 2

                threshold = hp_threshold if label == "HP" else mp_threshold
                target_x = x + int(w * (threshold / 100))
                below_threshold = False

                for check_x in range(x, target_x + 1):
                    pixel_bgr = tuple(frame_bgr[y_mid, check_x])
                    if pixel_bgr == target_rgb:
                        below_threshold = True
                        break

                current_time = time.time()
                if below_threshold and (current_time - last_key_time[label]) > cooldown:
                    if (label == "HP" and auto_hp) or (label == "MP" and auto_mp):
                        key = 'home' if label == "HP" else 'pageup'
                        pyautogui.press(key)
                        print(f"현재 {label} : {threshold}%, 물약을 마시세요")
                        last_key_time[label] = current_time
            else:
                x, y, w, h = box["x"], box["y"], box["w"], box["h"]
                cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame_rgb, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # 스크린샷 저장 로직
        current_time = time.time()
        if save_screenshots and (current_time - last_screenshot_time) >= 5:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
            cv2.imwrite(screenshot_path, frame_rgb)  # RGB로 저장
            print(f"스크린샷 저장됨: {screenshot_path}")
            last_screenshot_time = current_time

        cv2.imshow("Game Screen", frame_rgb)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

# UI와 캡처를 별도 스레드로 실행
ui_thread = threading.Thread(target=run_ui, daemon=True)
capture_thread = threading.Thread(target=run_capture)

ui_thread.start()
capture_thread.start()
capture_thread.join()