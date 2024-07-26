import ampy
from pyscript import document
import time
from qlearning import rl
import print_new

ARDUINO_NANO = 128
SPIKE = 256

value = 500
move_motor_code = f"""
import motor
import time
from hub import port

# Starts motor at power=1000 and runs for 1 second
motor.run(port.C, {value})
time.sleep_ms(2000)
motor.stop(port.C)

# Starts motor at power=1000 and runs for 1 second
motor.run(port.D, {value})
time.sleep_ms(2000)
motor.stop(port.D)



"""

stop_motor_code = f"""
import motor
import time
from hub import port

# Starts motor at power=1000 and runs for 1 second
motor.stop(port.C)

# Starts motor at power=1000 and runs for 1 second
motor.stop(port.D)


"""


def on_move_motor(event):
    print("moving motor")
    await terminal.eval(move_motor_code)

def on_stop_motor(event):
    print("stopping motor")
    await terminal.eval(stop_motor_code)

def on_connect(event):
    await terminal.board.connect('repl')
    if terminal.connected:
        move_motor.disabled = False
        connect.innerHTML = 'Disconnect'
        connect.onclick = on_disconnect
        print("connected")
        
def on_disconnect(event):
    print("disconnected")
    connect.innerHTML = 'Connect'
    move_motor.disabled = True
    connect.onclick = on_connect
    await terminal.board.disconnect()

color_val = "<div class='colorWrap'>"

color_sensor_code = """
from hub import port
import color
import color_sensor

print('im here')
color_reading = color_sensor.color(port.F)
color_reading
"""
#colorPick() #call this somewhere



# def myfunc(color_reading):
#     color_val += f"""
#     <div class="colorClass" style="background-color: {color_reading.lower()}">
#     """

def color_sensor(event):
    states = {
            -1:'ERR',
            0:"Black",
            1:"Magenta",
            3:"Blue",
            4:"Azure",
            6:"Green",
            7:"Yellow",
            9:"Red",
            10:"White",
            }
    event.goal_state = [6] # goal state is Green
    event.end_state = [1, 6]
    event.reward_default = -1
    event.current_state = None
    event.action_space = [0, 1]
    #print("calling color sensor")
    color_name = await terminal.eval(color_sensor_code)
    #color_name = await terminal.eval(ex.code)
    color = states[int(color_name)]
    print(color)
    document.getElementById('colorOutput').innerHTML = f"""
    <div class="colorOutput">
        <span class="color-value">{color} </span>
    </div>
    """
    #run for 4 seconds
    #start_time = time.time()
    #text = "hello"
    #print(await terminal.eval("""text"""))
    #color = await terminal.eval(color_sensor_code)
    #print(color)
    #document.getElementById('colorOutput').innerHTML = await terminal.eval("""text""")
    #document.getElementById('colorOutput').style.backgroundColor = color
    # while time.time() - start_time < 4:
    #color_name = await terminal.eval("""color_sensor.color(port.F)""", 'hidden')
    #print(color_name)
    #     # color_name = await terminal.eval(color_sensor_code)
    #     #print(await terminal.eval("""text"""))
    #     print(await terminal.eval(color_sensor_code))

    #     #document.getElementById('colorOutput').innerHTML = await terminal.eval("""text""")
    #     document.getElementById('colorOutput').style.backgroundColor = color_val

rl_example_code = """
for i in range(5):
    print("EPISODE " + str(i) + "... Waiting to reset robot to START STATE ")
    while not button.pressed(button.LEFT):
        #print("waiting to begin episodes")
        continue
    time.sleep(1)
    print("Episode " + str(i) + " Beginning...")
"""

def run_rl(event):
    rl_code = rl()
    print("starting RL")
    #await terminal.eval(rl_code)
    await terminal.eval('\x05' + rl_code + "#**END-CODE**#" + '\x04')



terminal = ampy.Ampy(SPIKE)
terminal.newData_callback = print_new.on_data_jav

#connect button
connect = document.getElementById('connect')
connect.onclick = on_connect

#motor
#move_motor = document.getElementById("move_motor")
#move_motor.disabled = True
#move_motor.onclick = on_move_motor

#stop_motor = document.getElementById("stop_motor")
#stop_motor.disabled = True
#stop_motor.onclick = on_stop_motor

color_button = document.getElementById("get_color")
color_button.onclick = color_sensor

RL_button = document.getElementById("rl_code")
RL_button.onclick = run_rl
