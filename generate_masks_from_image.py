import cv2
import numpy as np
import os
import pyautogui
import time

# Color ranges in HSV for detection - PRECISE/SHARP colors only (same as main.py)
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

def generate_masks_from_screenshot(image_path):
    """Generate individual masks from a single screenshot"""
    
    # Load the image
    print(f"Loading image: {image_path}")
    img = cv2.imread(image_path)
    
    if img is None:
        print(f"ERROR: Could not load image from {image_path}")
        return
    
    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Create Masks folder if it doesn't exist
    if not os.path.exists('Masks'):
        os.makedirs('Masks')
        print("Created 'Masks' folder")
    
    print("\n" + "="*50)
    print("Generating masks for all elements...")
    print("="*50)
    
    results = {}
    
    for element in COLOR_RANGES.keys():
        # Create mask
        if element == 'red_glaze':
            mask1 = cv2.inRange(hsv, COLOR_RANGES[element]['lower1'], 
                               COLOR_RANGES[element]['upper1'])
            mask2 = cv2.inRange(hsv, COLOR_RANGES[element]['lower2'], 
                               COLOR_RANGES[element]['upper2'])
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            mask = cv2.inRange(hsv, COLOR_RANGES[element]['lower'], 
                              COLOR_RANGES[element]['upper'])
        
        # Count pixels
        pixel_count = cv2.countNonZero(mask)
        results[element] = pixel_count
        
        # Save mask
        cv2.imwrite(f'Masks/mask_{element}.png', mask)
        
        # Determine status
        if pixel_count > 100:
            status = "✓ DETECTED"
        elif pixel_count > 20:
            status = "⚠ WEAK"
        else:
            status = "✗ NOT PRESENT"
        
        print(f"{element:20} {pixel_count:6} pixels - {status}")
    
    # Save the original pattern too
    cv2.imwrite('Masks/pattern_source.png', img)
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print("Elements detected in this pattern:")
    for element, count in results.items():
        # Show elements above their actual thresholds
        thresholds = {
            'green_glaze': 1000,
            'red_glaze': 200,
            'blue_sprinkles': 100,
            'grapes': 40,
            'eyes': 60
        }
        if count >= thresholds[element]:
            print(f"  ✓ {element} ({count} pixels)")
    
    print("\nAll masks saved in 'Masks' folder!")
    print("  - mask_[element].png for each element")
    print("  - pattern_source.png (original image)")

if __name__ == "__main__":
    print("=== Generate Masks from Screenshot ===\n")
    
    print("1. Capture from screen (coordinates: 1652, 175 to 1876, 392)")
    print("2. Load from existing image file")
    
    choice = input("\nChoose option (1 or 2): ")
    
    if choice == '1':
        # Capture from screen
        print("\nCapturing pattern region in 5 seconds... Alt-tab to game!")
        time.sleep(1)
        
        # Calculate region (x, y, width, height)
        # Top-left (1652, 175) to Bottom-right (1876, 392)
        x1, y1 = 1652, 188
        x2, y2 = 1856, 390
        region = (x1, y1, x2-x1, y2-y1)  # (1652, 175, 224, 217)
        
        # Capture screenshot
        screenshot = pyautogui.screenshot(region=region)
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Save the captured image
        cv2.imwrite('captured_pattern.png', img)
        print("✓ Pattern captured and saved as 'captured_pattern.png'")
        
        # Generate masks from captured image
        generate_masks_from_screenshot('captured_pattern.png')
        
    elif choice == '2':
        # Load from file
        default_files = ['pattern_region.png', 'pattern_opencv.png', 'test_capture.png', 'captured_pattern.png']
        
        found_file = None
        for file in default_files:
            if os.path.exists(file):
                found_file = file
                break
        
        if found_file:
            print(f"Found: {found_file}")
            use_file = input(f"Use this image? (y/n): ")
            if use_file.lower() == 'y':
                generate_masks_from_screenshot(found_file)
            else:
                image_path = input("Enter image path: ")
                generate_masks_from_screenshot(image_path)
        else:
            print("No default image found.")
            image_path = input("Enter path to your screenshot: ")
            generate_masks_from_screenshot(image_path)
    else:
        print("Invalid choice")
