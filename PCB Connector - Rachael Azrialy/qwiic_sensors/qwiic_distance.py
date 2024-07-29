from hub import pins as Pin
from hub import uart
import time
from softwarei2c import SoftwareI2C

i2c = SoftwareI2C(scl_pin=Pin.TX, sda_pin=Pin.RX)  # Example GPIO pins

# VCNL4040 I2C address
vcnl4040_addr = 0x60

# VCNL4040 register addresses
PROXIMITY_DATA_REG = 0x08  # Proximity data registers (2 bytes)
AMBIENT_LIGHT_REG = 0x09   # Ambient light data registers (2 bytes)
ALS_CONF_REG = 0x00        # Ambient light sensor configuration register
PS_CONF_REG = 0x03         # Proximity sensor configuration registers

# Function to initialize VCNL4040
def init_vcnl4040():
    # Example: write to ALS and PS configuration registers to initialize (values depend on desired configuration)
    i2c.writeto_mem(vcnl4040_addr, ALS_CONF_REG, b'\x00\x00')  # Example settings for ALS
    i2c.writeto_mem(vcnl4040_addr, PS_CONF_REG, b'\x00\x00')   # Example settings for PS

# Function to read proximity data
def read_proximity():
    data = i2c.readfrom_mem(vcnl4040_addr, PROXIMITY_DATA_REG, 2)
    proximity = int.from_bytes(data, 'little')
    return proximity

# Function to read ambient light level
def read_ambient_light():
    data = i2c.readfrom_mem(vcnl4040_addr, AMBIENT_LIGHT_REG, 2)
    light_level = int.from_bytes(data, 'little')
    return light_level

# Initialize the sensor
while(1):
    p = i2c.scan()
    print(p)
    if(p and p[0] == 96):
        break

print("Scanning I2C bus...", i2c.scan())
init_vcnl4040()

while(1):# Example usage
    time.sleep(0.1)
    print("Reading Proximity:", read_proximity())
    print("Reading Ambient Light:", read_ambient_light())
  
