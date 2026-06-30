#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import XboxController



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
return_button = TouchSensor(Port.S3)
collision_sensor = UltrasonicSensor(Port.S4)

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
LAGGING_LINE_FOLLOW_SPEED = 200
TURN_SPEED = 300
LINE_FOLLOW_SPEED = 300

# Define colors
LINE_COLOUR = Color.BLUE
GROUND_COLOUR = Color.WHITE

# Beep to indicate the the project started
ev3.speaker.beep()

# Connect to xbox controller
controller = XboxController()


def DropItem():
    drop_motor.run_until_stalled(500,Stop.COAST, 30)
    wait(100)
    drop_motor.run_angle(500,-180)


def SortItems():
    while stack_color_sensor != Color.BLACK:
        searching_color = stack_color_sensor.color

        ev3.speaker.say("Finding " + ColorToName(searching_color) + " box")
        move_sorter_motor.run(SORT_SPEED)

        while True:
            if line_color_sensor.color == searching_color:
                break
        move_sorter_motor.hold()
        DropItem()

        # Return to start
        move_sorter_motor.run(-SORT_SPEED)
        while not return_button.pressed:
            wait(10)
        move_sorter_motor.stop()

        # Wait between loops to allow items to fall
        wait(500)


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
    move_motor_l.run_angle(TURN_SPEED, angle)
    move_motor_r.run_angle(-TURN_SPEED, angle)


def LineFollow():
    while IsBlockColor(stack_color_sensor.color):
        searching_color = stack_color_sensor.color

        ev3.speaker.say(ColorToName(searching_color))
        ev3.speaker.say("Delivery for the " + ColorToName(searching_color) + " house.")
        ev3.speaker.say(ColorToName(searching_color))
        going_left = True
        while True:
            if going_left:
                move_motor_l.run(LAGGING_LINE_FOLLOW_SPEED)
                move_motor_r.run(LINE_FOLLOW_SPEED)
            else:
                move_motor_l.run(LINE_FOLLOW_SPEED)
                move_motor_r.run(LAGGING_LINE_FOLLOW_SPEED)

            if line_color_sensor.color == LINE_COLOUR:
                going_left = False
            elif line_color_sensor.color == GROUND_COLOUR:
                going_left = True
                
                
            # Detect letterboxes
            if collision_sensor.distance() < 100:
                move_motor_l.stop()
                move_motor_r.stop()
                ev3.speaker.say("Found a house")
                Turn(-90)
                move_motor_l.run_angle(MOVE_SPEED,0.5)
                move_motor_r.run_angle(MOVE_SPEED,0.5)
                found_color = line_color_sensor.color
                ev3.speaker.say("This house is " + found_color)
                if searching_color == found_color:
                    ev3.speaker.say("I was looking for this one")
                    Turn(90)
                    DropItem()
                    Turn(-90)
                    break

                # Reverse out of house
                move_motor_l.run_angle(MOVE_SPEED,-0.8) 
                move_motor_r.run_angle(MOVE_SPEED,-0.8)
                    

            # Check if there is anything in the 10cm in front of the vehicle and stop
            #if collision_sensor.distance() < 100:
                #ev3.speaker.say("Something is in the way!")
                #while collision_sensor.distance() < 110:
                    #wait(100)
                

            if line_color_sensor.color == searching_color:
                Turn(-90)
                DropItem()
                ev3.speaker.say("Your delivery is here")
                Turn(120)
                break
            #if line_color_sensor.color == searching_color:
                #Turn(-90)
                #DropItem()
                #ev3.speaker.say("Your delivery is here")
                #Turn(120)
                #break

        # Wait 200ms between deliveries to allow time for error
        wait(200)
    ev3.speaker.say("My deliveries are done.")
        
def ManualControlEv3():
    drop_held = False
    while (Button.B not in controller.buttons.pressed):
        pressed_buttons = controller.buttons.pressed
        trigger_percentages = controller.triggers()
        trigger_percentages[1]

        # If right trigger pressed
        if trigger_percentages[1] > 10:
            accel = trigger_percentages[1]
            dir = controller.joystick_left()[0]
            move_motor_l.run(CONTROLLER_MOVE_SPEED * accel * (dir))
            move_motor_r.run(CONTROLLER_MOVE_SPEED * accel * (-dir))
        else:
            move_motor_l.hold()
            move_motor_r.hold()
            
        if Button.A in pressed_buttons and not drop_held:
            DropItem()
        
        wait(15) # Wait 15ms between polling input



ev3.speaker.set_volume(100)
ev3.speaker.set_speech_options('en','f1',70,50)

while True:
    print(ev3.buttons.pressed())
    if Button.LEFT in ev3.buttons.pressed():
        LineFollow()
    if Button.RIGHT in ev3.buttons.pressed():
        ManualControlEv3()
    wait(80)