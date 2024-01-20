import cv2
import pytesseract
import re
import pyautogui
import time

# Capture a screenshot
screenshot = pyautogui.screenshot()
screenshot.save('screendump_org.png')

# Load the screenshot image using OpenCV
image = cv2.imread('screendump_org.png')

# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Use any necessary preprocessing techniques (e.g., thresholding, noise reduction)

# Perform OCR using Tesseract
activation_code = pytesseract.image_to_string(gray_image)

# Define a regular expression pattern to find "OSiispiay" followed by 8 digits
pattern = r"OSiispiay\s+(\d{8})"

# Search for the pattern in the OCR result
match = re.search(pattern, activation_code)

if match:
    detected_code = match.group(1)
    print("Detected Activation Code:", detected_code)
else:
    print("Activation code not found in the OCR result.")
