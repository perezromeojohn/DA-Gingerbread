import cv2
import numpy as np
import pyautogui
import pydirectinput
import time
from main import detect_elements, press_keys, capture_pattern, wait_for_checkmark_cycle, is_rewards_screen, claim_rewards

BLUE_BAR_REGION = (1401, 131, 121, 51)

BLUE_BAR_COLOR = {
    'lower': np.array([85, 100, 100]),
    'upper': np.array([110, 255, 255])
}
BLUE_THRESHOLD = 100


def is_outside_game():
    screenshot = pyautogui.screenshot(region=BLUE_BAR_REGION)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask_blue = cv2.inRange(hsv, BLUE_BAR_COLOR['lower'], BLUE_BAR_COLOR['upper'])
    blue_pixels = cv2.countNonZero(mask_blue)
    return blue_pixels > BLUE_THRESHOLD


def walk_backward_until_inside():
    print("Walking backward into trigger zone...")
    while is_outside_game():
        pydirectinput.press('s', _pause=False)
        time.sleep(0.2)
    print("✓ Inside trigger zone!")


def run_pattern_game():
    print("\nWaiting 5 seconds for game countdown...")
    time.sleep(5)
    
    print("Starting pattern detection!\n")
    count = 0
    
    while True:
        if is_rewards_screen():
            claim_rewards()
            break
        
        img = capture_pattern()
        detected = detect_elements(img)
        press_keys(detected)
        
        count += 1
        print(f"Pattern {count} completed - waiting for next...")
        
        if not wait_for_checkmark_cycle():
            claim_rewards()
            break
    
    return count


def auto_loop(max_rounds=None):
    print("=== Auto Game Loop ===")
    print("Starting in 5 seconds... Alt-tab to game!")
    print("Make sure you're standing BEHIND the trigger area")
    time.sleep(5)
    
    round_num = 0
    total_patterns = 0
    start_time = time.time()
    
    try:
        while True:
            round_num += 1
            print(f"\n{'='*50}")
            print(f"ROUND {round_num}")
            print(f"{'='*50}")
            
            if is_outside_game():
                walk_backward_until_inside()
            
            patterns = run_pattern_game()
            total_patterns += patterns
            
            print(f"\n✓ Round {round_num} completed: {patterns} patterns")
            
            if max_rounds and round_num >= max_rounds:
                break
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    elapsed = time.time() - start_time
    print(f"\n{'='*50}")
    print(f"SESSION COMPLETE")
    print(f"{'='*50}")
    print(f"Rounds completed: {round_num}")
    print(f"Total patterns: {total_patterns}")
    print(f"Total time: {elapsed:.1f}s")
    if round_num > 0:
        print(f"Average per round: {elapsed/round_num:.1f}s")


if __name__ == "__main__":
    print("=== Roblox Auto Game Loop ===")
    print("\n1. Infinite loop (Ctrl+C to stop)")
    print("2. Limited rounds")
    
    choice = input("\nChoice (1/2): ")
    
    if choice == "1":
        auto_loop()
    elif choice == "2":
        rounds = input("Number of rounds: ")
        try:
            rounds = int(rounds)
            auto_loop(max_rounds=rounds)
        except:
            print("Invalid number")
    else:
        print("Invalid choice")
