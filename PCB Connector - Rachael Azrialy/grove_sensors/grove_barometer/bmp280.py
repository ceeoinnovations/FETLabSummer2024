# Simplified BMP280 driver for MicroPython with error checking
# Save this as bmp280.py in your /lib directory

import time

class BMP280:
    def __init__(self, i2c, addr=0x77):
        self.i2c = i2c
        self.addr = addr
        self.t_fine = 0
        
        # Check if the sensor is responding
        if not self.is_sensor_present():
            raise RuntimeError("BMP280 sensor not found")
        
        self.load_calibration()

    def is_sensor_present(self):
        try:
            # Try to read the chip ID register
            chip_id = self.read_byte(0xD0)
            return chip_id == 0x58  # BMP280 chip ID
        except:
            return False

    def load_calibration(self):
        # Read calibration data
        self.dig_T1 = self.read_word(0x88)
        self.dig_T2 = self.read_signed_word(0x8A)
        self.dig_T3 = self.read_signed_word(0x8C)
        self.dig_P1 = self.read_word(0x8E)
        self.dig_P2 = self.read_signed_word(0x90)
        self.dig_P3 = self.read_signed_word(0x92)
        self.dig_P4 = self.read_signed_word(0x94)
        self.dig_P5 = self.read_signed_word(0x96)
        self.dig_P6 = self.read_signed_word(0x98)
        self.dig_P7 = self.read_signed_word(0x9A)
        self.dig_P8 = self.read_signed_word(0x9C)
        self.dig_P9 = self.read_signed_word(0x9E)

    def read_byte(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 1)
        if data is None or len(data) == 0:
            raise RuntimeError(f"Failed to read from register {reg}")
        return data[0]

    def read_word(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        if data is None or len(data) < 2:
            raise RuntimeError(f"Failed to read word from register {reg}")
        return data[0] | (data[1] << 8)

    def read_signed_word(self, reg):
        raw = self.read_word(reg)
        if raw > 32767:
            raw -= 65536
        return raw

    @property
    def temperature(self):
        # Read temperature
        self.i2c.writeto_mem(self.addr, 0xF4, b'\x2E')
        time.sleep_ms(10)
        data = self.i2c.readfrom_mem(self.addr, 0xF7, 3)
        if data is None or len(data) < 3:
            raise RuntimeError("Failed to read temperature data")
        adc_T = (data[0] << 16 | data[1] << 8 | data[2]) >> 4

        var1 = ((((adc_T >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11)
        var2 = (((((adc_T >> 4) - self.dig_T1) * ((adc_T >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        self.t_fine = var1 + var2
        T = (self.t_fine * 5 + 128) >> 8
        return T / 100

    @property
    def pressure(self):
        # Read pressure
        self.i2c.writeto_mem(self.addr, 0xF4, b'\x74')
        time.sleep_ms(10)
        data = self.i2c.readfrom_mem(self.addr, 0xF7, 3)
        if data is None or len(data) < 3:
            raise RuntimeError("Failed to read pressure data")
        adc_P = (data[0] << 16 | data[1] << 8 | data[2]) >> 4

        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = ((var1 * var1 * self.dig_P3) >> 8) + ((var1 * self.dig_P2) << 12)
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
            return 0
        p = 1048576 - adc_P
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.dig_P8 * p) >> 19
        p = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
        return p / 256 / 100
