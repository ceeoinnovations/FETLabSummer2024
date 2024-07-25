from machine import ADC, Pin
import time

adc = ADC(Pin(27))  # Initialize ADC on GPIO pin 27
uvs = []


def get_voltage(value):
    ref = 3.3
    voltage = (value / 65535) * ref
    return voltage


def get_illumination(voltage):
    return voltage * 307


def get_uvindex(illumination):
    return illumination / 35


def measure_uv_index():
    value = adc.read_u16()
    voltage = get_voltage(value)
    illumination = get_illumination(voltage)
    uv_index = get_uvindex(illumination)
    return uv_index


x = 1
while x < 6:
    uv_index = measure_uv_index()
    uv_index = round(uv_index, 2)
    uvs.append(uv_index)
    print("UV Index:", uv_index)
    # Sleep for 1 hour (3600 seconds)
    x += 1
    time.sleep(.2)
