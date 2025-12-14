import cv2
import numpy as np
import pyautogui
import time
import os

CHECKMARK_REGION = (1785, 191, 63, 65)

CHECKMARK_WHITE = {
    'lower': np.array([0, 0, 200]),
    'upper': np.array([180, 30, 255])
}

WHITE_THRESHOLD = 50


def capture_checkmark_region():
    screenshot = pyautogui.screenshot(region=CHECKMARK_REGION)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return img


def detect_checkmark(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask_white = cv2.inRange(hsv, CHECKMARK_WHITE['lower'], CHECKMARK_WHITE['upper'])
    white_pixels = cv2.countNonZero(mask_white)
    is_present = white_pixels > WHITE_THRESHOLD
    return is_present, white_pixels


def run_detection():
    print("Starting detection in 3 seconds...")
    time.sleep(3)
    
    if not os.path.exists('checkmark_captures'):
        os.makedirs('checkmark_captures')
    
    print("MONITORING - Press Ctrl+C to stop\n")
    
    previous_state = None
    
    try:
        while True:
            img = capture_checkmark_region()
            is_present, white_px = detect_checkmark(img)
            
            if is_present != previous_state:
                timestamp = time.strftime("%H%M%S")
                
                if is_present:
                    filename = f"checkmark_captures/appeared_{timestamp}.png"
                    cv2.imwrite(filename, img)
                    print(f"[{time.strftime('%H:%M:%S')}] ✓ APPEARED (White: {white_px})")
                else:
                    filename = f"checkmark_captures/disappeared_{timestamp}.png"
                    cv2.imwrite(filename, img)
                    print(f"[{time.strftime('%H:%M:%S')}] ✗ DISAPPEARED (White: {white_px})")
                    print("    → TRIGGER: Next pattern")
                
                previous_state = is_present
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopped")


if __name__ == "__main__":
    run_detection()
