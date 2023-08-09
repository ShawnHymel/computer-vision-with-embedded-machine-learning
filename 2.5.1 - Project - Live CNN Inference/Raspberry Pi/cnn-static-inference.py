#!/usr/bin/env python
"""
Pi Camera Static Image Classification

Detects objects in continuous stream of images from Pi Camera. Use Edge Impulse
Runner and downloaded .eim model file to perform inference. Bounding box info is
drawn on top of detected objects along with framerate (FPS) in top-left corner.

Copy one of the test images to the same folder, rename image_file as necessary
(e.g. "48.png").

Author: EdgeImpulse, Inc.
Date: August 3, 2021
Updated: August 9, 2023
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import os, sys, time
import cv2
from edge_impulse_linux.image import ImageImpulseRunner

# Settings
image_file = "48.png"                   # Image to test
model_file = "modelfile.eim"            # Trained ML model from Edge Impulse

# The ImpulseRunner module will attempt to load files relative to its location,
# so we make it load files relative to this program instead
dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(dir_path, model_file)

# Load the model file
runner = ImageImpulseRunner(model_path)

# Initialize model (and print information if it loads)
try:
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

# Load image (as BGR color image)
img = cv2.imread(image_file, cv2.IMREAD_COLOR)

# Convert image to RGB
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Encapsulate raw image values into array for model input
features, cropped = runner.get_features_from_image(img)

# Perform inference
res = None
try:
    res = runner.classify(features)
except Exception as e:
    print("ERROR: Could not perform inference")
    print("Exception:", e)
    
# Print out results information
print(res)
    
# Display predictions and timing data
print("-----")
results = res['result']['classification']
for label in results:
    prob = results[label]
    print(label + ": " + str(round(prob, 3)))