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
ev3.speaker.beep()
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
    ev3.speaker.set_volume(50)
    for note, duration in melody:
        ev3.speaker.beep(frequency=note, duration=duration)
        wait(50) # Small pause between notes for clarity
    ev3.speaker.set_volume(100)

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
    move_motor_l.run_angle(TURN_SPEED, angle*2,Stop.HOLD, False)
    move_motor_r.run_angle(-TURN_SPEED, angle*2)

def PopFirstColor():
    return stored_bricks.pop(0)

def LineFollow(dance = False):
    while IsABlockColor(stack_color_sensor.color()):
        searching_color = stack_color_sensor.color()
        ev3.speaker.say("Delivery for " + HouseColorToName(searching_color))
        loop_wait = 20
        found_color = False
        last_found = None
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
                #found_color = True
                #last_found = searching_color
            #elif found_color and floor_colour != Color.BLACK and floor_colour != searching_color:
                move_motor_l.stop()
                move_motor_r.stop()
                ev3.speaker.say("I am at " + HouseColorToName(searching_color))
                Turn(-60)
                while floor_colour == searching_color:
                    DropItem()
                    wait(200)
                    if dance:
                        Turn(-10)
                        Turn(10)
                        PlaySong()
                    searching_color = stack_color_sensor.color() # Drop off multiple parcels if they are there
                Turn(55)
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
            move_motor_l.run(LAGGING_LINE_FOLLOW_SPEED) 
            move_motor_r.run(LINE_FOLLOW_SPEED)
        if red_found:
            since_found_red += 20
        elif line_color_sensor.color() == Color.RED:
            red_found = True
        wait(20)
        if since_found_red > 2000: # 2000ms
            return
    

ev3.speaker.set_volume(100)
ev3.speaker.set_speech_options('en','f3',120,70)

def ScanReflection():
    while True:
        rgb = line_color_sensor.rgb()
        reflection = max(rgb)
        print(reflection)
        if Button.UP in ev3.buttons.pressed():
            break

def SayLine():
    ev3.speaker.say("I am ready to deliver some packages.")

def ScanItems():
    while not Button.DOWN in ev3.buttons.pressed():
        found_colour = stack_color_sensor.color()
        if IsABlockColor(found_colour):
            stored_bricks.append(found_colour)
            ev3.speaker.beep()
            wait(1000)
            ev3.speaker.beep(1000,50)
        wait(100)
            
    
while True:
    pressedButtons = ev3.buttons.pressed()
    if Button.LEFT in pressedButtons:
        LineFollow()
        continue
    if Button.RIGHT in pressedButtons:
        LineFollow(True)
        continue
    if Button.DOWN in pressedButtons:
        DropItem()
        continue
    if Button.UP in pressedButtons:
        ScanItems()
        continue
    wait(100)