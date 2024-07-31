from hub import pins as Pin
from hub import uart
import time
from softwarei2c import SoftwareI2C

i2c = SoftwareI2C(scl_pin=Pin.TX, sda_pin=Pin.RX)  # Example GPIO pins
    
print("Scanning I2C bus...", i2c.scan())
