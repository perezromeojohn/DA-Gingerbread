import cv2
import numpy as np
import pyautogui
import pydirectinput
import time
from collections import defaultdict

# Configuration - Coordinates: Top-left (1652, 188) to Bottom-right (1856, 390)
PATTERN_REGION = (1652, 188, 204, 202)  # (x, y, width, height)
CHECKMARK_REGION = (1785, 191, 63, 65)  # (x, y, width, height)

# Keybinds
KEYBINDS = {
    'green_glaze': 'q',
    'red_glaze': 'e',
    'blue_sprinkles': 'a',
    'grapes': 's',
    'eyes': 'd'
}

# Color ranges in HSV for detection - PRECISE/SHARP colors only
COLOR_RANGES = {
    'green_glaze': {
        'lower': np.array([35, 150, 150]),   # Bright lime/neon green
        'upper': np.array([85, 255, 255])
    },
    'red_glaze': {
        'lower1': np.array([0, 180, 180]),    # Very sharp red/pink only - higher saturation
        'upper1': np.array([8, 255, 255]),
        'lower2': np.array([170, 180, 180]),  # Very sharp red/pink only - higher saturation
        'upper2': np.array([180, 255, 255])
    },
    'blue_sprinkles': {
        'lower': np.array([95, 120, 120]),    # Sharp blue/cyan dots only
        'upper': np.array([115, 255, 255])
    },
    'grapes': {
        'lower': np.array([135, 100, 100]),   # Sharp purple only
        'upper': np.array([155, 255, 255])
    },
    'eyes': {
        'lower': np.array([0, 25, 15]),       # Dark brown/chocolate spots
        'upper': np.array([30, 180, 85])      # Wider range for brown tones
    }
}

# Thresholds (minimum pixel count to consider element present)
THRESHOLDS = {
    'green_glaze': 1000,   # Needs substantial green
    'red_glaze': 200,      # Based on actual detection (was 1000, saw 288)
    'blue_sprinkles': 100,
    'grapes': 40,          # Based on actual detection (was 200, saw 52)
    'eyes': 60             # Lowered slightly to catch smaller eye spots
}

# Checkmark detection
CHECKMARK_WHITE = {
    'lower': np.array([0, 0, 200]),
    'upper': np.array([180, 30, 255])
}
WHITE_THRESHOLD = 50


def capture_pattern():
    """Capture the pattern region from screen"""
    screenshot = pyautogui.screenshot(region=PATTERN_REGION)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return img


def capture_checkmark():
    screenshot = pyautogui.screenshot(region=CHECKMARK_REGION)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return img


def is_checkmark_present():
    img = capture_checkmark()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask_white = cv2.inRange(hsv, CHECKMARK_WHITE['lower'], CHECKMARK_WHITE['upper'])
    white_pixels = cv2.countNonZero(mask_white)
    return white_pixels > WHITE_THRESHOLD


def wait_for_checkmark_cycle():
    """Wait for checkmark to appear then disappear"""
    # Wait for checkmark to appear (pattern completed)
    while not is_checkmark_present():
        time.sleep(0.05)
    
    # Wait for checkmark to disappear (new pattern ready)
    while is_checkmark_present():
        time.sleep(0.05)


def detect_elements(img):
    """Detect which elements are present in the image"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    detected = {}
    
    # Green Glaze
    mask_green = cv2.inRange(hsv, COLOR_RANGES['green_glaze']['lower'], 
                             COLOR_RANGES['green_glaze']['upper'])
    green_pixels = cv2.countNonZero(mask_green)
    detected['green_glaze'] = green_pixels > THRESHOLDS['green_glaze']
    
    # Red Glaze (handle HSV wraparound)
    mask_red1 = cv2.inRange(hsv, COLOR_RANGES['red_glaze']['lower1'], 
                            COLOR_RANGES['red_glaze']['upper1'])
    mask_red2 = cv2.inRange(hsv, COLOR_RANGES['red_glaze']['lower2'], 
                            COLOR_RANGES['red_glaze']['upper2'])
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    red_pixels = cv2.countNonZero(mask_red)
    detected['red_glaze'] = red_pixels > THRESHOLDS['red_glaze']
    
    # Blue Sprinkles
    mask_blue = cv2.inRange(hsv, COLOR_RANGES['blue_sprinkles']['lower'], 
                            COLOR_RANGES['blue_sprinkles']['upper'])
    blue_pixels = cv2.countNonZero(mask_blue)
    detected['blue_sprinkles'] = blue_pixels > THRESHOLDS['blue_sprinkles']
    
    # Grapes
    mask_grapes = cv2.inRange(hsv, COLOR_RANGES['grapes']['lower'], 
                              COLOR_RANGES['grapes']['upper'])
    grape_pixels = cv2.countNonZero(mask_grapes)
    detected['grapes'] = grape_pixels > THRESHOLDS['grapes']
    
    # Eyes
    mask_eyes = cv2.inRange(hsv, COLOR_RANGES['eyes']['lower'], 
                            COLOR_RANGES['eyes']['upper'])
    eye_pixels = cv2.countNonZero(mask_eyes)
    detected['eyes'] = eye_pixels > THRESHOLDS['eyes']
    
    # Debug: Show pixel counts
    print(f"  Pixel counts: Red={red_pixels}, Green={green_pixels}, Blue={blue_pixels}, Grapes={grape_pixels}, Eyes={eye_pixels}")
    
    # Smart glaze logic: Red and green are mutually exclusive
    # Use whichever has MORE pixels. If neither detected, default to green.
    if detected['red_glaze'] and detected['green_glaze']:
        # Both detected - use the one with more pixels
        if green_pixels > red_pixels:
            detected['red_glaze'] = False
            print(f"  → Green wins: {green_pixels} vs {red_pixels} pixels")
        else:
            detected['green_glaze'] = False
            print(f"  → Red wins: {red_pixels} vs {green_pixels} pixels")
    elif detected['red_glaze']:
        detected['green_glaze'] = False
    elif detected['green_glaze']:
        detected['red_glaze'] = False
    else:
        # Neither detected - default to green
        detected['green_glaze'] = True
        print("  → Glaze fallback: Defaulting to green glaze")
    
    return detected


def press_keys(detected_elements):
    """Press the keys for detected elements"""
    time.sleep(0.1)  # Wait for pattern to fully appear
    
    keys_to_press = []
    for element, is_present in detected_elements.items():
        if is_present:
            keys_to_press.append(KEYBINDS[element])
    
    print(f"Detected elements: {[k for k, v in detected_elements.items() if v]}")
    print(f"Pressing keys: {keys_to_press}")
    
    for key in keys_to_press:
        pydirectinput.press(key)
        time.sleep(0.05)  # Small delay between keypresses


def test_detection():
    """Test detection on current screen (for calibration)"""
    print("Testing detection in 3 seconds... Alt-tab to game!")
    time.sleep(3)
    
    img = capture_pattern()
    cv2.imwrite('test_capture.png', img)
    
    detected = detect_elements(img)
    
    print("\n=== Detection Results ===")
    for element, is_present in detected.items():
        status = "✓ DETECTED" if is_present else "✗ Not detected"
        print(f"{element}: {status}")


def run_automation(duration_seconds=60):
    """Run the automation loop"""
    print(f"Starting automation in 5 seconds... Alt-tab to game!")
    print(f"Will run for {duration_seconds} seconds")
    print("Press Ctrl+C to stop early")
    time.sleep(5)
    
    start_time = time.time()
    count = 0
    
    try:
        while time.time() - start_time < duration_seconds:
            img = capture_pattern()
            detected = detect_elements(img)
            press_keys(detected)
            
            count += 1
            print(f"Pattern {count} completed - waiting for next...")
            
            # Wait for checkmark cycle instead of fixed timing
            wait_for_checkmark_cycle()
    
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    print(f"\nCompleted {count} patterns in {time.time() - start_time:.1f} seconds")


if __name__ == "__main__":
    print("=== Roblox Pattern Automation ===")
    print("Color ranges calibrated from Masks folder")
    print("\nPress 1 to start automation (or any other key to exit)")
    
    choice = input("\nChoice: ")
    
    if choice == "1":
        duration = input("Run for how many seconds? (default 60): ")
        try:
            duration = int(duration) if duration else 60
        except:
            duration = 60
        
        run_automation(duration)
    else:
        print("Exiting...")