#!/usr/bin/env python
"""
Pi Camera Sliding Window Object Detection

Continuously captures images and performs inference on a sliding window to 
detect objects.

Author: EdgeImpulse, Inc.
Date: August 5, 2021
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import os, sys, time, math
import cv2
from picamera2 import Picamera2
from edge_impulse_linux.image import ImageImpulseRunner

# Settings
model_file = "modelfile.eim"            # Trained ML model from Edge Impulse
target_label = "dog"                    # Which label we're looking for
target_threshold = 0.6                  # Draw box if output prob. >= this value
cam_width = 320                         # Width of frame (pixels)
cam_height = 240                        # Height of frame (pixels)
rotation = 0                            # Camera rotation (0, 90, 180, or 270)
window_width = 96                       # Window width (input to CNN)
window_height = 96                      # Window height (input to CNN)
stride = 24                             # How many pixels to move the window

# The ImpulseRunner module will attempt to load files relative to its location,
# so we make it load files relative to this program instead
dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(dir_path, model_file)

# Load the model file
runner = ImageImpulseRunner(model_path)

# Initialize model (and print information if it loads)
try:
    model_info = runner.init()
    labels = model_info['model_parameters']['labels']
    print("Model name:", model_info['project']['name'])
    print("Model owner:", model_info['project']['owner'])
    print("Labels:", labels)
    
# Exit if we cannot initialize the model
except Exception as e:
    print("ERROR: Could not initialize model")
    print("Exception:", e)
    if (runner):
            runner.stop()
    sys.exit(1)

# Compute number of window steps
num_horizontal_windows = math.floor((cam_width - window_width) / stride) + 1
num_vertical_windows = math.floor((cam_height - window_height) / stride) + 1

# Initial framerate value
fps = 0

# Interface with camera
with Picamera2() as camera:

    # Configure camera settings
    config = camera.create_video_configuration(main={"size": (cam_width, cam_height)})
    camera.configure(config)

    # Start camera
    camera.start()

    # Continuously capture frames
    while True:
                                            
        # Get timestamp for calculating actual framerate
        timestamp = cv2.getTickCount()
        
        # Get array that represents the image (in RGB format)
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
        
        # >>> ENTER YOUR CODE HERE <<<
        # Loop over all possible windows, crop/copy image under window, 
        # perform inference on windowed image, compare output to threshould, 
        # print out info (x, y, w, h) of all bounding boxes that meet or exceed 
        # that threshold.
        
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