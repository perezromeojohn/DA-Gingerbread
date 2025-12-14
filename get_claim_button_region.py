import pyautogui
import time

print("=== Get Claim Button Coordinates ===")
print("\nMove mouse to center of the green 'Claim' button...")

input("Press Enter to start...")

time.sleep(3)
x, y = pyautogui.position()

print(f"\n✓ Claim button position: ({x}, {y})")
print(f"\nCopy this to main.py:")
print(f"CLAIM_BUTTON_POS = ({x}, {y})")
