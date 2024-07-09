ver = "2.2.3"
repeat = 200
max_pause = 33

from colorama import Fore, Back, Style
import serial
from serial.tools import list_ports
import platform
import numpy as np
import time
from tqdm import tqdm # Додано бібліотеку для створення прогрес бару (Added a library to create a progress bar)
import pygame
from pygame.locals import *
pygame.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

# Виходимл якщо геймпадів не знайдено (No gamepads were found)
if not joysticks:
    print(" ")
    print("\033[31mNo connected gamepads found!\033[0m")
    input("Press Enter to exit...")
    exit(1)

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
print("\033[33mAttention:\033[0m If your gamepad is connected in wired mode, only one (Red) tester wire should be connected!")
for i, joystick in enumerate(joysticks):
    print(f"{i + 1} - {joystick.get_name()}")

try:
    joystick_num = int(input("Enter the gamepad number: ")) - 1
    joystick = joysticks[joystick_num]
    joystick.init()
except IndexError: # Виходимо з програми якщо обратинй неправильний геймпад (Exit the program if you select the wrong gamepad)
    print("\033[31mInvalid gamepad number!\033[0m")
    input("Press Enter to exit...")
    exit(1)

print(" ")
print("The test will begin in 3 seconds...")
print("\033[33mIf the bar does not progress, try swapping the contacts.\033[0m")

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

# Отримання відхилення стіку
def read_gamepad_axis(joystick):
    for event in pygame.event.get():
        if event.type == JOYAXISMOTION and event.joy == joystick.get_id():
            # Вибираємо лише осі стіків (0 і 1 для лівого стіку, 3 і 4 для правого стіку)
            stick_axes = [joystick.get_axis(i) for i in [2, 3]]
            # print("Axis values:", stick_axes)
            if any(abs(value) >= 0.99 for value in stick_axes):
                return True
    return False

def sleep_ms(milliseconds):
    seconds = milliseconds / 1000.0
    if seconds < 0:
        seconds = 0  # Переконуємося, що час сну не є негативним
    time.sleep(seconds)

sleep_ms(2000)

while counter < repeat:
    ser.write(str("L").encode()) # Посилаємо сигнал натискання кнопки (send a button press signal)
    start = time.perf_counter()  # Використовуйте time.perf_counter() (start a timer)
    while True: # Цикл очікування на натискання (click wait cycle)
        current_time = time.perf_counter()
        elapsed_time = (current_time - start) * 1000  # в мілісекундах
        button_state = read_gamepad_axis(joystick) # Статус зміни кнопки (Button change status)
        if button_state:  # Якщо кнопка була натиснута (button was pressed)
            end = current_time  # Використовуйте time.perf_counter() (end timer)
            delay = end - start # timer duration
            delay = round(delay * 1000, 2)
            ser.write(str("H").encode()) # Посилаємо сигнал на підняття кнопки (send raise the button signal)
            if delay >= 0.28 and delay < 150:
                delays.append(delay)
                print(f"Delay: {delay:.2f} ms")
                counter += 1

            # Динамічний розмір паузи (dynamic pause size)
            if (delay + 16 > max_pause):
                max_pause = round(delay + 33)
                if max_pause > 100: # Якщо пауза задовга, зменьшуємо її (If the pause is too long, reduce it).
                    max_pause = 100

            sleep = max_pause - delay
            sleep_ms(sleep)
            break

        if elapsed_time > 400:  # Примусовий вихід з циклу через 400 мс (Forced exit from the cycle after 400 ms)
            ser.write(str("H").encode())
            sleep_ms(100)
            break

        sleep_ms(1) # Обмежуємо швидкчть вторинного циклу (limit the speed of the secondary cycle)

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

# Якщо омилка в розрахунках (if there is a mistake in the calculations)
if filteredAverage_rounded > 500:
    print("\033[31mThe test failed with errors. The result will not be saved!\033[0m")
    answer = input('Quit (Y/N): ').lower()
    if answer == 'y':
        exit(1)

answer = input('Quit (Y/N): ').lower()
if answer == 'y':
    exit(1)
