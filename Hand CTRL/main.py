import ctypes
import cv2
import mediapipe as mp
import numpy as np
import time
import os
from datetime import datetime
import pyautogui

pyautogui.FAILSAFE = False

class HandImageCapture:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.last_action_time = 0
        self.cooldown = 2

    def is_finger_up(self, lm, tip, pip):
        return lm[tip].y < lm[pip].y

    def is_finger_down(self, lm, tip, pip):
        return lm[tip].y > lm[pip].y

    def is_thumb_up(self, lm):
        return lm[4].x < lm[3].x and lm[4].y < lm[3].y

    def is_fist(self, lm):
        return all(lm[tip].y > lm[tip - 2].y for tip in [8, 12, 16, 20])

    def is_peace_sign(self, lm):
        return (
            lm[8].y < lm[6].y and
            lm[12].y < lm[10].y and
            lm[16].y > lm[14].y and
            lm[20].y > lm[18].y
        )

    def is_only_index_up(self, lm):
        return (
            lm[8].y < lm[6].y and
            all(lm[i].y > lm[i - 2].y for i in [12, 16, 20])
        )

    def get_ring_finger_direction(self, lm):
        if self.is_finger_up(lm, 16, 14):
            return "up"
        elif self.is_finger_down(lm, 16, 14):
            return "down"
        return "neutral"

    def handle_gestures(self, landmarks):
        now = time.time()
        if now - self.last_action_time < self.cooldown:
            return

        ring_dir = self.get_ring_finger_direction(landmarks)
        if ring_dir == "up":
            pyautogui.press("volumeup")
            self.last_action_time = now
        elif ring_dir == "down":
            pyautogui.press("volumedown")
            self.last_action_time = now

        if self.is_thumb_up(landmarks):
            ctypes.windll.user32.LockWorkStation()
            self.last_action_time = now

        if self.is_fist(landmarks):
            pyautogui.hotkey("win", "d")
            self.last_action_time = now

        if self.is_peace_sign(landmarks):
            pyautogui.hotkey("ctrl", "alt", "delete")
            self.last_action_time = now

        if self.is_only_index_up(landmarks):
            pyautogui.moveRel(0, -20)
            self.last_action_time = now

    def start(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
            image = cv2.flip(image, 1)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    lm = hand_landmarks.landmark
                    self.handle_gestures(lm)

            cv2.imshow("Gesture Control", image)
            key = cv2.waitKey(1)
            if key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = HandImageCapture()
    app.start()
