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
from picamera import PiCamera
from picamera.array import PiRGBArray
from edge_impulse_linux.image import ImageImpulseRunner

# Settings
model_file = "modelfile.eim"            # Trained ML model from Edge Impulse
target_label = "dog"                    # Which label we're looking for
target_threshold = 0.6                  # Draw box if output prob. >= this value
cam_width = 320                         # Width of frame (pixels)
cam_height = 240                        # Height of frame (pixels)
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

# Start the camera
with PiCamera() as camera:
    
    # Configure camera settings
    camera.resolution = (cam_width, cam_height)
    
    # Container for our frames
    raw_capture = PiRGBArray(camera, size=(cam_width, cam_height))

    # Continuously capture frames (this acts as our main "while True" loop)
    for frame in camera.capture_continuous(raw_capture, 
                                            format='bgr', 
                                            use_video_port=True):
                                            
        # Get timestamp for calculating actual framerate
        timestamp = cv2.getTickCount()
        
        # Get Numpy array that represents the image
        img = frame.array
        
        # Convert image to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # >>> ENTER YOUR CODE HERE <<<
        # Loop over all possible windows, crop/copy image under window, 
        # perform inference on windowed image, compare output to threshould, 
        # print out info (x, y, w, h) of all bounding boxes that meet or exceed 
        # that threshold.
        
        # Slide window across image and perform inference on each sub-image
        bboxes = []
        for vertical_window in range(num_vertical_windows):
            for horizontal_window in range(num_horizontal_windows):

                # Crop out image under window
                x = horizontal_window * stride
                y = vertical_window * stride
                window_img = img[y:(y + window_height), x:(x + window_width)]
                
                # Extract features from image (e.g. convert to grayscale, crop, etc.)
                features, cropped = runner.get_features_from_image(window_img)

                # Do inference on sub-image (cropped window portion)
                res = None
                try:
                    res = runner.classify(features)
                except Exception as e:
                    print("ERROR: Could not perform inference")
                    print("Exception:", e)
                
                # The output probabilities are stored in the results
                predictions = res['result']['classification']
                
                # Remember bounding box location if target inference >= thresh.
                if predictions[target_label] >= target_threshold:
                    bboxes.append((x, 
                                   y, 
                                   window_width, 
                                   window_height, 
                                   predictions[target_label]))

        # Draw bounding boxes on preview image
        for bb in bboxes:
            cv2.rectangle(img, 
                          pt1=(bb[0], bb[1]), 
                          pt2=(bb[0] + bb[2], bb[1] + bb[3]),
                          color=(255, 255, 255))

        # Print bounding box locations
        print("---")
        print("Boxes:")
        for bb in bboxes:
            print(" " + "x:" + str(bb[0]) + " y:" + str(bb[1]) + " w:" + str(bb[2]) +
                    " h:" + str(bb[3]) + " prob:" + str(bb[4]))
        print("FPS:", round(fps, 2))
        
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