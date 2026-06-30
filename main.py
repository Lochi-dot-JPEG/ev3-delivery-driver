#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
#from pybricks.iodevices import XboxController



ev3 = EV3Brick()

# ----------------
# - Define ports -
# ----------------
# Motors
move_motor_l = Motor(Port.B)
move_motor_r = Motor(Port.C)
move_sorter_motor = Motor(Port.B)
drop_motor = Motor(Port.D)
# Sensors
stack_color_sensor = ColorSensor(Port.S1)
line_color_sensor = ColorSensor(Port.S2)
#return_button = TouchSensor(Port.S3)
collision_sensor = UltrasonicSensor(Port.S4)

stored_bricks = []

# --------------------
# - Define Constants -
# --------------------

# Speeds (in degrees/second)
# Medium motors can go up to 1560 degrees/second
# Large motors can go up to 1050 degrees/second
DROP_SPEED = 500
MOVE_SPEED = 400
CONTROLLER_MOVE_SPEED = 200
SORT_SPEED = 1000
LAGGING_LINE_FOLLOW_SPEED = 100
TURN_SPEED = 300
LINE_FOLLOW_SPEED = 300

BLACK = 9
WHITE = 85
LINE_THRESHOLD = (BLACK + WHITE) / 2

# Define colors
LINE_COLOUR = Color.BLACK
GROUND_COLOUR = Color.WHITE

# Beep to indicate the the project started
ev3.speaker.beep()

# Connect to xbox controller
#controller = XboxController()


def DropItem():
    drop_motor.run_angle(1500, 180)
    drop_motor.run_angle(1500, -180)


def IsBlockColor(col : Color) -> bool:
    if (col == Color.RED):
        return True
    if (col == Color.GREEN):
        return True
    if (col == Color.YELLOW):
        return True
    if (col == Color.BLUE):
        return True
    return False 


def ColorToName(col : Color) -> str:
    if col == Color.RED:
        return "Red"
    if col == Color.GREEN:
        return "Green"
    if col == Color.BLUE:
        return "Blue"
    if col == Color.YELLOW:
        return "Yellow"
    if col == Color.BROWN:
        return "Brown"
    if col == Color.BLACK:
        return "Black"
    if col == Color.WHITE:
        return "White"
    return "An error"


def Turn(angle : int):
    move_motor_l.run_angle(TURN_SPEED, angle*2)
    move_motor_r.run_angle(-TURN_SPEED, angle*2)


def LineFollow():
    while IsBlockColor(stack_color_sensor.color()):
        searching_color = stack_color_sensor.color()
        ev3.speaker.say("Delivery for the " + ColorToName(searching_color) + " house.")
        ev3.speaker.say(ColorToName(searching_color))
        going_left = True
        last_going = False
        loop_wait = 20
        while True:
            reflection = line_color_sensor.reflection()
            if (reflection > LINE_THRESHOLD): # if the ground is bright go right
                move_motor_l.run_time(LINE_FOLLOW_SPEED,loop_wait) # Left forward
                move_motor_r.run_time(LAGGING_LINE_FOLLOW_SPEED,loop_wait)
            else:
                move_motor_l.run_time(LAGGING_LINE_FOLLOW_SPEED, loop_wait) # Right forward
                move_motor_r.run_time(LINE_FOLLOW_SPEED, loop_wait)

            floor_colour = line_color_sensor.color()
            if floor_colour == searching_color:
                ev3.speaker.say("Your delivery is here")
                while floor_colour == searching_color:
                    DropItem()
                    wait(100)
                    searching_color = stack_color_sensor.color() # Drop off multiple parcels if they are there
                break
            wait(loop_wait)

        # Wait 200ms between deliveries to allow time for error
        wait(200)
    ev3.speaker.say("My deliveries are done.")
        
def ManualControlEv3():
    pass # Could not get the controller to work
#    drop_held = False
#    while (Button.B not in controller.buttons.pressed):
#        pressed_buttons = controller.buttons.pressed
#        trigger_percentages = controller.triggers()
#        trigger_percentages[1]
#
#        # If right trigger pressed
#        if trigger_percentages[1] > 10:
#            accel = trigger_percentages[1]
#            dir = controller.joystick_left()[0]
#            move_motor_l.run(CONTROLLER_MOVE_SPEED * accel * (dir))
#            move_motor_r.run(CONTROLLER_MOVE_SPEED * accel * (-dir))
#        else:
#            move_motor_l.hold()
#            move_motor_r.hold()
#            
#        if Button.A in pressed_buttons and not drop_held:
#            DropItem()
#        
        #wait(15) # Wait 15ms between polling input



ev3.speaker.set_volume(100)
ev3.speaker.set_speech_options('en','f1',90,50)

def ScanInStoredBricks():
    while not (Button.CENTER in ev3.buttons.pressed()):
        if (IsBlockColor(stack_color_sensor.color())):
            stored_bricks.append(stack_color_sensor.color())
            ev3.speaker.beep()
            wait(1000)
            while (stack_color_sensor.color() != Color.BLACK):
                wait(100)


def ScanReflection():
    while True:
        reflection = line_color_sensor.reflection()
        print(reflection)
        if Button.UP in ev3.buttons.pressed():
            break


while True:
    if Button.LEFT in ev3.buttons.pressed():
        LineFollow()
    if Button.RIGHT in ev3.buttons.pressed():
        ManualControlEv3()
    if Button.DOWN in ev3.buttons.pressed():
        DropItem()
    if Button.UP in ev3.buttons.pressed():
        ScanReflection()
    wait(80)