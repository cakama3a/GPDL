import time
import serial
from serial.tools import list_ports
from colorama import Fore, Style
import json
import numpy as np
import uuid
from tqdm import tqdm

ver = "3.0.9.3-MethodTest"  # Version for method testing
repeat = 2000  # Number of test repetitions
max_pause = 33  # Maximum pause between tests

# Function to connect to COM port with retry
def connect_to_com_port(port, baud_rate=115200, max_attempts=5):
    attempts = 0
    while attempts < max_attempts:
        try:
            ser = serial.Serial(port, baud_rate)
            print(f"\033[32mSuccessfully connected to {port}\033[0m")
            return ser
        except serial.SerialException as e:
            attempts += 1
            print(f"\033[31mAttempt {attempts}/{max_attempts}: Error connecting to {port}: {e}\033[0m")
            if attempts < max_attempts:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"\033[31mFailed to connect after {max_attempts} attempts. Exiting.\033[0m")
                exit(1)

# Display program header
print(f" ")
print(f" ")
print("   ██████╗ ██████╗ ██████╗ " + Fore.LIGHTRED_EX + "██╗     " + Fore.RESET + "")
print("  ██╔════╝ ██╔══██╗██╔══██╗" + Fore.LIGHTRED_EX + "██║     " + Fore.RESET + Fore.LIGHTRED_EX + "    " + "Method Latency Test" + Fore.RESET + " " + ver)
print("  ██║  ███╗██████╔╝██║  ██║" + Fore.LIGHTRED_EX + "██║     " + Fore.RESET + "    Modified for measuring")
print("  ██║   ██║██╔═══╝ ██║  ██║" + Fore.LIGHTRED_EX + "██║     " + Fore.RESET + "    the latency of the testing method itself")
print("  ╚██████╔╝██║     ██████╔╝" + Fore.LIGHTRED_EX + "███████╗" + Fore.RESET + "")
print("   ╚═════╝ ╚═╝     ╚═════╝ " + Fore.LIGHTRED_EX + "╚══════╝" + Fore.RESET + "")
print(f" ")
print(f" ")

# Get list of available COM ports
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
    ser = connect_to_com_port(port)
except Exception as e:
    print(f"\033[31mUnexpected error: {e}\033[0m")
    exit(1)

# Use button test mode as in the original script
button_pin = 2
down = "L"
up = "H"
method = "METHOD_TEST"

# Send button_pin to Arduino
print(f"Sending pin {button_pin} to Arduino...")
ser.write(f"{button_pin}\n".encode())

# Inform user and start test
print("\nTest will start in 2 seconds...")
time.sleep(2)

counter = 0
delays = []

# Function to filter outliers from array
def filter_outliers(array):
    lower_quantile = 0.02
    upper_quantile = 0.995
    sorted_array = sorted(array)
    lower_index = int(len(sorted_array) * lower_quantile)
    upper_index = int(len(sorted_array) * upper_quantile)
    return sorted_array[lower_index:upper_index + 1]

# Function to sleep for specified milliseconds
def sleep_ms(milliseconds):
    seconds = milliseconds / 1000.0
    if seconds < 0:
        seconds = 0
    time.sleep(seconds)

# Initial press for calibration
sleep_ms(2000)
ser.write(str(down).encode())
sleep_ms(100)
ser.write(str(up).encode())
sleep_ms(1000)

# Clear input buffer before starting the test
ser.reset_input_buffer()

# Initialize progress bar for the test
with tqdm(total=repeat, ncols=76, bar_format='{l_bar}{bar} | {postfix[0]}', dynamic_ncols=False, postfix=[0]) as pbar:
    while counter < repeat:
        # Send DOWN signal
        start = time.perf_counter()
        ser.write(str(down).encode())
        
        # Wait for Arduino to process the command and send a response
        while ser.in_waiting == 0:
            # Small delay to avoid CPU overload
            sleep_ms(0.5)
            
        # Get response and record time
        response = ser.read(1)
        end = time.perf_counter()
        
        # Calculate delay
        delay = round((end - start) * 1000, 2)
        
        # Return button to initial state
        ser.write(str(up).encode())
        
        # Check for valid delay
        if delay < 150:
            delays.append(delay)
            
            # Update progress bar
            pbar.postfix[0] = "{:05.2f} ms".format(delay)
            pbar.update(1)
            counter += 1
            
            # Dynamically adjust maximum pause
            if (delay + 16 > max_pause):
                max_pause = round(delay + 33)
                if max_pause > 100:
                    max_pause = 100
                
            sleep = max_pause - delay
            sleep_ms(sleep)
        else:
            # Skip too long delays
            sleep_ms(100)

# Statistical analysis of delays
str_of_numbers = ', '.join(map(str, delays))
delay_list = filter_outliers(delays)

filteredMin = min(delay_list)
filteredMax = max(delay_list)
filteredAverage = np.mean(delay_list)
filteredAverage_rounded = round(filteredAverage, 2)

polling_rate = round(1000 / filteredAverage, 2)
jitter = np.std(delay_list)
jitter = round(jitter, 2)

# Display test results
print(f" ")
print(f"\033[1mMethod Latency Test Results:\033[0m")
print(f"------------------------------------------")
print(f"Test type:          Method")
print(f" ")
print(f"Minimum latency:    {filteredMin} ms")
print(f"Average latency:    {filteredAverage_rounded} ms")
print(f"Maximum latency:    {filteredMax} ms")
print(f" ")
print(f"Jitter:             {jitter} ms")
print(f"------------------------------------------")
print(f" ")

# Save test data locally
test_data = {
    'version': ver,
    'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
    'sleep_time': sleep,
    'min_latency': filteredMin,
    'avg_latency': filteredAverage_rounded,
    'max_latency': filteredMax,
    'polling_rate': polling_rate,
    'jitter': jitter,
    'method': method,
    'delay_list': str_of_numbers
}

with open('method_test_data.txt', 'w') as outfile:
    json.dump(test_data, outfile, indent=4)

# Close serial connection
ser.close()

print("Test results saved to method_test_data.txt file")
input("Press Enter to exit...")
exit(0)