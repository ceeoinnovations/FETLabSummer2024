import asyncio
from pyscript.js_modules import mqtt_library
from pyscript import document, window, when
from datetime import datetime, timedelta
import andrea_terminal
import restapi
import file_transfer
import file_os
import json

##############################################
#               Terminal Code                #
##############################################

ARDUINO_NANO = 128
SPIKE = 256
path = "https://raw.githubusercontent.com/chrisbuerginrogers/SPIKE_Prime/main/BLE/BLE_CEEO.py"


async def on_connect(event):
    if terminal.connected:
        connect.innerText = 'connect up'
        await terminal.board.disconnect()
    else:
        await terminal.board.connect('repl')
        if terminal.connected:
            connect.innerText = 'disconnect'
            await file_os.getList(terminal, list)
            await terminal.eval('\x03', True)
    for b in btns:
        b.disabled = not terminal.connected


def on_disconnect():
    connect.innerText = 'connect up'
    python.code = ''
    list.options.length = 0
    terminal.update(0)


async def on_load(event):
    if terminal.connected:
        name = path.split('/')[-1]
        print('path, name: ', path, name)
        reply = await restapi.get(path)
        status = await terminal.download(name, reply)
        if not status:
            window.alert(f"Failed to load {name}")
    else:
        window.alert('connect to a processor first')


def handle_board(event):
    code = event.code
    if terminal.connected:
        await terminal.eval('\x05'+code+'\x04')
        terminal.focus()
        return False  # return False to avoid executing on browser
    else:
        return True


def on_select(event):
    python.code = await file_os.read_code(terminal, list)


def on_clear(event):
    python.code = ''


@when("click", "#test")
def on_test(event):
    python.code = test_code


@when("click", "#get_sensor_data")
def on_data(event):
    import json
    try:
        # Get the data from the terminal buffer
        data = terminal.buffer
        # Debug: Print the raw data
        print(f"Raw data:\n{data}")

        # Get the HTML element with id 'uvData'
        uv_data_element = document.getElementById('uvData')
        if not uv_data_element:
            print("Error: HTML element with id 'uvData' not found.")
            return

        # Split the data into lines
        data_lines = data.split('\n')
        # Debug: Print the split data lines
        print(f"Data lines:\n{data_lines}")

        # Filter lines that start with "UV Index: "
        uv_data_lines = [
            line for line in data_lines if line.startswith("UV Index: ")]
        # Debug: Print the filtered UV data lines
        print(f"UV data lines:\n{uv_data_lines}")

        # Create a list of dictionaries to convert to JSON
        uv_data_dicts = []
        start_hour = 9
        for i, line in enumerate(uv_data_lines):
            # Assuming the format is "UV Index: value"
            uv_value = line.replace("UV Index: ", "").strip()
            data_dict = {"UV Index": uv_value, "time": f"{start_hour + i}:00"}
            uv_data_dicts.append(data_dict)

        # Debug: Print the list of dictionaries
        print(f"UV data dictionaries:\n{uv_data_dicts}")

        # Manually construct the JSON string
        uv_data_json = json.dumps(uv_data_dicts)

        # Debug: Print the JSON string
        print(f"UV data JSON:\n{uv_data_json}")

        # Set the JSON data as the inner text of the UV data element
        uv_data_element.innerText = uv_data_json
        global message
        message = uv_data_json

    except Exception as e:
        print(f"An error occurred: {e}")


connect = document.getElementById('connect')
library = document.getElementById('library')
progress_bar = document.getElementById('progress')
list = document.getElementById('files')
python = document.getElementById('mpCode')
remote = document.getElementById('upload')
clear = document.getElementById('clear')

connect.onclick = on_connect
library.onclick = on_load
# list.onchange = on_select
remote.onclick = on_select
clear.onclick = on_clear
python.handleEvent = handle_board

terminal = andrea_terminal.Terminal()
# terminal = file_transfer.Ampy(ARDUINO_NANO, progress_bar)
terminal.disconnect_callback = on_disconnect

btns = [library, remote, clear]
for b in btns:
    b.disabled = not terminal.connected


##############################################
#               MQTT CODE                    #
##############################################

myClient = mqtt_library.myClient
topic = 'Tufts_CEEO/uv_sensor'

dataUV = document.getElementById('uvData')


async def waitForMQTT():
    while not myClient.connected:
        await asyncio.sleep(0.1)


myClient.init()
await waitForMQTT()
myClient.subscribe('Tufts_CEEO/uv_sensor')


@when("click", "#colab")
def send_colab(event):
    msg = message
    myClient.publish(topic, msg)
