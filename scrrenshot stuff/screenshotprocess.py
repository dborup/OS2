import subprocess
import cv2
import pytesseract
import re
import os

# Set the XAUTHORITY and DISPLAY environment variables
os.environ["XAUTHORITY"] = "/home/chrome/.Xauthority"
os.environ["DISPLAY"] = ":0"

# Capture a screenshot using scrot (you can remove this if the screenshot is already available)
subprocess.run(["scrot", "screendump_org.png", "-o", "-d", "2", "-q", "10"])

# Load the image using OpenCV
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
    
    # Log the activation code to syslog
    subprocess.run(["logger", "-p", "local0.info", "-t", "os2displayactivationcode", detected_code])
    
else:
    print("Activation code not found in the OCR result.")
