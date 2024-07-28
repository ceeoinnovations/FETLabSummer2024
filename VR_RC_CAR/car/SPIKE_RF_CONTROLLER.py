from BLE_CEEO import Yell, Listen
import time
from hub import port
import force_sensor
import motor

def central(name):
    
    try:
        L = Listen(name, verbose=True)
        if L.connect_up():
            print('L connected')
            while L.is_connected:
                time.sleep_ms(10)  # Adjust sleep time as needed
                
                if 500 < force_sensor.raw(port.B) < 690:
                    motor_speed_acc = (force_sensor.raw(port.B) - 400) * 2
                elif force_sensor.raw(port.B) > 690:
                    motor_speed_acc = 600
                else:
                    motor_speed_acc = 0
                    
                if 500 < force_sensor.raw(port.E) < 680:
                    motor_speed_rev = (force_sensor.raw(port.E) - 400) * 2
                elif force_sensor.raw(port.E) > 680:
                    motor_speed_rev = 600
                else:
                    motor_speed_rev = 0
      
                motor_speed = motor_speed_acc - motor_speed_rev
                motor_speed = str(motor_speed)
                
                button = force_sensor.pressed(port.D)
                
                controller_values = str(motor_speed)+","+str(button)+"."
                
                L.send(controller_values)
                
#                 if L.is_any:
#                     message = L.read()
#                     message = str(message.split(",")[0])
#                     print(message)
                    
    
    except Exception as e:
        print(e)
    finally:
        L.disconnect()
        print('Closing up')

central('bob')
