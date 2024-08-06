ver = "3.0.1"
repeat = 2000
max_pause = 33

# Import necessary libraries
from colorama import Fore, Back, Style
import serial
from serial.tools import list_ports
import json
import requests
import webbrowser
import platform
import numpy as np
import time
import uuid
from tqdm import tqdm
import pygame
from pygame.locals import *

# Initialize pygame
pygame.init()

# Print welcome messages
print(f" ")
print(f" ")
print("   ██████╗ ██████╗ ██████╗ " + Fore.LIGHTRED_EX + "██╗     " + Fore.RESET + "")
print("  ██╔════╝ ██╔══██╗██╔══██╗" + Fore.LIGHTRED_EX + "██║     " + Fore.RESET + Fore.LIGHTRED_EX + "    " + "Gamepad Latency Tester" + Fore.RESET + " " + ver)
print("  ██║  ███╗██████╔╝██║  ██║" + Fore.LIGHTRED_EX + "██║     " + Fore.RESET + "    Website: https://gamepadla.com")
print("  ██║   ██║██╔═══╝ ██║  ██║" + Fore.LIGHTRED_EX + "██║     " + Fore.RESET + "    Author: John Punch")
print("  ╚██████╔╝██║     ██████╔╝" + Fore.LIGHTRED_EX + "███████╗" + Fore.RESET + "")
print("   ╚═════╝ ╚═╝     ╚═════╝ " + Fore.LIGHTRED_EX + "╚══════╝" + Fore.RESET + "")
print(f" ")
print(f" ")

# Display credits and links
print(f"Credits:")
print(f"My Reddit page: https://reddit.com/user/JohnnyPunch")
print(f"Support Me: https://ko-fi.com/gamepadla")
print(f"---")

# Get a list of connected joysticks
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

# Check if any joystick is connected
if not joysticks:
    print(" ")
    print("\033[31mNo connected gamepads found!\033[0m")
    input("Press Enter to exit...")
    exit(1)

# List available COM ports
available_ports = [port.device for port in list_ports.comports()]
print(" ")
print("Available COM ports:")
for i, port in enumerate(available_ports):
    port_name = list_ports.comports()[i].description
    print(f"{i + 1} - {port_name}")

print("\033[33m* Notice: You must have a GPDL device to test!\033[0m")

# Prompt user to enter COM port number for GPDL
port_num = int(input("Enter the COM port number for GPDL: ")) - 1
try:
    port = available_ports[port_num]
except IndexError:
    print("\033[31mInvalid COM port number. Exiting.\033[0m")
    time.sleep(5)
    exit()

# Connect to the specified COM port
try:
    ser = serial.Serial(port, 115200)
except serial.SerialException as e:
    print(f"\033[31mError opening {port}: {e}\033[0m")
    time.sleep(5)
    exit()

# List available gamepads
print(" ")
print("Available gamepads:")
print("\033[33mAttention:\033[0m If your gamepad is connected in wired mode, only one (Red) tester wire should be connected!")
for i, joystick in enumerate(joysticks):
    print(f"{i + 1} - {joystick.get_name()}")

# Prompt user to select gamepad number
try:
    joystick_num = int(input("Enter the gamepad number: ")) - 1
    joystick = joysticks[joystick_num]
    joystick.init()
except IndexError:
    print("\033[31mInvalid gamepad number!\033[0m")
    input("Press Enter to exit...")
    exit(1)

# Add a 3-second delay
print("\nPreparing to choose test type...")
time.sleep(3)

# Prompt user to select test type (Button test or Stick test)
print(" ")
print("Choose test type:")
print("\033[33mAttention:\033[0m Do not mix up the modes, otherwise you may damage the gamepad.")
test_type = input("1 for Button test, 2 for Stick test: ")

# Set variables based on selected test type
if test_type == '1':
    button_pin = 2  # Pin number for Button test
    down = "L"      # Command to press the button
    up = "H"        # Command to release the button
    method = "ARD"  # Method identifier
elif test_type == '2':
    button_pin = 8  # Pin number for Stick test
    down = "H"      # Command to move the stick
    up = "L"        # Command to stop moving the stick
    method = "STK"  # Method identifier
else:
    print("\033[31mInvalid test type. Exiting.\033[0m")
    ser.close()
    exit(1)

# Send button_pin to Arduino
ser.write(f"{button_pin}\n".encode())

# Inform user and start the test
print(" ")
print("The test will begin in 2 seconds...")
print("\033[33mIf the bar does not progress, try swapping the contacts.\033[0m")

counter = 0
delays = []
prev_button_state = False

# Function to filter outliers from an array
def filter_outliers(array):
    lower_quantile = 0.02
    upper_quantile = 0.995
    sorted_array = sorted(array)
    lower_index = int(len(sorted_array) * lower_quantile)
    upper_index = int(len(sorted_array) * upper_quantile)
    return sorted_array[lower_index:upper_index + 1]

# Function to read gamepad button state
def read_gamepad_button(joystick):
    for event in pygame.event.get():
        if event.type == JOYBUTTONDOWN and event.joy == joystick.get_id():
            return True
    return False

# Function to read gamepad stick axis state
def read_gamepad_axis(joystick):
    for event in pygame.event.get():
        if event.type == JOYAXISMOTION and event.joy == joystick.get_id():
            stick_axes = [joystick.get_axis(i) for i in [2, 3]]
            if any(abs(value) >= 0.99 for value in stick_axes):
                return True
    return False

# Function to sleep for specified milliseconds
def sleep_ms(milliseconds):
    seconds = milliseconds / 1000.0
    if seconds < 0:
        seconds = 0
    time.sleep(seconds)

# Initial button press and release for calibration
sleep_ms(2000)
ser.write(str(down).encode())
sleep_ms(100)
ser.write(str(up).encode())
sleep_ms(1000)

# Initialize progress bar for the test
with tqdm(total=repeat, ncols=76, bar_format='{l_bar}{bar} | {postfix[0]}', dynamic_ncols=False, postfix=[0]) as pbar:
    while counter < repeat:
        ser.write(str(down).encode())
        
        start = time.perf_counter()
        while True:
            current_time = time.perf_counter()
            elapsed_time = (current_time - start) * 1000
            button_state = read_gamepad_button(joystick) if test_type == '1' else read_gamepad_axis(joystick)
            if button_state:
                end = current_time
                delay = end - start
                delay = round(delay * 1000, 2)
                ser.write(str(up).encode())
                
                # Record delays within valid range
                if delay >= 0.28 and delay < 150:
                    delays.append(delay)
                    pbar.postfix[0] = "{:05.2f} ms".format(delay)
                    pbar.update(1)
                    counter += 1

                # Adjust maximum pause time dynamically
                if (delay + 16 > max_pause):
                    max_pause = round(delay + 33)
                    if max_pause > 100:
                        max_pause = 100

                sleep = max_pause - delay
                sleep_ms(sleep)
                break

            # Abort if no response within 400 ms
            if elapsed_time > 400:
                ser.write(str(up).encode())
                sleep_ms(100)
                break

            sleep_ms(1)

# Perform statistical analysis on recorded delays
str_of_numbers = ', '.join(map(str, delays))
delay_list = filter_outliers(delays)

filteredMin = min(delay_list)
filteredMax = max(delay_list)
filteredAverage = np.mean(delay_list)
filteredAverage_rounded = round(filteredAverage, 2)

polling_rate = round(1000 / filteredAverage, 2)
jitter = np.std(delay_list)
jitter = round(jitter, 2)

# Retrieve OS information
os_name = platform.system()
uname = platform.uname()
os_version = uname.version

# Display test results
print(f" ")
print(f"\033[1mTest results:\033[0m")
print(f"------------------------------------------")
print(f"OS:                 {os_name} {os_version}")
print(f"Gamepad mode:       {joystick.get_name()}")
print(f" ")
print(f"Minimal latency:    {filteredMin} ms")
print(f"Average latency:    {filteredAverage_rounded} ms")
print(f"Maximum latency:    {filteredMax} ms")
print(f" ")
print(f"Jitter:             {jitter} ms")
print(f"------------------------------------------")
print(f" ")

# Перехід на gamepadla.com (go to gamepadla.com)
answer = input('Open test results on the website (Y/N): ').lower()
if answer != 'y':
    exit(1)

# Prepare data for upload to server
test_key = uuid.uuid4()
gamepad_name = input("Gamepad name: ")

connection = input("Current connection (1. Cable, 2. Bluetooth, 3. Dongle): ")
if connection == "1":
    connection = "Cable"
elif connection == "2":
    connection = "Bluetooth"
elif connection == "3":
    connection = "Dongle"
else:
    print("Invalid choice. Defaulting to Unset.")
    connection = "Unset"

data = {
    'test_key': str(test_key),
    'version': ver,
    'url': 'https://gamepadla.com',
    'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
    'driver': joystick.get_name(),
    'connection': connection,
    'name': gamepad_name,
    'os_name': os_name,
    'sleep_time': sleep,
    'os_version': os_version,
    'min_latency': filteredMin,
    'avg_latency': filteredAverage_rounded,
    'max_latency': filteredMax,
    'polling_rate': polling_rate,
    'jitter': jitter,
    'mathod': method,
    'delay_list': str_of_numbers
}

# Send data to server and open results page
response = requests.post('https://gamepadla.com/scripts/poster.php', data=data)
if response.status_code == 200:
    print("Test results successfully sent to the server.")
    webbrowser.open(f'https://gamepadla.com/result/{test_key}/')
else:
    print("Failed to send test results to the server.")

# Save test data locally
with open('test_data.txt', 'w') as outfile:
    json.dump(data, outfile, indent=4)

# Prompt user to quit
answer = input('Quit (Y/N): ').lower()
if answer == 'y':
    exit(1)
