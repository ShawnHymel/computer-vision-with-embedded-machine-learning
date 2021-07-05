#!/usr/bin/env python
"""
Raspberry Pi Camera Image Capture

Displays image preview on screen. Counts down and saves image. Restart program 
to take multiple photos.

Author: EdgeImpulse, Inc.
Date: June 8, 2021
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import picamera
from PIL import Image, ImageDraw, ImageFont
from time import sleep

# Settings
save_path = "./"                        # Save images to current directory
file_num = 0                            # Starting point for filename
file_suffix = ".png"                    # Extension for image file
precountdown = 2                        # Seconds before starting countdown
countdown = 3                           # Seconds to count down from
font_file = "FreeMono.ttf"              # Local font file to use
font_size = 40                          # Size of font to display countdown
res_width = 640                         # Resolution of camera (width)
res_height = 480                        # Resolution of camera (height)
img_width = 96                          # Width of image to capture
img_height = 96                         # Height of image to capture

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

# Start the camera
with picamera.PiCamera() as camera:
    
    # Configure camera settings
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
    
    # Set font and placeholder overlay layer for text
    font = ImageFont.truetype(font_file, size=font_size)
    text_overlay = None
    
    # Count down
    for i in reversed(range(countdown + precountdown)):
    
        # Remove text overlay layer to clear items
        if text_overlay is not None:
            camera.remove_overlay(text_overlay)
            
        # Create a new overlay image for text
        text_img = Image.new('RGBA', (res_width, res_height), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)

        # Draw countdown text
        if (i > 0) and (i <= countdown):
            text_draw.text((vf_x0, vf_y0 - font_size), 
                            str(i), 
                            font=font, 
                            fill=(255, 255, 255))
                        
        # Add text overlay to a separate layer (above viewfinder overlay)
        text_overlay = camera.add_overlay(text_img.tobytes(), 
                                            layer=4, 
                                            alpha=100)
        
        # There's a pause before image capture, so we don't need the sleep at 0
        if i > 0:
            sleep(1)
    
    # Set region of interest (ROI) to viewfinder area
    roi_x = vf_x0 / res_width
    roi_y = vf_y0 / res_height
    roi_w = img_width / res_width
    roi_h = img_height / res_height
    camera.zoom = (roi_x, roi_y, roi_w, roi_h)
    
    # Capture image and resize to desired resolution
    camera.capture(filepath, resize=(img_width, img_height))
    print("Image saved to:", filepath)
    
    # Stop the preview
    camera.stop_preview()