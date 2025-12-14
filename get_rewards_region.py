import pyautogui
import time

print("=== Get Rewards Screen Detection Region ===")
print("\nCapture a small region of the rewards screen (like part of the question mark or Claim button)")

input("Press Enter to start...")

print("\nMove mouse to TOP-LEFT of detection area...")
time.sleep(3)
x1, y1 = pyautogui.position()
print(f"✓ Top-left: ({x1}, {y1})")

print("\nMove mouse to BOTTOM-RIGHT of detection area...")
time.sleep(3)
x2, y2 = pyautogui.position()
print(f"✓ Bottom-right: ({x2}, {y2})")

width = x2 - x1
height = y2 - y1

print("\n" + "="*60)
print("Copy this to main.py:")
print("="*60)
print(f"REWARDS_SCREEN_REGION = ({x1}, {y1}, {width}, {height})")
print("="*60)
