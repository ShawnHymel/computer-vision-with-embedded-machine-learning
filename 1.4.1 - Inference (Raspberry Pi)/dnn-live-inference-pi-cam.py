#!/usr/bin/env python
"""
Raspberry Pi Live Image Inference

Continuously captures image from Raspberry Pi Camera module and perform 
inference using provided .eim model file. Outputs probabilities in console.

Author: EdgeImpulse, Inc.
Date: June 8, 2021
Updated: August 9, 2023
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import os, sys, time
import cv2
import numpy as np
from picamera2 import Picamera2
from edge_impulse_linux.runner import ImpulseRunner

# Settings
model_file = "modelfile.eim"            # Trained ML model from Edge Impulse
draw_fps = True                         # Draw FPS on screen
res_width = 96                          # Resolution of camera (width)
res_height = 96                         # Resolution of camera (height)
rotation = 0                            # Camera rotation (0, 90, 180, or 270)
cam_format = "RGB888"                   # Color format
img_width = 28                          # Resize width to this for inference
img_height = 28                         # Resize height to this for inference

# The ImpulseRunner module will attempt to load files relative to its location,
# so we make it load files relative to this program instead
dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(dir_path, model_file)

# Load the model file
runner = ImpulseRunner(model_path)

# Initialize model
try:

    # Print model information
    model_info = runner.init()
    print("Model name:", model_info['project']['name'])
    print("Model owner:", model_info['project']['owner'])
    
# Exit if we cannot initialize the model
except Exception as e:
    print("ERROR: Could not initialize model")
    print("Exception:", e)
    if (runner):
            runner.stop()
    sys.exit(1)
    
# Initial framerate value
fps = 0

# Interface with camera
with Picamera2() as camera:

    
    # Configure camera settings
    config = camera.create_video_configuration(
        main={"size": (res_width, res_height), "format": cam_format})
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

        # Convert image to grayscale
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Resize captured image
        img_resize = cv2.resize(img, (img_width, img_height))
        
        # Convert image to 1D vector of floating point numbers
        features = np.reshape(img_resize, (img_width * img_height)) / 255
        
        # Edge Impulse model expects features in list format
        features = features.tolist()
        
        # Perform inference
        res = None
        try:
            res = runner.classify(features)
        except Exception as e:
            print("ERROR: Could not perform inference")
            print("Exception:", e)
            
        # Display predictions and timing data
        print("Output:", res)
        
        # Display prediction on preview
        if res is not None:
        
            # Find label with the highest probability
            predictions = res['result']['classification']
            max_label = ""
            max_val = 0
            for p in predictions:
                if predictions[p] > max_val:
                    max_val = predictions[p]
                    max_label = p
                    
            # Draw predicted label on bottom of preview
            cv2.putText(img,
                        max_label,
                        (0, res_height - 20),
                        cv2.FONT_HERSHEY_PLAIN,
                        1,
                        (255, 255, 255))
                        
            # Draw predicted class's confidence score (probability)
            cv2.putText(img,
                        str(round(max_val, 2)),
                        (0, res_height - 2),
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
            
# Clean up
cv2.destroyAllWindows()