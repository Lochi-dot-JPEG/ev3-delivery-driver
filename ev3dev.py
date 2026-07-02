#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_4
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
from ev3dev2.sound import Sound
from ev3dev2.button import Button
from time import sleep
import evdev

# ----------------
# - define ports -
# ----------------
# Note: Motor and sensor objects use OUTPUT_X and INPUT_X
move_motor_l = LargeMotor(OUTPUT_B)
move_motor_r = LargeMotor(OUTPUT_C)
drop_motor = MediumMotor(OUTPUT_D)

stack_color_sensor = ColorSensor(INPUT_1)
line_color_sensor = ColorSensor(INPUT_2)
collision_sensor = UltrasonicSensor(INPUT_4)

ev3_sound = Sound()
ev3_btn = Button()

# --------------------
# - define constants -
# --------------------
# ev3dev2 uses speed_sp (Degrees Per Second or % with SpeedPercent)
DROP_SPEED = 1000  
TURN_SPEED = 200
LAGGING_LINE_FOLLOW_SPEED = 60
LINE_FOLLOW_SPEED = 100
LINE_THRESHOLD = 35

# ev3dev2 Color Mapping
COLOR_NONE = 0
COLOR_BLACK = 1
COLOR_BLUE = 2
COLOR_GREEN = 3
COLOR_YELLOW = 4
COLOR_RED = 5
COLOR_WHITE = 6
COLOR_BROWN = 7

# -----------------
# - Helper Methods -
# -----------------
def get_xbox_device():
    """Locates the Xbox controller in system devices."""
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if 'Xbox' in device.name:
                return device
    except Exception:
        pass
    return None

def DropItem():
    """Exact logic for dropping items using relative position."""
    drop_motor.run_to_rel_pos(speed_sp=DROP_SPEED, position_sp=180)
    drop_motor.wait_until_not_moving()
    drop_motor.run_to_rel_pos(speed_sp=DROP_SPEED, position_sp=-180)
    drop_motor.wait_until_not_moving()

def IsABlockColor(col):
    return col in [COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE]

def HouseColorToName(col):
    mapping = {COLOR_RED: "Koala", COLOR_GREEN: "Bird", 
               COLOR_YELLOW: "Rabbit", COLOR_BLUE: "Mr Mouse"}
    return mapping.get(col, False)

def ColorToName(col):
    mapping = {COLOR_RED: "Red", COLOR_GREEN: "Green", COLOR_BLUE: "Blue",
               COLOR_YELLOW: "Yellow", COLOR_BROWN: "Brown", 
               COLOR_BLACK: "Black", COLOR_WHITE: "White"}
    return mapping.get(col, "An error")

def Turn(angle):
    move_motor_l.run_to_rel_pos(speed_sp=TURN_SPEED, position_sp=angle*2)
    move_motor_r.run_to_rel_pos(speed_sp=TURN_SPEED, position_sp=-angle*2)
    move_motor_l.wait_until_not_moving()
    move_motor_r.wait_until_not_moving()

# -----------------
# - Robot Modes -
# -----------------
def LineFollow():
    while IsABlockColor(stack_color_sensor.color):
        searching_color = stack_color_sensor.color
        ev3_sound.speak("Delivery for the " + ColorToName(searching_color) + " house.")
        found_color = False
        while True:
            # rgb returns raw values (0-255); max(rgb) mimics reflection intensity
            rgb = line_color_sensor.rgb
            reflection = max(rgb)

            if reflection < LINE_THRESHOLD:
                move_motor_l.run_forever(speed_sp=-LAGGING_LINE_FOLLOW_SPEED)
                move_motor_r.run_forever(speed_sp=LINE_FOLLOW_SPEED)
            else:
                move_motor_l.run_forever(speed_sp=LAGGING_LINE_FOLLOW_SPEED)
                move_motor_r.run_forever(speed_sp=LINE_FOLLOW_SPEED)

            floor_colour = line_color_sensor.color
            if floor_colour == searching_color:
                found_color = True
            elif found_color and floor_colour == COLOR_WHITE:
                move_motor_l.stop()
                move_motor_r.stop()
                ev3_sound.speak("Your delivery is here " + HouseColorToName(searching_color))
                while floor_colour == searching_color:
                    DropItem()
                    sleep(0.1)
                    searching_color = stack_color_sensor.color
                break
            sleep(0.02)
        sleep(0.2)
    ev3_sound.speak("My deliveries are done.")

def xbox_control_mode():
    """Manual drive mode using Xbox joystick and buttons."""
    gamepad = get_xbox_device()
    if not gamepad:
        ev3_sound.speak("No controller found")
        return
    ev3_sound.speak("Controller connected")
    for event in gamepad.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            if event.code == evdev.ecodes.ABS_Y: # Left stick vertical axis
                # Standardize speed from joystick range
                val = -(event.value - 32768) // 32 
                move_motor_l.run_forever(speed_sp=val)
                move_motor_r.run_forever(speed_sp=val)
        elif event.type == evdev.ecodes.EV_KEY:
            if event.code == evdev.ecodes.BTN_A and event.value == 1:
                DropItem()
            if event.code == evdev.ecodes.BTN_B and event.value == 1:
                break # Exit Xbox mode back to main menu
    move_motor_l.stop()
    move_motor_r.stop()

def ScanReflection():
    while True:
        rgb = line_color_sensor.rgb
        print(max(rgb))
        if ev3_btn.up: break
        sleep(0.1)

def SayLine():
    ev3_sound.speak("I am ready to deliver some packages.")

# -----------------
# - Main Loop -
# -----------------
ev3_sound.beep()

while True:
    if ev3_btn.left:
        LineFollow()
    elif ev3_btn.right:
        SayLine()
    elif ev3_btn.down:
        DropItem()
    elif ev3_btn.up:
        ScanReflection()
    elif ev3_btn.enter: # Trigger the new Xbox Mode
        xbox_control_mode()
    sleep(0.1)
