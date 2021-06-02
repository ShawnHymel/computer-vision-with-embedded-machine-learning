"""
OpenMV Image Capture

Displays image in viewport in IDE. Counts down and saves image. Restart program to take multiple
photos.

Author: EdgeImpulse, Inc.
Date: June 2, 2021
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import sensor
import image
import time

# Settings
save_path = "/"                         # Save images to root directory
file_num = 0                            # Starting point for filename
file_suffix = ".bmp"                    # Extension for image file
countdown = 3                           # Seconds to count down from
countdown_delay = 1000                  # Milliseconds
width = 160                             # Width of frame (pixels)
height = 160                            # Height of frame (pixels)

####################################################################################################
# Functions

def file_exists(filepath):
    """
    Returns true if file exists, false otherwise
    """
    try:
        f = open(filepath, 'r')
        exists = True
        f.close()
    except:
        exists = False
    return exists


def get_filepath():
    """
    Returns the next available full path to image file
    """

    global file_num

    # Loop through possible file numbers to see if that file already exists
    filepath = save_path + str(file_num) + file_suffix
    while file_exists(filepath):
        file_num += 1
        filepath = save_path + str(file_num) + file_suffix

    return filepath

####################################################################################################
# Main

# Configure camera
sensor.reset()
sensor.set_pixformat(sensor.RGB565)     # Set pixel format to RGB565 or GRAYSCALE
sensor.set_framesize(sensor.QVGA)       # Set frame size to QVGA (320x240)
sensor.set_windowing((width, height))   # Crop sensor frame to this resolution
sensor.skip_frames(time = 2000)         # Let the camera adjust

# Start clock (for measureing FPS)
clock = time.clock()

# Get initial timestamp
timestamp = time.ticks_ms()

# Main while loop
while(True):

    # Update timer
    clock.tick()

    # Get image from camera
    img = sensor.snapshot()

    # Do countdown
    current_time = time.ticks_ms()
    if (current_time - timestamp) >= countdown_delay:
        timestamp = current_time
        if countdown > 0:
            countdown -= 1

            # When countdown hits 0, save image and flash viewfinder black
            if countdown == 0:
                filepath = get_filepath()
                img.save(filepath)
                img.draw_rectangle(0, 0, width, height, color=(0,0,0), fill=True)
                time.sleep_ms(100)
                print("Image saved to:", filepath)

    # Draw countdown string on image
    if countdown != 0:
        img.draw_string(int(width / 2 + 0.5) - 35,
                        int(height / 2 + 0.5) - 50,
                        str(countdown),
                        scale=10.0)
