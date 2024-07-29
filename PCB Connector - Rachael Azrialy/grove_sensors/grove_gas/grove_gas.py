from hub import pins as Pin
from hub import uart
import time
from softwarei2c import SoftwareI2C
from sgp30 import SGP30

i2c = SoftwareI2C(scl_pin=Pin.TX, sda_pin=Pin.RX)  # Example GPIO pins
    
print("Scanning I2C bus...", i2c.scan())

# Initialize the SGP30 sensor
sensor = SGP30(i2c)
sensor.init_sgp30()

# Read and print sensor data
while True:
    eCO2 = sensor.eCO2
    TVOC = sensor.TVOC

    print("eCO2: {} ppm".format(eCO2))
    print("TVOC: {} ppb".format(TVOC))

    time.sleep(1)
