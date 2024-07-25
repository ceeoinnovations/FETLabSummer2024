'''
# install the openmv IDE and save this code on your camera: connect camera --> save to camera --> tools --> save open script to camera. 
# this will ensure that this code runs when the camera is powered on.

import sensor, image, time
import sensor, image, time, pyb

# Initialize the camera
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# Set up UART communication
uart = pyb.UART(3, 115200, timeout_char=1000)  # Use UART3, baud rate 115200

# Color threshold for red ball detection
red_threshold = (30, 100, 15, 127, 15, 127)

def init():
    img = sensor.snapshot()
    blobs = img.find_blobs([red_threshold], pixels_threshold=200, area_threshold=200)

    if blobs:
        largest_blob = max(blobs, key=lambda b: b.pixels())
        x, y = largest_blob.cx(), largest_blob.cy()
        # Send the coordinates over UART
        uart.write(f"({x},{y})")  # Format: (123,456)
        #img.draw_cross(x, y, color=(0, 0, 255))
        #print(f"Ball position: x={x}, y={y}")
        #return x, y

    time.sleep_ms(100)

while(True):
    init()
    '''
