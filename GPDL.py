ver = "3.0.83"  # Updated version
repeat = 2000
max_pause = 33
stick_treshold = 0.99  # Threshold for detecting valid axis values

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
else:
    print("\033[31mInvalid test type. Exiting.\033[0m")
    ser.close()
    exit(1)

if test_type in ['2', '3']:
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

    # Initialize tracking for invalid test (positive and negative X axis detection)
    positive_x_detected = False
    negative_x_detected = False

# Prompt user for Reverse mode
reverse = 0
# print("\n\033[1mReverse Mode:\033[0m")
# print("This mode reverses the polling type (LOW becomes HIGH, and HIGH becomes LOW).")
# print("\033[33mOnly activate this mode if the standard mode doesn't work.\033[0m")
# print("\033[33mIn most cases, you should NOT use Reverse mode.\033[0m")
# reverse_mode = input("Do you want to activate Reverse mode? (y/N): ").lower() == 'y'

# if reverse_mode:
#     reverse = 1
#     down, up = up, down  # Swap the values of down and up
#     print("\033[38;5;208mReverse mode activated. Use with caution.\033[0m")
# else:
#     print("Standard mode selected.")

# Send button_pin to Arduino
ser.write(f"{button_pin}\n".encode())

# Inform user and start the test
print("\nThe test will begin in 2 seconds...")
print("\033[33mIf the bar does not progress, the program will automatically try to swap the test mode.\033[0m")
time.sleep(2)

counter = 0
delays = []
prev_button_state = False
invalid_test = False  # Track if the test is invalid

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
            stick_axes = [joystick.get_axis(i) for i in stick_axes_indices]
            if any(stick_treshold <= value <= 1 for value in stick_axes) or any(-1 <= value <= -stick_treshold for value in stick_axes):
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

                if test_type in ['2', '3']:  # Only for stick test
                    # Get current stick position for detection
                    stick_position_x = joystick.get_axis(stick_axes_indices[0])  # X axis
                    stick_position_y = joystick.get_axis(stick_axes_indices[1])  # Y axis

                    # Round the values for display
                    stick_position_x_rounded = round(stick_position_x, 2)
                    stick_position_y_rounded = round(stick_position_y, 2)

                    # Check if both positive and negative X detected using threshold
                    if stick_position_x_rounded >= stick_treshold:
                        positive_x_detected = True
                    elif stick_position_x_rounded <= -stick_treshold:
                        negative_x_detected = True

                    # If both positive and negative X detected, mark test as invalid
                    if positive_x_detected and negative_x_detected:
                        invalid_test = True
                        pbar.bar_format = '{l_bar}{bar} ' + Fore.RED + '| {postfix[0]}' + Fore.RESET  # Change progress bar color to red

                # Record delays within valid range
                if delay >= 0.28 and delay < 150:
                    delays.append(delay)
                    
                    # Update progress bar for button or stick test
                    if test_type == '1':  # For button test, no need to show coordinates
                        pbar.postfix[0] = "{:05.2f} ms".format(delay)
                    elif test_type in ['2', '3']:  # For stick test, show X and Y coordinates
                        pbar.postfix[0] = "{:05.2f} ms | X: {:05.2f}, Y: {:05.2f}".format(delay, stick_position_x_rounded, stick_position_y_rounded)

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

# Check if test is invalid due to both positive and negative X detections
if invalid_test:
    print(Fore.RED + "\nWarning: The test detected input on both positive and negative X axes, which indicates improper wiring. The test is not valid." + Fore.RESET)
    print("\033[31mTest results cannot be submitted to the server.\033[0m")
    # Prompt user to quit
    answer = input('Quit (Y/N): ').lower()
    if answer == 'y':
        exit(1)

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
    'reverse': reverse,
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
