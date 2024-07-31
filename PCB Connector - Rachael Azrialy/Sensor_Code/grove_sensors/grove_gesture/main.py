import gesture
import SoftI2C
#from machine import Pin
from hub import pins as Pin
from hub import uart
from time import sleep

i2c = SoftI2C.SoftwareI2C(scl_pin=Pin.TX, sda_pin=Pin.RX)

g=gesture.Gesture(i2c)


from hub import pins as Pin
from hub import uart
import time

import struct

# 	0:nothing  ->Black
# 	1:Forward  -> Red
# 	2:Backward -> Green
# 	3:Right    -> Yellow
# 	4:Left     -> Blue
# 	5:Up       -> White
# 	6:Down     -> Aqua
# 	7:Clockwise -> Magenta
# 	8:anti-clockwise -> Mix Green|Red
# 	9:wave           -> Mix Green| Blue
while 1:
    #g.print_gesture()
    value=g.return_gesture()
    print(value)
    if value==0:
        print("nothing")
    if value==1:
        print("Forward")
    if value==2:
        print("Backward")
    if value==3:
        print("Right")
    if value==4:
        print("Left")
    if value==5:
        print("UP")
    if value==6:
        print("Down")
    if value==7:
        print("Clockwise")
    if value==8:
        print("anti-clockwise")
    if value==9:
        print("wave")
    sleep(1)
