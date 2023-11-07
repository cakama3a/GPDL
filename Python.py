ver = "2.0.9"
print(f" ")
print(f" ")
print(f"   ██████╗  █████╗ ███╗   ███╗███████╗██████╗  █████╗ ██████╗ \033[38;5;208m██╗      █████╗ \033[0m")
print(f"  ██╔════╝ ██╔══██╗████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔══██╗\033[38;5;208m██║     ██╔══██╗\033[0m")
print(f"  ██║  ███╗███████║██╔████╔██║█████╗  ██████╔╝███████║██║  ██║\033[38;5;208m██║     ███████║\033[0m")
print(f"  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ██╔═══╝ ██╔══██║██║  ██║\033[38;5;208m██║     ██╔══██║\033[0m")
print(f"  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║     ██║  ██║██████╔╝\033[38;5;208m███████╗██║  ██║\033[0m")
print(f"   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═════╝ \033[38;5;208m╚══════╝╚═╝  ╚═╝\033[0m")
print(f"   \033[38;5;208mLatency GPDL Tester\033[0m " + ver + "                            https://gamepadla.com")
print(f" ")
print(f" ")
print(f"Credits:")

repeat = 2000

import serial
from serial.tools import list_ports
import pygame
import json
import requests
import webbrowser
import platform
import numpy as np
import time
import random
import uuid
from pygame.locals import *
from tqdm import tqdm # Додано бібліотеку для створення прогрес бару
print(f"The code was written by John Punch: https://reddit.com/user/JohnnyPunch")

pygame.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

# Виходимл якзо геймпадів не знайдено
if not joysticks:
    print(" ")
    print("\033[31mNo connected gamepads found! Exiting.\033[0m")
    time.sleep(5)  # Затримка на 5 секунд
    exit()

# Вибір геймпаду
print(" ")
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
    time.sleep(5)  # Затримка на 5 секунд
    exit()

# Підключаємося до ардуіно по порту
arduino_port = available_ports[port_num]
ser = serial.Serial(arduino_port, 115200)

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

# Натискання на кнопку конкретного геймпаду
def read_gamepad_button(joystick):
    for event in pygame.event.get():
        if event.type == JOYBUTTONDOWN and event.joy == joystick.get_id():
            return True
    return False


ser.write(str("H").encode())
with tqdm(total=repeat, ncols=76, bar_format='{l_bar}{bar} | {postfix[0]}', postfix=[0]) as pbar:
    while counter < repeat:
        ser.write(str("L").encode()) # Посилаємо сигнал натискання кнопки
        start = time.perf_counter()  # Використовуйте time.perf_counter()
        while True: # Цикл очікування на натискання
            button_state = read_gamepad_button(joystick) # Статус зміни кнопки
            if button_state:  # Якщо кнопка була натиснута
                ser.write(str("H").encode())
                end = time.perf_counter()  # Використовуйте time.perf_counter()
                delay = end - start
                delay = round(delay * 1000, 2)
                if delay >= 0.28 and delay < 150:
                    delays.append(delay)
                    pbar.postfix[0] = "{:05.2f} ms".format(delay)
                    pbar.update(1)  # Оновлюємо прогрес бар
                    counter += 1
                #time.sleep(random.uniform(0.066, 0.077))
                time.sleep(0.016)
                break
            
str_of_numbers = ', '.join(map(str, delays))
delay_list = filter_outliers(delays)

filteredMin = min(delay_list)
filteredMax = max(delay_list)
filteredAverage = np.mean(delay_list)
filteredAverage_rounded = round(filteredAverage, 2)

polling_rate = round(1000 / filteredAverage, 2)
jitter = np.std(delay_list)
jitter = round(jitter, 2)

# Отримати інформацію про операційну систему
os_name = platform.system()  # Назва операційної системи
os_version = platform.release()  # Версія операційної системи

# Вивід інформації
print(f" ")
print(f"\033[1mTest results:\033[0m")
print(f"------------------------------------------")
print(f"OS info:            {os_name} [{os_version}]")
print(f"Gamepad mode:       {joystick.get_name()}")
print(f" ")
print(f"Minimal latency:    {filteredMin} ms")
print(f"Average latency:    {filteredAverage_rounded} ms")
print(f"Maximum latency:    {filteredMax} ms")
print(f" ")
print(f"Polling Rate:       {polling_rate} Hz")
print(f"Jitter:             {jitter} ms")
print(f"------------------------------------------")
print(f" ")

# Генеруємо унікальний ключ ідентифікатора
test_key = uuid.uuid4()
# Отримати інформацію про операційну систему
os_name = platform.system()  # Назва операційної системи
os_version = platform.release()  # Версія операційної системи

# Якщо омилка в розрахунках
if filteredAverage_rounded > 500:
    print("\033[31mThe test failed with errors. The result will not be saved!\033[0m")
    answer = input('Quit (Y/N): ').lower()
    if answer == 'y':
        exit(1)

# Перехід на gamepadla.com
answer = input('Open test results on the website (Y/N): ').lower()
if answer != 'y':
    exit(1)

# Вписуємо назву геймпаду
gamepad_name = input("Gamepad name: ")

# Обираємо тип підключення
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

# Генеруємо унікальний ключ ідентифікатора
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
    'os_version': os_version,
    'min_latency': filteredMin,
    'avg_latency': filteredAverage_rounded,
    'max_latency': filteredMax,
    'polling_rate': polling_rate,
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

answer = input('Quit (Y/N): ').lower()
if answer == 'y':
    exit(1)