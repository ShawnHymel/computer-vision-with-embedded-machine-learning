#!/usr/bin/env python
"""
Raspberry Pi Camera Image Capture

Displays image preview on screen. Counts down and saves image. Restart program 
to take multiple photos.

Author: EdgeImpulse, Inc.
Date: July 6, 2021
Updated: August 9, 2023
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import cv2
from picamera2 import Picamera2

# Settings
res_width = 96                          # Resolution of camera (width)
res_height = 96                         # Resolution of camera (height)
rotation = 0                            # Camera rotation (0, 90, 180, or 270)
cam_format = "RGB888"                   # Color format
draw_fps = False                        # Draw FPS on screen
save_path = "./"                        # Save images to current directory
file_num = 0                            # Starting point for filename
file_suffix = ".png"                    # Extension for image file
precountdown = 2                        # Seconds before starting countdown
countdown = 5                           # Seconds to count down from

# Initial framerate value
fps = 0

################################################################################
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

################################################################################
# Main

# Figure out the name of the output image filename
filepath = get_filepath()

# Interface with camera
with Picamera2() as camera:

    # Configure camera settings
    config = camera.create_video_configuration(
        main={"size": (res_width, res_height), "format": cam_format})
    camera.configure(config)

    # Start camera
    camera.start()
    
    # Initial countdown timestamp
    countdown_timestamp = cv2.getTickCount()

    # Continuously capture frames
    while True:
                                            
        # Get timestamp for calculating actual framerate
        timestamp = cv2.getTickCount()
        
        # Get array that represents the image
        img = camera.capture_array()
        
        # Rotate image
        if rotation == 0:
            pass
        elif rotation == 90:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif rotation == 180:
            img = cv2.rotate(img, cv2.ROTATE_180)
        elif rotation == 270:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            print("ERROR: rotation not supported. Must be 0, 90, 180, or 270.")
            break

        # Fix colors (as OpenCV works in BGR format)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
       
        # Each second, decrement countdown
        if (timestamp - countdown_timestamp) / cv2.getTickFrequency() > 1.0:
            countdown_timestamp = cv2.getTickCount()
            countdown -= 1
            
            # When countdown reaches 0, break out of loop to save image
            if countdown <= 0:
                countdown = 0
                break
                
        
        # Draw countdown on screen
        cv2.putText(img,
                    str(countdown),
                    (int(round(res_width / 2) - 5),
                        int(round(res_height / 2))),
                    cv2.FONT_HERSHEY_PLAIN,
                    1,
                    (255, 255, 255))
                    
        # Draw framerate on frame
        if draw_fps:
            cv2.putText(img, 
                        "FPS: " + str(round(fps, 2)), 
                        (0, 12),
                        cv2.FONT_HERSHEY_PLAIN,
                        1,
                        (255, 255, 255))
        
        # Show the frame
        cv2.imshow("Frame", img)
        
        # Calculate framrate
        frame_time = (cv2.getTickCount() - timestamp) / cv2.getTickFrequency()
        fps = 1 / frame_time
        
        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break
    
    # Capture image
    cv2.imwrite(filepath, img)
    print("Image saved to:", filepath)

# Clean up
cv2.destroyAllWindows()
