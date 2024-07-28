import machine
led = machine.Pin("LED", machine.Pin.OUT)
led.off()
led.on()




import time
import network, ubinascii
#from mySecrets import Weston_Wireless as wifi

wifi = {'ssid':'tufts_eecs','pass':'foundedin1883'}

def connect_wifi(wifi):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    print("MAC " + mac)
    station.connect(wifi['ssid'], wifi['pass'])
    while not station.isconnected():
        time.sleep(1)
    print('Connection successful')
    print(station.ifconfig())

connect_wifi(wifi)






import mqtt
import machine
from BLE_CEEO import Yell, Listen








def whenCalled(topic, msg):
    message = (topic.decode(), msg.decode())
    message = message[1]
    print(message)
    p.send(message)



p = Yell('pico', verbose = True)

if p.connect_up():
    print('P connected')
    time.sleep(2)

try:
    fred = mqtt.MQTTClient('pico', 'broker.hivemq.com', keepalive=1000)
    temp = fred.connect()
    print('MQTT Connected')
    fred.set_callback(whenCalled)
    fred.subscribe('oculus/gyroscope')

    while True:
        
        temp = fred.wait_msg()  # check subscriptions - you might want to do this more often
        
        time.sleep_ms(100)

except Exception as e:
    print(e)
finally: 
    fred.disconnect()
    print('MQTT Disconnected')


    

