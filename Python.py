import serial
from serial.tools import list_ports
import pygame
import json
import requests
import webbrowser
import platform
import numpy as np
import time
import uuid
from pygame.locals import *

# Додано бібліотеку для створення прогрес бару
from tqdm import tqdm

ver = "2.0.1"
repeat = 1984

pygame.init()

print(f" ")
print(f"   ██████╗  █████╗ ███╗   ███╗███████╗██████╗  █████╗ ██████╗ ██╗      █████╗ ")
print(f"  ██╔════╝ ██╔══██╗████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔══██╗██║     ██╔══██╗")
print(f"  ██║  ███╗███████║██╔████╔██║█████╗  ██████╔╝███████║██║  ██║██║     ███████║")
print(f"  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ██╔═══╝ ██╔══██║██║  ██║██║     ██╔══██║")
print(f"  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║     ██║  ██║██████╔╝███████╗██║  ██║")
print(f"   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝")
print("                                         by John Punch: https://t.me/ivanpunch")

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

if not joysticks:
    print("No connected gamepads found")
    time.sleep(5)  # Затримка на 5 секунд
    exit()

# Вибір геймпаду
print("Available gamepads:")
for i, joystick in enumerate(joysticks):
    print(f"{i + 1} - {joystick.get_name()}")

try:
    joystick_num = int(input("Enter the gamepad number: ")) - 1
    joystick = joysticks[joystick_num]
    joystick.init()
except IndexError:
    print("Invalid gamepad number. Exiting.")
    time.sleep(5)  # Затримка на 5 секунд
    exit()

joystick = joysticks[joystick_num]
joystick.init()

joystick_name = joystick.get_name()
print(f"Gamepad mode: {joystick_name}")

# Обираємо порт
available_ports = [port.device for port in list_ports.comports()]
print(f" ")
print("Available COM ports:")
for i, port in enumerate(available_ports):
    port_name = list_ports.comports()[i].description
    print(f"{i + 1} - {port_name}")

port_num = int(input("Enter the COM port number for GPDL: ")) - 1
try:
    port = available_ports[port_num] 
except IndexError:
    print("Invalid COM port number. Exiting.")
    time.sleep(5)  # Затримка на 5 секунд
    exit()

arduino_port = available_ports[port_num]

ser = serial.Serial(arduino_port, 115200)

# Обираємо тип підключення
print(f" ")
connection = input("Please select connection type (1. Cable, 2. Bluetooth, 3. Dongle): ")
if connection == "1":
    connection = "Cable"
elif connection == "2":
    connection = "Bluetooth"
elif connection == "3":
    connection = "Dongle"
else:
    print("Invalid choice. Defaulting to Cable.")
    connection = "Unset"

# Вписуємо назву геймпаду
print(f" ")
gamepad_name = input("Please enter the name of your gamepad: ")

print(f" ")
repeatq = input("Please select number of tests (1. 2000, 2. 4000, 3. 6000), or enter your own number: ")
if repeatq == "1":
    repeat = 2000
elif repeatq == "2":
    repeat = 4000
elif repeatq == "3":
    repeat = 6000
else:
    try:
        repeat = int(repeatq)
    except ValueError:
        print("Invalid input. Please enter a valid number.")

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

def read_gamepad_button(joystick):
    for event in pygame.event.get():
        if event.type == JOYBUTTONDOWN:
            return True
    return False

# Вибір геймпада
joystick = joysticks[0]
joystick.init()

# Додано прогрес бар
with tqdm(total=repeat, ncols=76, bar_format='{l_bar}{bar} | {postfix[0]}', postfix=[0]) as pbar:
    while counter < repeat:
        button_state = read_gamepad_button(joystick)
        if button_state and not prev_button_state:
            ser.write(str("pong\n").encode())
        prev_button_state = button_state

        if ser.in_waiting > 0:
            counter += 1
            delay = ser.readline().decode("utf-8").strip()
            delay = round(float(delay), 2)
            delays.append(delay)
            pbar.update(1)  # Оновлюємо прогрес бар
            #pbar.postfix[0] = f"{int(delay):02d}.{int(delay * 10):02d} ms" # Встановлюємо поточну затримку
            pbar.postfix[0] = "{:05.2f} ms".format(delay)

        pygame.event.pump()

str_of_numbers = ', '.join(map(str, delays))
delay_list = filter_outliers(delays)

filteredMin = min(delay_list)
filteredMax = max(delay_list)
filteredAverage = np.mean(delay_list)
filteredAverage_rounded = round(filteredAverage, 2)

# polling_rate = round(1000 / filteredAverage, 2)
jitter = np.std(delay_list)
jitter = round(jitter, 2)

# print(f" ")
# print(f"List:")
# print(f"{delay_list}")
print(f" ")
print(f"Gamepad mode:       {joystick.get_name()}")
print(f"===")
print(f"Minimal latency:    {filteredMin} ms")
print(f"Average latency:    {filteredAverage_rounded} ms")
print(f"Maximum latency:    {filteredMax} ms")
print(f"===")
# print(f"Polling Rate:       {polling_rate} Hz")
print(f"Jitter:             {jitter} ms")

# Генеруємо унікальний ключ ідентифікатора
test_key = uuid.uuid4()
# Отримати інформацію про операційну систему
os_name = platform.system()  # Назва операційної системи
os_version = platform.release()  # Версія операційної системи

data = {
    'test_key': str(test_key),
    'version': ver,
    'url': 'https://gamepadla.com',
    'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
    'driver': joystick_name,
    'connection': connection,
    'name': gamepad_name,
    'os_name': os_name,
    'os_version': os_version,
    'min_latency': filteredMin,
    'avg_latency': filteredAverage_rounded,
    'max_latency': filteredMax,
    'polling_rate': '',
    'jitter': jitter,
    'mathod': 'ARD',
    'delay_list': str_of_numbers
}

# Відправка на сервер
response = requests.post('https://gamepadla.com/scripts/poster.php', data=data)
if response.status_code == 200:
    print("Test results successfully sent to the server.")
    # Перенаправляємо користувача на сторінку з результатами тесту
    webbrowser.open(f'https://gamepadla.com/result/{test_key}/')
else:
    print("Failed to send test results to the server.")

# Записуємо дані в файл з відступами для кращої читабельності
with open('data.txt', 'w') as outfile:
    json.dump(data, outfile, indent=4)