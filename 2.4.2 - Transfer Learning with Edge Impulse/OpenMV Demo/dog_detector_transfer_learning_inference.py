"""
OpenMV Live Image Inference

Continuously captures images and performs image using provided TFLite model
file. Outputs probabilities in console.

Author: EdgeImpulse, Inc.
Date: June 24, 2021
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import sensor, image, time, tf

# Settings
model_file = "trained.tflite"           # Location of TFLite model file
labels_file = "labels.txt"              # Location of labels file
width = 48                              # Width of frame (pixels)
height = 48                             # Height of frame (pixels)
pixel_format = sensor.GRAYSCALE         # This model only supports grayscale

# Configure camera
sensor.reset()
sensor.set_pixformat(pixel_format)      # Set pixel format to RGB565 or GRAYSCALE
sensor.set_framesize(sensor.QVGA)       # Set frame size to QVGA (320x240)
sensor.set_windowing((width, height))   # Crop sensor frame to this resolution
sensor.skip_frames(time = 2000)         # Let the camera adjust

# Extract labels from labels file
labels = [line.rstrip('\n').rstrip('\r') for line in open(labels_file)]

# Start clock (for measureing FPS)
clock = time.clock()

# Main while loop
inference_count = 0
while(True):

    # Update timer
    clock.tick()

    # Get image from camera
    img = sensor.snapshot()

    # Do inference. OpenMV tf classify returns a list of prediction objects.
    objs = tf.classify(model_file, img)

    # We should only get one item in the predictions list, so we extract the
    # output probabilities from that.
    predictions = objs[0].output()

    # Find label with the highest probability
    max_val = max(predictions)
    max_idx = predictions.index(max_val)

    # Draw label with highest probability to image viewer
    img.draw_string(0, 0, labels[max_idx] + "\n{:.2f}".format(round(max_val, 2)), mono_space = False)

    # Slow printing to the console by only printing every few inferences
    inference_count += 1
    if inference_count >= 10:
        inference_count = 0

        # Print all the probabilities
        print("-----")
        for i, label in enumerate(labels):
            print(str(label) + ": " + str(predictions[i]))

    # Uncomment this if you want to see FPS measurement
    print("FPS:", clock.fps())
