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
LAGGING_LINE_FOLLOW_SPEED = 80
LINE_FOLLOW_SPEED = 100

#BLACK = 29
#WHITE = 69
#LINE_THRESHOLD = (BLACK + WHITE) / 2
LINE_THRESHOLD = 35

# Define colors
LINE_COLOUR = Color.BLACK
GROUND_COLOUR = Color.WHITE

# Beep to indicate the the project started
#ev3.speaker.play_file

# Define song playing
# Define musical notes (frequencies in Hz)
E4, D4, C4, G4 = 330, 294, 262, 392

# Melody: (Note, Duration in ms)
melody = [
    (E4, 200), (D4, 200), (C4, 200), (D4, 200), 
    (E4, 200), (E4, 200), (E4, 400),           
    (D4, 200), (D4, 200), (E4, 200), (D4, 200), 
    (C4, 400)                                  
]

def PlaySong():
    Turn(-20)
    Turn(20)
    ev3.speaker.set_volume(50)
    for note, duration in melody:
        ev3.speaker.beep(frequency=note, duration=duration)
        wait(50) # Small pause between notes for clarity
    ev3.speaker.set_volume(100)
    Turn(-20)
    Turn(20)

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
        return "the koala cottage"
    if (col == Color.GREEN):
        return "the birds nest"
    if (col == Color.YELLOW):
        return "panda place"
    if (col == Color.BLUE):
        return "the shah mansion"
    return False 


def ColorToName(col : Color) -> str: # Used for debugging
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
    move_motor_l.run_angle(TURN_SPEED, angle*2,Stop.HOLD, False)
    move_motor_r.run_angle(-TURN_SPEED, angle*2)

def PopFirstColor():
    return stored_bricks.pop(0)

def LineFollow(dance = False):
    while len(stored_bricks) > 0:
        searching_color = stored_bricks[0]
        ev3.speaker.say("I am going to " + HouseColorToName(searching_color))
        loop_wait = 20
        while True:
            rgb = line_color_sensor.rgb()
            reflection = max(rgb)

            if reflection < LINE_THRESHOLD: # On line
                move_motor_l.run(-LAGGING_LINE_FOLLOW_SPEED)  # Turn more sharply
                move_motor_r.run(LINE_FOLLOW_SPEED)
            else: # Off the line
                move_motor_l.run(LINE_FOLLOW_SPEED) 
                move_motor_r.run(LAGGING_LINE_FOLLOW_SPEED)

            floor_colour = line_color_sensor.color()

            if collision_sensor.distance() < 100:
                while collision_sensor.distance() < 115:
                    wait(500)
                    ev3.speaker.beep(800,500)

            if floor_colour == searching_color:
                move_motor_l.stop()
                move_motor_r.stop()
                ev3.speaker.say("Delivery for " + HouseColorToName(searching_color))
                Turn(-60)
                while floor_colour == searching_color:
                    DropItem()
                    wait(200)
                    stored_bricks.pop(0)
                    if len(stored_bricks) == 0:
                        searching_color = None
                    else:
                        searching_color = stored_bricks[0] # Drop off multiple parcels if they are there
                if dance:
                    PlaySong()
                Turn(50)
                break
            wait(loop_wait)

        # Wait 200ms between deliveries to allow time for error in dropping items
        wait(200)
    ev3.speaker.say("My deliveries are done.")
    ReturnToPostOffice()
        
def ReturnToPostOffice():
    moving = True
    since_found_red = 0
    red_found = False
    while moving:
        rgb = line_color_sensor.rgb()
        reflection = max(rgb)
        if reflection < LINE_THRESHOLD: # On line
            move_motor_l.run(-LAGGING_LINE_FOLLOW_SPEED)  # Turn more sharply
            move_motor_r.run(LINE_FOLLOW_SPEED)
        else: # Off the line
            move_motor_l.run(LINE_FOLLOW_SPEED) 
            move_motor_r.run(LAGGING_LINE_FOLLOW_SPEED)
        if red_found:
            since_found_red += 20
        elif line_color_sensor.color() == Color.RED:
            red_found = True
        if since_found_red > 8000: # Continue moving for 8 seconds
            moving = False
        wait(20)
    move_motor_l.hold()
    move_motor_r.hold()
    
    


def ScanReflection(): # For calibrating line following
    while True:
        rgb = line_color_sensor.rgb()
        reflection = max(rgb)
        print(reflection)
        if Button.UP in ev3.buttons.pressed():
            break


def ScanItems():
    while not Button.DOWN in ev3.buttons.pressed():
        found_colour = stack_color_sensor.color()
        if IsABlockColor(found_colour):
            stored_bricks.append(found_colour)
            ev3.speaker.beep()
            wait(1000)
            ev3.speaker.beep(1000,50)
        wait(100)
    ev3.speaker.beep(100,50)
            
ev3.speaker.beep()
ev3.speaker.set_volume(100)
ev3.speaker.set_speech_options('en','f3',120,70)

while True:
    pressedButtons = ev3.buttons.pressed()
    if Button.LEFT in pressedButtons:
        LineFollow()
        continue
    if Button.RIGHT in pressedButtons:
        LineFollow(True)
        continue
    if Button.UP in pressedButtons:
        ScanItems()
        continue
    wait(100)