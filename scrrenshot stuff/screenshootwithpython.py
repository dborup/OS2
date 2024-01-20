import os
from PIL import ImageGrab

# Set the XAUTHORITY and DISPLAY environment variables
os.environ["XAUTHORITY"] = "/home/chrome/.Xauthority"
os.environ["DISPLAY"] = ":0"

# Capture a screenshot
screenshot = ImageGrab.grab()

# Save the screenshot as a file
screenshot.save("screendump_org.png")

print("Screenshot saved as screendump_org.png")
