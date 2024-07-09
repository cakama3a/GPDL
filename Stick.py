import pygame
from pygame.locals import *

# Ініціалізація Pygame та джойстиків
pygame.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

if not joysticks:
    print("No connected gamepads found!")
    input("Press Enter to exit...")
    exit(1)

print("Available gamepads:")
for i, joystick in enumerate(joysticks):
    print(f"{i + 1} - {joystick.get_name()}")

try:
    joystick_num = int(input("Enter the gamepad number: ")) - 1
    joystick = joysticks[joystick_num]
    joystick.init()
except IndexError:
    print("Invalid gamepad number!")
    input("Press Enter to exit...")
    exit(1)

def read_gamepad_axis(joystick):
    for event in pygame.event.get():
        if event.type == JOYAXISMOTION and event.joy == joystick.get_id():
            # Вибираємо лише осі стіків (0 і 1 для лівого стіку, 3 і 4 для правого стіку)
            stick_axes = [joystick.get_axis(i) for i in [2, 3]]
            # print("Axis values:", stick_axes)
            if any(abs(value) >= 0.99 for value in stick_axes):
                return True
    return False

print("Move the joystick to its maximum position in any direction.")

while True:  # Безкінечний цикл
    if read_gamepad_axis(joystick):
        print("Axis moved to the edge.")
