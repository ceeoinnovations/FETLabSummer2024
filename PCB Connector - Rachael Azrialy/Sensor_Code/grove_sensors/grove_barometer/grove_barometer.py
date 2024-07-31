from hub import pins as Pin
from hub import uart
import time
from softwarei2c import SoftwareI2C
import bmp280

i2c = SoftwareI2C(scl_pin=Pin.TX, sda_pin=Pin.RX)  # Example GPIO pins

print("Scanning I2C bus...", i2c.scan())

# Initialize the BMP280 sensor
sensor = bmp280.BMP280(i2c)

# Read and print sensor data
while True:
    temperature = -1*sensor.temperature
    pressure = sensor.pressure

    print("Temperature: {:.2f} C".format(temperature))
    print("Pressure: {:.2f} hPa".format(pressure))

    time.sleep(1)
