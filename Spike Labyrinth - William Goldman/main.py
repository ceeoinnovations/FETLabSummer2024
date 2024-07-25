from pyscript import document, window, when
import andrea_terminal, restapi, file_transfer, file_os
from ble_test import code as ble_code
import json
import file_transfer
import math, re

#
ARDUINO_NANO = 128
SPIKE = 256
path = "https://raw.githubusercontent.com/chrisbuerginrogers/SPIKE_Prime/main/BLE/BLE_CEEO.py"

def on_connect(event):
    if terminal.connected:
        connect.innerText = 'Connect the Spike'
        await terminal.board.disconnect()
    else:
        await terminal.board.connect('repl')
        if terminal.connected:
            connect.innerText = 'Disconnect'
            document.getElementById('library').classList.toggle("inactive")
            await terminal.eval('\x03', True)
    for b in btns:
        b.disabled = not terminal.connected

def on_disconnect():
    connect.innerText = 'Connect the Spike'
    terminal.update(0)

async def on_load(event):
    if terminal.connected:
        name = path.split('/')[-1]
        print('path, name: ',path,name)
        reply = await restapi.get(path)
        status = await terminal.download(name,reply)

        if terminal.connected:
            await terminal.eval('\x05' + ble_code + '\x04') #run code 
            terminal.focus()
            document.getElementById('ble_connect').classList.toggle("inactive")
            # return False
        else:
            print('terminal not connected')
            # return True

        if not status: 
            window.alert(f"Failed to load {name}")  
    else:
        window.alert('connect to a processor first')

#define loading bar value
def update_progress_display(value):    
    progress_bar.value = value
    percent_text.innerText = f"{int(value)}%"

path = "https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/umqtt.simple/umqtt/simple.py"

connect      = document.getElementById('connect')
library      = document.getElementById('library')
progress_bar = document.getElementById('progress')
percent_text = document.getElementById('progress-percent')

connect.onclick = on_connect
library.onclick = on_load

#update loading bar
terminal = file_transfer.Ampy(SPIKE, update_progress_callback=update_progress_display)
terminal.disconnect_callback = on_disconnect

btns = [library]
for b in btns:
    b.disabled = not terminal.connected


#--------------------------- all BLE control --------------------------------
from pyscript.js_modules import ble_library

ble_info = document.getElementById("ble_info")
yaw = 0
pitch = 0
roll = 0
x = 0
y = 0

#split the data into x,y and yaw, pitch, roll based on the ** delimiter
def parse_payload(data):
    document.getElementById("ble_answer").innerHTML = 'received: '+ data
    parts = data.split("**")
    xy_data = parts[0] if len(parts) > 0 else ""
    ypr_data = parts[1] if len(parts) > 1 else ""
    return xy_data, ypr_data

def parse_ypr(data):
    data = data.strip('()') # Remove the parentheses
    num_strings = data.split(',') # Split the string by comma
    try:
        numbers = [int(num.strip()) for num in num_strings] # Convert the split strings to integers
        if len(numbers) != 3:
            raise ValueError("Expected 3 numbers for yaw, pitch, roll")
        return numbers
    except (ValueError, IndexError) as e:
        print(f"Error parsing yaw, pitch, roll data: {e}")
        return None, None, None

def parse_xy(data):
    xy_data, _ = parse_payload(data)
    if not xy_data:
        print("No x, y coordinate data available") #when openmv does not recognize the ball
        return None, None
    
    # since I converted byte string into string, remove b', ', and parentheses, then split by comma
    clean_data = xy_data.strip("b'()").split(',')

    try:
        if len(clean_data) != 2:
            raise ValueError("Expected 2 values for x and y coordinates")
        x = int(clean_data[0].strip())
        y = int(clean_data[1].strip())
        return x, y
    except (IndexError, ValueError) as e:
        print(f"Invalid data format: {data}. Error: {e}")
        return None, None

#when I receive ble data, decide whether I am going to parse the xy info or the ypr info based on current mode
def received_ble(data):
    xy_data, ypr_data = parse_payload(data)
    
    if window.ballControlMode == 'coordinates':
        x, y = parse_xy(xy_data)
        if x is not None and y is not None:
            window.updateBallPosition(x, y)
    else:
        yaw, pitch, roll = parse_ypr(ypr_data)
        if yaw is not None and pitch is not None and roll is not None:
            # from decidegrees convert to radians 
            pitch_rad = (pitch / 10) * (math.pi / 180)
            roll_rad = (roll / 10) * (math.pi / 180) * -1
            window.updateBallTilt(pitch_rad, roll_rad)

ble = ble_library.newBLE()
ble.callback = received_ble

connected = False
@when("click", "#ble_connect")
async def ask(event):
    global connected
    if connected:
        await ble.disconnect()
        document.getElementById("ble_connect").innerHTML = 'Connect via BLE'
        document.querySelector(".ble_info").style.display = 'none'
        print('disconnected')
        connected = False
    else:
        name = document.getElementById("ble_name").value
        if await ble.ask(name):
            print('name ', name)
            document.getElementById("ble_connect").innerHTML = 'Connecting...'
            await ble.connect() 
            print('connected!')
            document.querySelector(".ble_info").style.display = 'block'
            document.getElementById("ble_connect").innerHTML = 'Disconnect'
            connected = True

@when("click", "#send_ble")
def on_send_ble(event):
    print(ble_info.value)
    ble.write(ble_info.value)

#--------------------------- controlling the ball --------------------------------

def stop_simulation(event):
    print('stop simulation')

# stop_button = document.getElementById("stop")
# stop_button.onclick = stop_simulation

#--------------------------- UART communication with openMV camera -----------------------------
uart_code = '''
from hub import uart
import time

U = uart.init(0,115200,100) #make sure the baud rate matches the baud rate of the openMV camera. In this case: 115200

#other custom CEEO uart functions. Download the firmware onto your spike here: https://raw.githack.com/tuftsceeo/SPIKE-html/main/index.html
#BEWARE OF SLIGHT MOTOR ISSUES WITH THIS FIRMWARE -- in other words, running motors sometimes has a strange oscillation affect
#U.write("hello there")
#U.read(4)
#U.readline()
#U.readuntil("b")
#U.any()
#U.readchar()
#U.txdone()
#U.status()


while(U.status() != "MODE_UART"):
    ...

while(1):
    b = U.any()
    message = U.read(b)
    messStr = str(message)[2:-3]
    print('messStr: ', messStr)
    print('message: ', message)
    time.sleep(1)
'''

# async def uart_codeFunc(event):
#     print('running uart code')
#     await terminal.eval(uart_code)

# document.getElementById("uartTest").onclick = uart_codeFunc