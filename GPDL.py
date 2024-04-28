ver = "2.1.8"
repeat = 2000

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

from tqdm import tqdm # Додано бібліотеку для створення прогрес бару (Added a library to create a progress bar)

print(f" ")
print(f" ")
print("   ██████╗  █████╗ ███╗   ███╗███████╗██████╗  █████╗ ██████╗ " + Fore.LIGHTRED_EX + "██╗      █████╗ " + Fore.RESET)
print("  ██╔════╝ ██╔══██╗████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔══██╗" + Fore.LIGHTRED_EX + "██║     ██╔══██╗" + Fore.RESET)
print("  ██║  ███╗███████║██╔████╔██║█████╗  ██████╔╝███████║██║  ██║" + Fore.LIGHTRED_EX + "██║     ███████║" + Fore.RESET)
print("  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ██╔═══╝ ██╔══██║██║  ██║" + Fore.LIGHTRED_EX + "██║     ██╔══██║" + Fore.RESET)
print("  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║     ██║  ██║██████╔╝" + Fore.LIGHTRED_EX + "███████╗██║  ██║" + Fore.RESET)
print("   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═════╝ " + Fore.LIGHTRED_EX + "╚══════╝╚═╝  ╚═╝" + Fore.RESET)
print(Fore.LIGHTRED_EX + "    " + "GPDL Latency Tester" + Fore.RESET + "  " + ver + "                          https://gamepadla.com")
print(f" ")
print(f" ")

print(f"Credits:")
print(f"The code was written by John Punch: https://reddit.com/user/JohnnyPunch")
print(f"Support Me on: https://ko-fi.com/gamepadla")
print()
import pygame
from pygame.locals import *
pygame.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

# Виходимл якщо геймпадів не знайдено (No gamepads were found)
if not joysticks:
    print(" ")
    print("\033[31mNo connected gamepads found! Exiting.\033[0m")
    time.sleep(5)  # Затримка на 5 секунд (Delay for 5 seconds)
    exit()

# Обираємо порт
available_ports = [port.device for port in list_ports.comports()]
print(" ")
print("Available COM ports:")
for i, port in enumerate(available_ports):
    port_name = list_ports.comports()[i].description
    print(f"{i + 1} - {port_name}")

print("\033[33m* Notice: You must have a GPDL device to test!\033[0m")
port_num = int(input("Enter the COM port number for GPDL: ")) - 1
try:
    port = available_ports[port_num]
except IndexError:
    print("\033[31mInvalid COM port number. Exiting.\033[0m")
    time.sleep(5)  # Затримка на 5 секунд (Delay for 5 seconds)
    exit()
# Підключаємося до обраного COM-порту (connect to the selected COM port)
try:
    ser = serial.Serial(port, 115200)
except serial.SerialException as e:
    print(f"\033[31mError opening {port}: {e}\033[0m")
    time.sleep(5)  # Затримка на 5 секунд (Delay for 5 seconds)
    exit()

# Вибір геймпаду (Gamepad selection)
print(" ")
print("Available gamepads:")
print("\033[33mAttention:\033[0m When connecting a gamepad wired, connect only one pin of the tester!")
for i, joystick in enumerate(joysticks):
    print(f"{i + 1} - {joystick.get_name()}")

try:
    joystick_num = int(input("Enter the gamepad number: ")) - 1
    joystick = joysticks[joystick_num]
    joystick.init()
except IndexError:
    print("Invalid gamepad number. Exiting.")
    time.sleep(5)  # Затримка на 5 секунд (Delay for 5 seconds)
    exit()

connection_mode = 1

print(" ")
print("The test has started:")

counter = 0
delays = []
prev_button_state = False

def filter_outliers(array):
    lower_quantile = 0.02
    upper_quantile = 0.995
    sorted_array = sorted(array)
    lower_index = int(len(sorted_array) * lower_quantile)
    upper_index = int(len(sorted_array) * upper_quantile)
    return sorted_array[lower_index:upper_index + 1]

# Натискання на кнопку конкретного геймпаду (Check for press of a button on specific gamepad)
def read_gamepad_button(joystick):
    for event in pygame.event.get():
        if event.type == JOYBUTTONDOWN and event.joy == joystick.get_id():
            return True
    return False

def sleep_ms(milliseconds):
    seconds = milliseconds / 1000.0
    time.sleep(seconds)

sleep_ms(2000)

if connection_mode == 1:
    ser.write(str("H").encode()) # Відпускаємо кнопку (release the button)
else:
    ser.write(str("L").encode()) # Відпускаємо кнопку по одномк контакту (release the button for one contact)

sleep_ms(200)
max_pause = 33

with tqdm(total=repeat, ncols=76, bar_format='{l_bar}{bar} | {postfix[0]}', dynamic_ncols=False, postfix=[0]) as pbar:
    while counter < repeat:
        if connection_mode == 1:
            ser.write(str("L").encode()) # Посилаємо сигнал натискання кнопки (send a button press signal)
        else:
            ser.write(str("H").encode()) # Посилаємо сигнал натискання кнопки по одному контакту
        start = time.perf_counter()  # Використовуйте time.perf_counter() (start a timer)
        while True: # Цикл очікування на натискання (click wait cycle)
            button_state = read_gamepad_button(joystick) # Статус зміни кнопки (Button change status)
            if button_state:  # Якщо кнопка була натиснута (button was pressed)
                end = time.perf_counter()  # Використовуйте time.perf_counter() (end timer)
                delay = end - start # timer duration
                delay = round(delay * 1000, 2)
                ser.write(str("H").encode()) # Посилаємо сигнал на підняття кнопки (send raise the button signal)
                #print(delay)
                if delay >= 0.28 and delay < 150:
                    delays.append(delay)
                    pbar.postfix[0] = "{:05.2f} ms".format(delay)
                    pbar.update(1)  # Оновлюємо прогрес бар (update the progress bar)
                    counter += 1

                # Динамічний розмір паузи (dynamic pause size)
                if (delay + 16 > max_pause):
                    max_pause = round(delay + 33)

                sleep = max_pause-delay
                sleep_ms(sleep)
                break
            sleep_ms(1) # Обмежуємо швидкчть вторинного циклу (limit the speed of the secondary cycle)

str_of_numbers = ', '.join(map(str, delays))
delay_list = filter_outliers(delays)

filteredMin = min(delay_list)
filteredMax = max(delay_list)
filteredAverage = np.mean(delay_list)
filteredAverage_rounded = round(filteredAverage, 2)

polling_rate = round(1000 / filteredAverage, 2)
jitter = np.std(delay_list)
jitter = round(jitter, 2)

# OS Version
os_name = platform.system()  # Назва операційної системи (the name of the operating system)
uname = platform.uname()
os_version = uname.version

# Вивід інформації (output of information)
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
#print(f"Polling Rate:       {polling_rate} Hz")
print(f"Jitter:             {jitter} ms")
print(f"------------------------------------------")
#print(f"The results of the Polling rate test in this method are calculated very roughly and may differ significantly from the actual results.")
print(f" ")

# Генеруємо унікальний ключ ідентифікатора (we generate a unique identifier key)
test_key = uuid.uuid4()

# Якщо омилка в розрахунках (if there is a mistake in the calculations)
if filteredAverage_rounded > 500:
    print("\033[31mThe test failed with errors. The result will not be saved!\033[0m")
    answer = input('Quit (Y/N): ').lower()
    if answer == 'y':
        exit(1)

# Перехід на gamepadla.com (go to gamepadla.com)
answer = input('Open test results on the website (Y/N): ').lower()
if answer != 'y':
    exit(1)

# Вписуємо назву геймпаду (enter the name of the gamepad)
gamepad_name = input("Gamepad name: ")

# Обираємо тип підключення (select the connection type)
connection = input("Current connection (1. Cable, 2. Bluetooth, 3. Dongle): ")
if connection == "1":
    connection = "Cable"
elif connection == "2":
    connection = "Bluetooth"
elif connection == "3":
    connection = "Dongle"
else:
    print("Invalid choice. Defaulting to Cable.")
    connection = "Unset"

# Генеруємо унікальний ключ ідентифікатора (generate a unique identifier key)
test_key = uuid.uuid4()

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
    'mathod': 'ARD',
    'delay_list': str_of_numbers
}

# Відправка на сервер (sending to the server)
response = requests.post('https://gamepadla.com/scripts/poster.php', data=data)
if response.status_code == 200:
    print("Test results successfully sent to the server.")
    # Перенаправляємо користувача на сторінку з результатами тесту (redirect the user to the page with the test results)
    webbrowser.open(f'https://gamepadla.com/result/{test_key}/')
else:
    print("Failed to send test results to the server.")

# Записуємо дані в файл з відступами для кращої читабельності (describe the data in a file with indents for better readability)
with open('data.txt', 'w') as outfile:
    json.dump(data, outfile, indent=4)

answer = input('Quit (Y/N): ').lower()
if answer == 'y':
    exit(1)
