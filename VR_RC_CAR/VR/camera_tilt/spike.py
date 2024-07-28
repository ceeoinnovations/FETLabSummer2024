from BLE_CEEO import Yell, Listen
import time
import motor
from hub import port

def central(name):
    try:
        L = Listen(name, verbose=True)
        if L.connect_up():
            print('L connected')
            while L.is_connected:
                time.sleep_ms(10)  # Adjust sleep time as needed
                if L.is_any:
                    print("working")
                    msg = L.read()

                    msg_list = msg.split(",")
                    #yaw = int(msg_list[0])
                    pitch = int(msg_list[1])
                    
#                     print(yaw, pitch)
#                     if yaw > 180:
#                         yaw = 180 - yaw
#                     if pitch > 180:
#                         pitch = 180 - pitch
#                     
#                     print("adjusted yaw and pitch:", yaw, pitch)

                    
                    #adjusted_yaw = int(yaw*2.333)
                    
                    #motor.run_to_absolute_position(port.D, adjusted_yaw, 1000)    
                    motor.run_to_absolute_position(port.F, pitch, 1000)

    
    except Exception as e:
        print(e)
    finally:
        L.disconnect()
        print('Closing up')

central('pico')

