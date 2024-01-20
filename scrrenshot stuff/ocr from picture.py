import cv2
import pytesseract

# Load the image using OpenCV
image = cv2.imread('screendump_org.png')

# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Use any necessary preprocessing techniques (e.g., thresholding, noise reduction)

# Perform OCR using Tesseract
activation_code = pytesseract.image_to_string(gray_image)

# Print the detected activation code
print("Detected Activation Code:", activation_code)

