from BLE_CEEO import Yell, Listen
import time
#import force_sensor as fs
import motor
from hub import port

claw_open = False
new_press = False

try:
    L = Listen('dave', verbose=True)
    if L.connect_up():
        print('L connected')
        while L.is_connected:
            time.sleep_ms(10)  # Adjust sleep time as needed
            if L.is_any:
                message = L.read()
                #message = message.strip('\x00')
                #control_values = message.split('.')[0]
                control_values = message.split(',')
                print(control_values)
                if len(control_values) == 6:
                    x0 = 10 * int(control_values[0])
                    y0 = 10 * int(control_values[1])
                    x1 = 10 * int(control_values[2])
                    y1 = 10 * int(control_values[3])
                    
                    throttle = -int(control_values[4])*2
                    button = control_values[5] 
                    steer_angle = int(85 - ((x1 - 132)*(30/132)))
                    arm_pan = x0 - 120
                    arm_lift = y0 - 120

                    motor.run(port.A, throttle)
                    motor.run_to_absolute_position(port.B, steer_angle, 200)
                    motor.run(port.E, arm_pan)
                    motor.run(port.F, arm_lift)
                    
                    #CLAW
                    if button == "T" and new_press == True:
                        if claw_open:
                            motor.run(port.D, 1000)
                        else:
                            motor.run(port.D, -1000)     
                        claw_open = not claw_open
                        new_press = False
                    elif button == "F":
                        motor.stop(port.D)
                        new_press = True
                        
                    #ARM
                        
                        

except Exception as e:
    print(e)
finally:
    L.disconnect()
    print('Closing up')

#central('dave')
