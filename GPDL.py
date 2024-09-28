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

# Set constants
ver = "3.1.1"  # Updated version
repeat = 200  # Number of tests per threshold
max_pause = 33
thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

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
print(f"Guide to using GPDL: https://gamepadla.com/gpdl-tester-guide.pdl")
print("\033[33mDon't forget to update the firmware of GPDL device! https://gamepadla.com/updating-gpdl-firmware.pdl\033[0m")
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

if len(available_ports) == 1:
    port = available_ports[0]
    print(f"\033[32mOnly one COM port found. Automatically selected: {port}\033[0m")
else:
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
for i, joystick in enumerate(joysticks):
    print(f"{i + 1} - {joystick.get_name()}")

if len(joysticks) == 1:
    joystick = joysticks[0]
    joystick.init()
    print(f"\033[32mOnly one gamepad found. Automatically selected: {joystick.get_name()}\033[0m")
else:
    joystick_num = int(input("Enter the gamepad number: ")) - 1
    try:
        joystick = joysticks[joystick_num]
        joystick.init()
    except IndexError:
        print("\033[31mInvalid gamepad number!\033[0m")
        input("Press Enter to exit...")
        exit(1)

# Prompt user to select test type (Button test or Stick test)
print("\n\033[1mChoose Test Type:\033[0m")
print("1 - BUTTON latency test")
print("2 - STICK W/O Resistor")
print("\033[38;5;208m⚠  WARNING: DO NOT MIX UP THE MODES! Incorrect selection may damage your gamepad. ⚠\033[0m")
print("Wait 3 seconds...")
time.sleep(3)
test_type = input("Enter test type (1/2): ")

# Set variables based on selected test type
if test_type == '1':
    button_pin, down, up, method = 2, "L", "H", "ARD"  # Button test
elif test_type == '2':
    button_pin, down, up, method = 5, "L", "H", "STK"  # Stick test (WO Resistor mode)
    
    # Choose which stick to test (left or right)
    print("\n\033[1mChoose Stick to Test:\033[0m")
    print("1 - Left Stick")
    print("2 - Right Stick")
    stick_choice = input("Enter stick number (1 or 2): ")

    # Assign axes based on stick choice
    if stick_choice == '1':
        stick_axes_indices = [0, 1]  # Left stick uses axes 0 and 1
        print("Testing Left Stick")
    elif stick_choice == '2':
        stick_axes_indices = [2, 3]  # Right stick uses axes 2 and 3
        print("Testing Right Stick")
    else:
        print("\033[31mInvalid stick choice! Exiting.\033[0m")
        exit(1)
else:
    print("\033[31mInvalid test type. Exiting.\033[0m")
    ser.close()
    exit(1)

# Send button_pin to Arduino
ser.write(f"{button_pin}\n".encode())

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
def read_gamepad_axis(joystick, threshold):
    for event in pygame.event.get():
        if event.type == JOYAXISMOTION and event.joy == joystick.get_id():
            stick_axes = [joystick.get_axis(i) for i in stick_axes_indices]
            if any(threshold <= value <= 1 for value in stick_axes) or any(-1 <= value <= -threshold for value in stick_axes):
                return True
    return False

# Function to sleep for specified milliseconds
def sleep_ms(milliseconds):
    seconds = milliseconds / 1000.0
    if seconds < 0:
        seconds = 0
    time.sleep(seconds)

# Inform user and start the test
print("\nThe test will begin in 2 seconds...")
print("\033[33mIf the bar does not progress, try swapping the contacts.\033[0m")
time.sleep(2)

# Initialize variables for storing results
all_delays = {}
all_stats = {}

# Main test loop
if test_type == '1':  # Button test
    delays = []
    counter = 0
    
    with tqdm(total=repeat, ncols=76, bar_format='{l_bar}{bar} | {postfix[0]}', dynamic_ncols=False, postfix=[0]) as pbar:
        while counter < repeat:
            ser.write(str(down).encode())
            
            start = time.perf_counter()
            while True:
                current_time = time.perf_counter()
                elapsed_time = (current_time - start) * 1000
                button_state = read_gamepad_button(joystick)
                
                if button_state:
                    end = current_time
                    delay = round((end - start) * 1000, 2)
                    ser.write(str(up).encode())

                    if 0.28 <= delay < 150:
                        delays.append(delay)
                        pbar.postfix[0] = "{:05.2f} ms".format(delay)
                        pbar.update(1)
                        counter += 1

                    max_pause = min(round(delay + 33), 100)
                    sleep_ms(max_pause - delay)
                    break

                if elapsed_time > 400:
                    ser.write(str(up).encode())
                    sleep_ms(100)
                    break

                sleep_ms(1)
    
    all_delays['button'] = delays
    filtered_delays = filter_outliers(delays)
    all_stats['button'] = {
        'min': min(filtered_delays),
        'max': max(filtered_delays),
        'avg': round(np.mean(filtered_delays), 2),
        'jitter': round(np.std(filtered_delays), 2)
    }

else:  # Stick test
    for threshold in thresholds:
        delays = []
        counter = 0
        invalid_test = False
        positive_x_detected = False
        negative_x_detected = False

        print(f"\nTesting with threshold: {threshold}")
        
        with tqdm(total=repeat, ncols=76, bar_format='{l_bar}{bar} | {postfix[0]}', dynamic_ncols=False, postfix=[0]) as pbar:
            while counter < repeat:
                ser.write(str(down).encode())
                
                start = time.perf_counter()
                while True:
                    current_time = time.perf_counter()
                    elapsed_time = (current_time - start) * 1000
                    button_state = read_gamepad_axis(joystick, threshold)
                    
                    if button_state:
                        end = current_time
                        delay = round((end - start) * 1000, 2)
                        ser.write(str(up).encode())

                        stick_position_x = joystick.get_axis(stick_axes_indices[0])
                        stick_position_y = joystick.get_axis(stick_axes_indices[1])
                        stick_position_x_rounded = round(stick_position_x, 2)
                        stick_position_y_rounded = round(stick_position_y, 2)

                        if stick_position_x_rounded >= threshold:
                            positive_x_detected = True
                        elif stick_position_x_rounded <= -threshold:
                            negative_x_detected = True

                        if positive_x_detected and negative_x_detected:
                            invalid_test = True
                            pbar.bar_format = '{l_bar}{bar} ' + Fore.RED + '| {postfix[0]}' + Fore.RESET

                        if 0.28 <= delay < 150:
                            delays.append(delay)
                            pbar.postfix[0] = "{:05.2f} ms | X: {:05.2f}, Y: {:05.2f}".format(delay, stick_position_x_rounded, stick_position_y_rounded)
                            pbar.update(1)
                            counter += 1

                        max_pause = min(round(delay + 33), 100)
                        sleep_ms(max_pause - delay)
                        break

                    if elapsed_time > 400:
                        ser.write(str(up).encode())
                        sleep_ms(100)
                        break

                    sleep_ms(1)

        all_delays[threshold] = delays
        filtered_delays = filter_outliers(delays)
        all_stats[threshold] = {
            'min': min(filtered_delays),
            'max': max(filtered_delays),
            'avg': round(np.mean(filtered_delays), 2),
            'jitter': round(np.std(filtered_delays), 2)
        }

# Display test results
print(f"\n\033[1mTest results:\033[0m")
print(f"------------------------------------------")
print(f"OS:                 {platform.system()} {platform.uname().version}")
print(f"Gamepad mode:       {joystick.get_name()}")
print(f"Test type:          {'Button' if test_type == '1' else 'Stick'}")
print(f"------------------------------------------")

if test_type == '1':
    stats = all_stats['button']
    print(f"Minimal latency:    {stats['min']} ms")
    print(f"Average latency:    {stats['avg']} ms")
    print(f"Maximum latency:    {stats['max']} ms")
    print(f"Jitter:             {stats['jitter']} ms")
else:
    for threshold, stats in all_stats.items():
        print(f"\nResults for threshold {threshold}:")
        print(f"  Minimal latency:    {stats['min']} ms")
        print(f"  Average latency:    {stats['avg']} ms")
        print(f"  Maximum latency:    {stats['max']} ms")
        print(f"  Jitter:             {stats['jitter']} ms")

print(f"------------------------------------------")

if test_type == '2' and invalid_test:
    print(Fore.RED + "\nWarning: The test detected input on both positive and negative X axes, which indicates improper wiring. The test may not be valid." + Fore.RESET)

# Prepare data for upload to server
test_key = uuid.uuid4()
gamepad_name = input("Gamepad name: ")

connection = input("Current connection (1. Cable, 2. Bluetooth, 3. Dongle): ")
connection_options = {"1": "Cable", "2": "Bluetooth", "3": "Dongle"}
connection = connection_options.get(connection, "Unset")

data = {
    'test_key': str(test_key),
    'version': ver,
    'url': 'https://gamepadla.com',
    'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
    'driver': joystick.get_name(),
    'connection': connection,
    'name': gamepad_name,
    'os_name': platform.system(),
    'os_version': platform.uname().version,
    'method': method,
    'all_delays': json.dumps(all_delays),
    'all_stats': json.dumps(all_stats)
}

# Send data to server and open results page
response = requests.post('https://gamepadla.com/scripts/poster.php', data=data)
if response.status_code == 200:
    print("Test results successfully sent to the server.")
    webbrowser.open(f'https://gamepadla.com/result/{test_key}/')
else:
    print("Failed to send test results to the server.")

# Save test data locally
with open('test_data.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)

# Prompt user to quit
input("Press Enter to exit...")
exit(0)