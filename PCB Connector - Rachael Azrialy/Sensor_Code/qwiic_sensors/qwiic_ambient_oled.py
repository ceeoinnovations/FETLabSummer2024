from hub import pins as Pin
from hub import uart
import time
from softwarei2c import SoftwareI2C
import ssd1306
import framebuf

#ENSURE SSD1306 and FRAMEBUF files are downloaded!!

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
    
print("Scanning I2C bus...", i2c.scan())
init_vcnl4040()

# Initialize the OLED display (width=64, height=48)
oled_width = 64
oled_height = 48
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c, addr=0x3D)

# Main loop to check ambient light and update OLED display
while True:
    ambient_light = read_ambient_light()
    dist = read_proximity()
    
    # Clear the OLED display buffer
    oled.fill(0);
    #oled.text("Ambient:", 0, 0, 1)
    #oled.text("{}".format(ambient_light), 0, 10,1)
    
    oled.text("Prox: " + "{}".format(dist), 0,40,1)
    #oled.text("{}".format(dist),0,40,1)


    # Check if ambient light is greater than 2000 and turn on LED if true
    """
    if ambient_light < 500:
        oled.text("Dark!", 0, 30,1)
    elif ambient_light >2000:
        oled.text("Bright!", 0, 30,1)
    """
    oled.show()
   
