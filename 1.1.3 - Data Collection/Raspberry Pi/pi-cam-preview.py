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
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray

# Settings
res_width = 320                         # Resolution of camera (width)
res_height = 320                        # Resolution of camera (height)
rotation = 0                            # Camera rotation (0, 90, 180, or 270)

# Initial framerate value
fps = 0

# Start the camera
with PiCamera() as camera:

    # Configure camera settings
    camera.resolution = (res_width, res_height)
    camera.rotation = rotation
    
    # Container for our frames
    raw_capture = PiRGBArray(camera, size=(res_width, res_height))

    # Continuously capture frames (this is our while loop)
    for frame in camera.capture_continuous(raw_capture, 
                                            format='bgr', 
                                            use_video_port=True):
                                            
        # Get timestamp for calculating actual framerate
        timestamp = cv2.getTickCount()
        
        # Get Numpy array that represents the image
        img = frame.array
        
        # Draw framerate on frame
        cv2.putText(img, 
                    "FPS: " + str(round(fps, 2)), 
                    (0, 12),
                    cv2.FONT_HERSHEY_PLAIN,
                    1,
                    (255, 255, 255))
        
        # Show the frame
        cv2.imshow("Frame", img)
        
        # Clear the stream to prepare for next frame
        raw_capture.truncate(0)
        
        # Calculate framrate
        frame_time = (cv2.getTickCount() - timestamp) / cv2.getTickFrequency()
        fps = 1 / frame_time
        
        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break
            
# Clean up
cv2.destroyAllWindows()