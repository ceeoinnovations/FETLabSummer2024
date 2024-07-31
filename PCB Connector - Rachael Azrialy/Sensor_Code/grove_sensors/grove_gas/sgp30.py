# SGP30 - Air quality sensor
# Modified for use with custom SoftwareI2C implementation

import time
from micropython import const

SGP30_I2C_ADDR = const(0x58)

class SGP30:
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = SGP30_I2C_ADDR
        self._eCO2 = 0
        self._TVOC = 0

    def init_sgp30(self):
        # Init air quality measurement
        self.i2c.writeto(self.addr, b'\x20\x03')
        time.sleep_ms(20)  # Wait 20ms for measurement to initialize

    def _read_data(self, command):
        self.i2c.writeto(self.addr, command)
        time.sleep_ms(50)  # Wait for measurement
        data = self.i2c.readfrom(self.addr, 6)
        return data

    def _process_data(self, data):
        co2 = data[0] << 8 | data[1]
        tvoc = data[3] << 8 | data[4]
        return co2, tvoc

    def read_measurements(self):
        data = self._read_data(b'\x20\x08')
        self._eCO2, self._TVOC = self._process_data(data)
        return self._eCO2, self._TVOC

    @property
    def eCO2(self):
        return self._eCO2

    @property
    def TVOC(self):
        return self._TVOC
