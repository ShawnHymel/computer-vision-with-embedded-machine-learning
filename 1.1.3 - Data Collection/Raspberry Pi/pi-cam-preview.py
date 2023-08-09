#!/usr/bin/env python
"""
Raspberry Pi Camera Test

Capture frame from Pi Camera and display it to the screen using OpenCV (cv2).
Also display the framerate (fps) to the screen. Use this to adjust the camera's
focus. Press ctrl + c in the console or 'q' on the preview window to stop.

Based on the tutorial from Adrian Rosebrock:
https://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/

Author: EdgeImpulse, Inc.
Date: July 5, 2021
Updated: August 9, 2023
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import cv2
from picamera2 import Picamera2

# Settings
res_width = 320                         # Resolution of camera (width)
res_height = 320                        # Resolution of camera (height)
rotation = 0                            # Image rotation (0, 90, 180, or 270)

# Initial framerate value
fps = 0

# Interface with camera
with Picamera2() as camera:

    # Configure camera settings
    config = camera.create_video_configuration(main={"size": (res_width, res_height)})
    camera.configure(config)

    # Start camera
    camera.start()

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
        
        # Draw framerate on frame
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
            
# Clean up
cv2.destroyAllWindows()