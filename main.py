#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.iodevices import XboxController


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.
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

# Write your program here.
ev3.speaker.beep()

# Connect to xbox controller
controller = XboxController()


def DropItem():
    drop_motor.run_angle(DROP_SPEED,360)

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


def ColorToName(col : Color) -> str:
    match col:
        case Color.RED:
            return "Red"
        case Color.GREEN:
            return "Green"
        case Color.BLUE:
            return "Blue"
        case Color.YELLOW:
            return "Yellow"


def Turn(angle : int):
    move_motor_l.run_angle(TURN_SPEED, angle)
    move_motor_r.run_angle(-TURN_SPEED, angle)

def LineFollow():
    while stack_color_sensor != Color.BLACK:
        searching_color = stack_color_sensor.color

        ev3.speaker.say("Delivery for the " + ColorToName(searching_color) + " house.")
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
                ev3.speaker.say("Found a letterbox")
                Turn(-90)
                found_color = line_color_sensor.color
                ev3.speaker.say("This house is " + found_color)
                if searching_color == found_color:
                    ev3.speaker.say("I was looking for this one")
                    Turn(90)
                    DropItem()
                    Turn(10)
                    break
                    

                while collision_sensor.distance() < 110:
                    wait(100)

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
        wait(500)
        
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
            
        if Button.A in controller.buttons.pressed and not drop_held:
            DropItem()
        
        wait(15) # Wait 15ms between polling input



ev3.speaker.set_volume
while True:
    print(ev3.buttons.pressed())
    wait(100)
    #if Button.LEFT in ev3.buttons.pressed().__contains__:
        #LineFollow()
    #if Button.RIGHT in ev3.buttons.pressed():
        #SortItems()