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
DROP_SPEED = 1500
TURN_SPEED = 200
LAGGING_LINE_FOLLOW_SPEED = 60
LINE_FOLLOW_SPEED = 100

#BLACK = 29
#WHITE = 69
#LINE_THRESHOLD = (BLACK + WHITE) / 2
LINE_THRESHOLD = 35

# Define colors
LINE_COLOUR = Color.BLACK
GROUND_COLOUR = Color.WHITE

# Beep to indicate the the project started
ev3.speaker.beep()
#ev3.speaker.play_file


def DropItem():
    drop_motor.run_angle(DROP_SPEED, 180)
    drop_motor.run_angle(DROP_SPEED, -180)


def IsABlockColor(col : Color) -> bool:
    if (col == Color.RED):
        return True
    if (col == Color.GREEN):
        return True
    if (col == Color.YELLOW):
        return True
    if (col == Color.BLUE):
        return True
    return False 

def HouseColorToName(col : Color) -> str:
    if (col == Color.RED):
        return "Koala"
    if (col == Color.GREEN):
        return "Bird"
    if (col == Color.YELLOW):
        return "Rabbit"
    if (col == Color.BLUE):
        return "Mr Mouse"
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
    while IsABlockColor(stack_color_sensor.color()):
        searching_color = stack_color_sensor.color()
        ev3.speaker.say("Delivery for the " + ColorToName(searching_color) + " house.")
        loop_wait = 20
        found_color = False
        while True:
            rgb = line_color_sensor.rgb()
            reflection = max(rgb)

            if reflection < LINE_THRESHOLD: # On line
                move_motor_l.run(-LAGGING_LINE_FOLLOW_SPEED)  # Turn more sharply
                move_motor_r.run(LINE_FOLLOW_SPEED)
            else: # Off the line
                # This make it still turn with the line
                move_motor_l.run(LAGGING_LINE_FOLLOW_SPEED) 
                move_motor_r.run(LINE_FOLLOW_SPEED)
                # This make it turn towards the line slightly
                #move_motor_l.run(LINE_FOLLOW_SPEED) 
                #move_motor_r.run(LAGGING_LINE_FOLLOW_SPEED)

            floor_colour = line_color_sensor.color()

            if floor_colour == searching_color:
                found_color = True
            elif found_color and floor_colour == Color.WHITE:
                move_motor_l.stop()
                move_motor_r.stop()
                ev3.speaker.say("Your delivery is here " + HouseColorToName(searching_color))
                while floor_colour == searching_color:
                    DropItem()
                    wait(100)
                    searching_color = stack_color_sensor.color() # Drop off multiple parcels if they are there
                break
            wait(loop_wait)

        # Wait 200ms between deliveries to allow time for error in dropping items
        wait(200)
    ev3.speaker.say("My deliveries are done.")
        
ev3.speaker.set_volume(100)
ev3.speaker.set_speech_options('en','f1',90,50)

def ScanReflection():
    while True:
        rgb = line_color_sensor.rgb()
        reflection = max(rgb)
        print(reflection)
        if Button.UP in ev3.buttons.pressed():
            break

def SayLine():
    ev3.speaker.say("I am ready to deliver some packages.")

while True:
    pressedButtons = ev3.buttons.pressed()
    if Button.LEFT in pressedButtons:
        LineFollow()
        continue
    if Button.RIGHT in pressedButtons:
        SayLine()
        continue
    if Button.DOWN in pressedButtons:
        DropItem()
        continue
    if Button.UP in pressedButtons:
        ScanReflection()
        continue
    wait(100)