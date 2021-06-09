"""
Raspberry Pi Live Image Inference

Continuously captures image from Raspberry Pi Camera module and perform 
inference using provided .eim model file. Outputs probabilities in console.

Author: EdgeImpulse, Inc.
Date: June 8, 2021
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import os, sys, time
import cv2
import numpy as np
import picamera
from picamera.array import PiRGBArray
from PIL import Image, ImageDraw, ImageFont
from edge_impulse_linux.runner import ImpulseRunner

# Settings
model_file = "modelfile.eim"            # Trained ML model from Edge Impulse
font_size = 40                          # Size of font
res_width = 96                          # Resolution of camera (width)
res_height = 96                         # Resolution of camera (height)
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

# Text overlay for preview
text_overlay = None

# Start the camera
with picamera.PiCamera() as camera:
    
    # Configure camera settings
    camera.resolution = (res_width, res_height)
    camera.framerate = 24
    #camera.color_effects = (128, 128)   # Set capture to grayscale
    camera.start_preview()
    
    # Loop forever
    while(True):
    
        # Get image from camera (raw RGB array)
        raw_capture = PiRGBArray(camera)
        camera.capture(raw_capture, format='rgb')
        img = raw_capture.array
        
        # Resize captured image
        img = cv2.resize(img, (img_width, img_height))
        
        # Convert image to grayscale
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Convert image to 1D vector of floating point numbers
        features = np.reshape(img, (img_width * img_height)) / 255
        
        # Edge Impulse model expects features in list format
        features = features.tolist()
        
        # Perfrom inference and print results
        try:

            # Perform inference and time how long it takes
            res = runner.classify(features)
            
            # Display predictions
            print("Predictions:")
            predictions = res['result']['classification']
            for p in predictions:
                print("  " + p + ": " + str(predictions[p]))
                
            # Find label with the highest probability
            max_label = ""
            max_val = 0
            for p in predictions:
                if predictions[p] > max_val:
                    max_val = predictions[p]
                    max_label = p
                
            # Remove text overlay layer to clear text
            if text_overlay is not None:
                camera.remove_overlay(text_overlay)
                
            # Create a new overlay image for text
            text_img = Image.new('RGBA', (res_width, res_height), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            
            # Draw predicted label on preview overlay
            text_draw.text((0, 0), 
                            max_label + "\n{:.2f}".format(round(max_val, 2)), 
                            fill=(255, 255, 255))
                
            # Add text overlay to a separate layer (above viewfinder overlay)
            text_overlay = camera.add_overlay(text_img.tobytes(), 
                                                layer=3, 
                                                alpha=100)
            
        # Print error if inference fails
        except Exception as e:
            print("ERROR: Could not perform inference")
            print("Exception:", e)