#!/usr/bin/env bash
export XAUTHORITY=/home/chrome/.Xauthority
export DISPLAY=:0

# Capture a screenshot and save it as a temporary image file
screenshot_file="screendump_org.png"
scrot "$screenshot_file" -o -d 2 -q 10 

# Crop the screenshot to 416x544 pixels
convert "$screenshot_file" -crop 416x544+0+0 screendump.png

# Annotate the cropped screenshot with a timestamp
convert screendump.png -pointsize 24 -fill white -undercolor '#00000080' -gravity SouthEast -annotate +0+5 "$(date)" screendump_annotated.png

# Encode the annotated screenshot to Base64
#base64_data=$(base64 -w 0 screendump_annotated.png)

# Log the Base64 encoded screenshot to syslog
#logger -p local0.info -t screendump "$base64_data"

#echo "Screenshot data (Base64) has been written to syslog."
