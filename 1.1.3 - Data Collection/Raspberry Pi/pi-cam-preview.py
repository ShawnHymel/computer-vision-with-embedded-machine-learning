#!/usr/bin/env python
"""
Raspberry Pi Camera Preview

Displays image preview on screen. Use this to adjust the camera's focus. Press
ctrl + c to stop.

Author: EdgeImpulse, Inc.
Date: June 8, 2021
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import picamera
from PIL import Image, ImageDraw
from time import sleep

# Settings
res_width = 640                         # Resolution of camera (width)
res_height = 480                        # Resolution of camera (height)
img_width = 96                          # Width of image to capture
img_height = 96                         # Height of image to capture

# Open camera indefinitely until ctrl+c
try:

    # Start camera preview
    camera = picamera.PiCamera()
    camera.resolution = (res_width, res_height)
    camera.framerate = 24
    camera.start_preview()
    
    # Calculate center x and y of image (round up)
    center_x = int(res_width / 2 + 0.5)
    center_y = int(res_height / 2 + 0.5)
    
    # Determine coordinates for center viewfinder (vf) overlay
    vf_x0 = center_x - int(img_width / 2 + 0.5)
    vf_x1 = center_x + int(img_width / 2 + 0.5)
    vf_y0 = center_y - int(img_height / 2 + 0.5)
    vf_y1 = center_y + int(img_height / 2 + 0.5)
    
    # Add static viewfinder to preivew (on layer 3, just above preview layer)
    vf_img = Image.new('RGBA', (res_width, res_height), (0, 0, 0, 0))
    vf_draw = ImageDraw.Draw(vf_img)
    vf_draw.rectangle([(vf_x0, vf_y0), (vf_x1, vf_y1)], 
                        outline=(255, 255, 255), 
                        width=2)
    vf_overlay = camera.add_overlay(vf_img.tobytes(), layer=3, alpha=100)
    
    # Do nothing
    while True:
        sleep(0.1)

# Nicely shut down camera
finally:
    camera.stop_preview()
    camera.close()