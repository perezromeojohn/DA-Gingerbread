import pyautogui
import time

print("=== Get Region Coordinates ===")
print("\nThis will help you capture coordinates for the checkmark region")
print("\nInstructions:")
print("1. Move your mouse to the TOP-LEFT corner of the checkmark area")
print("2. Wait for the script to capture that position")
print("3. Move your mouse to the BOTTOM-RIGHT corner")
print("4. The script will calculate the region for you")

input("\nPress Enter to start...")

# Get top-left position
print("\nMove your mouse to the TOP-LEFT corner of the checkmark area...")
time.sleep(3)
x1, y1 = pyautogui.position()
print(f"✓ Top-left captured: ({x1}, {y1})")

# Get bottom-right position
print("\nNow move your mouse to the BOTTOM-RIGHT corner of the checkmark area...")
time.sleep(3)
x2, y2 = pyautogui.position()
print(f"✓ Bottom-right captured: ({x2}, {y2})")

# Calculate region
width = x2 - x1
height = y2 - y1

print(width, height)
