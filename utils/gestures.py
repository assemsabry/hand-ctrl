import ctypes
import pyautogui

class GestureController:
    def __init__(self):
        self.last_action_time = 0
        self.cooldown = 1

    def is_fist(self, landmarks):
        return all(landmarks[i].y > landmarks[i - 2].y for i in [8, 12, 16, 20])

    def is_peace_sign(self, landmarks):
        return (
            landmarks[8].y < landmarks[6].y and
            landmarks[12].y < landmarks[10].y and
            landmarks[16].y > landmarks[14].y and
            landmarks[20].y > landmarks[18].y
        )

    def is_index_up_only(self, landmarks):
        return (
            landmarks[8].y < landmarks[6].y and
            all(landmarks[i].y > landmarks[i - 2].y for i in [12, 16, 20])
        )

    def is_thumb_up(self, landmarks):
        return landmarks[4].y < landmarks[3].y and abs(landmarks[4].x - landmarks[3].x) < 0.1

    def is_palm_open(self, landmarks):
        return all(landmarks[i].y < landmarks[i - 2].y for i in [8, 12, 16, 20])

    def get_finger_direction(self, landmarks, tip, pip):
        if landmarks[tip].y < landmarks[pip].y:
            return "up"
        elif landmarks[tip].y > landmarks[pip].y:
            return "down"
        return "neutral"

    def control_by_gesture(self, landmarks, time):
        if time - self.last_action_time < self.cooldown:
            return

        ring_dir = self.get_finger_direction(landmarks, 16, 14)
        if ring_dir == "up":
            pyautogui.press("volumeup")
            self.last_action_time = time
        elif ring_dir == "down":
            pyautogui.press("volumedown")
            self.last_action_time = time

        if self.is_fist(landmarks):
            ctypes.windll.user32.LockWorkStation()
            self.last_action_time = time

        if self.is_peace_sign(landmarks):
            pyautogui.hotkey("ctrl", "alt", "delete")
            self.last_action_time = time

        if self.is_index_up_only(landmarks):
            pyautogui.moveRel(0, -30)
            self.last_action_time = time

        if self.is_thumb_up(landmarks):
            pyautogui.hotkey("win", "d")
            self.last_action_time = time

        if self.is_palm_open(landmarks):
            pyautogui.hotkey("win", "tab")
            self.last_action_time = time
