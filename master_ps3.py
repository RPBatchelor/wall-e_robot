# WALL-E RPi CONTROLLER
# Arduino code from Simon Bluett
# Author: Ryan Batchelor
# 13-Jan-2020

##########################################################
#---------- Import packages ----------

import pygame       # To read PS3 controller and control audo
import time         # For timers etc
import serial       # To communicate with the Arduino
import os
import random
import sys

##########################################################
#---------- Parameters ----------

# Axis mappings
LEFT_X = 0
LEFT_Y = 1
LEFT_TRIGGER = 2
RIGHT_X = 3
RIGHT_Y = 4
RIGHT_TRIGGER = 5
invert_Y = True         # By default, Y joystick are inverted so this needs to be corrected
invert_X = True         # Option to invert X

# Button mappings
CROSS = 0
CIRCLE = 1
TRIANGLE = 2
SQUARE = 3
L_1_BUTTON = 4
R_1_BUTTON = 5
L_2_BUTTON = 6
R_2_BUTTON = 7
SELECT = 8
START = 9
PS_BUTTON = 10
L_3_BUTTON = 11
R_3_BUTTON = 12
D_PAD_UP = 13
D_PAD_DOWN = 14
D_PAD_LEFT = 15
D_PAD_RIGHT = 16

# Timing and other settings
auto_servo_mode = False
loop_delay = .025
button_delay = 0.25
axis_threshold = 0.15

# Serial settings
port = '/dev/ttyACM0'
baud_rate = 115200

# Sound settings
volume = 10
wall_e_name_sound = "./sounds/walle-name-long.mp3"
wall_e_name_sound_time = 3.5
wall_e_startup_sound = "./sounds/startup-sound_2500.mp3"
wall_e_startup_sound_time = 2.5

###########################################################
#---------- Functions ----------

def connect_serial(port, baud_rate):
    try:
        ser = serial.Serial(port, baud_rate)
        ser.flushInput()
        print(ser)
        return ser
    except:
        print('Unable to connect serial')

def connect_controller():
    while pygame.joystick.get_count() == 0:
        print(f'Waiting for joystick connection. Joysticks found: {pygame.joystick.get_count()}')
        pygame.joystick.quit()
        time.sleep(1)
        pygame.joystick.init()
    j = pygame.joystick.Joystick(0)
    j.init()
    print(f'Initialised joystick : {j.get_name()}')
    num_axes = j.get_numaxes()
    num_buttons = j.get_numbuttons()
    # print(f'Joystick axes: {num_axes}')
    # print(f'Joystick buttons: {num_buttons}')
    time.sleep(1)
    return j, num_axes, num_buttons

def axis_value(axis):
    global axis_threshold
    pygame.event.get()
    value = j.get_axis(axis) 
    if abs(value) > axis_threshold:
        #print(f'Axis number: {axis} | Joystick value: {value}')
        value = value
    else:
        value = 0
    return value

def button_press(button):
    pygame.event.get()
    value = j.get_button(button)
    return value

def motors():
    if invert_X == True:
        LEFT_X_VALUE = -axis_value(LEFT_X)
    else:
        LEFT_X_VALUE = axis_value(LEFT_X)

    if invert_Y == True:
        LEFT_Y_VALUE = -axis_value(LEFT_Y)
    else:
        LEFT_Y_VALUE = axis_value(LEFT_Y)
    # print(f'Left X: {LEFT_X_VALUE} | Left Y: {LEFT_Y_VALUE}')
    # print(f'Right X: {RIGHT_X_VALUE} | Right Y: {RIGHT_Y_VALUE}')
    xVal = int(float(LEFT_X_VALUE)*100)
    yVal = int(float(LEFT_Y_VALUE)*100)
    ser.write(str.encode("X" + str(xVal) + '\n'))
    ser.write(str.encode("Y" + str(yVal) + '\n'))

def process_servo_mode(button):
    global auto_servo_mode
    button_value = button_press(button)
    if button_value == True:
        auto_servo_mode = not auto_servo_mode
        time.sleep(button_delay)
    
    if auto_servo_mode == True:
        ser.write(str.encode("M" + str(1) + '\n'))
    else:
        ser.write(str.encode("M" + str(0) + '\n'))
    

def head_direction():
    RIGHT_X_VALUE = axis_value(RIGHT_X)
    #print(f'The right X value is {RIGHT_X_VALUE}')
    #TODO: Process serial commands to send to arduino

def neck_top():
    if invert_Y == True:
        RIGHT_Y_VALUE = -axis_value(RIGHT_Y)
    else:
        RIGHT_Y_VALUE = axis_value(RIGHT_Y)
    #print(f'The right Y value is {RIGHT_Y_VALUE}')
    #TODO Need to process serial commands to send to arduino

def left_arm():
    L_2_BUTTON_VALUE = button_press(L_2_BUTTON)
    L_1_BUTTON_VALUE = button_press(L_1_BUTTON)
    if L_2_BUTTON_VALUE == True:
        ser.write(str.encode('b' + '\n'))
    if L_1_BUTTON_VALUE == True:
        ser.write(str.encode('m' + '\n'))

def right_arm():
    R_2_BUTTON_VALUE = button_press(R_2_BUTTON)
    R_1_BUTTON_VALUE = button_press(R_1_BUTTON)
    if R_2_BUTTON_VALUE == True:
        ser.write(str.encode('m' + '\n'))
    if R_1_BUTTON_VALUE == True:
        ser.write(str.encode('b' + '\n'))

def hard_reset(button):
    button_value = button_press(button)
    hold_duration = 1
    num_samples = 4
    if button1_value == True:
        # Check for hold duration
        start = time.time()
        while button_press(button) == True:
            time.sleep(hold_duration/num_samples)
            length = time.time() - start
            print(length)
            if length > hold_duration:
                # os.execl(sys.executable,*([sys.executable]+sys.argv))
                print("You DID IT")


def preset_animations(button1, button2, button3):
    button1_value = button_press(button1)
    button2_value = button_press(button2)
    button3_value = button_press(button3)

    if button1_value == True:
        ser.write(str.encode('A' + str(0) + '\n')) # 'A0' = SOFT_LEN Starting sequence
    if button2_value == True:
        ser.write(str.encode('A' + str(1) + '\n')) # 'A1' = BOOT_LEN Bootup eye sequence
    if button3_value == True:
        ser.write(str.encode('A' + str(2) + '\n')) # 'A2' = INQU_LEN Inquisitive sequence

def get_list_of_sound_clips():
    files = []
    for item in os.listdir('./sounds/'):
        if item.lower().endswith('.mp3'):
            # file_name = os.path.splitext(os.path.basename(item))[0]
            # file_time = float(file_name.split('_')[1])/1000.0
            # files.append((file_name, file_time))
            files.append(item)
            # print(files)
    return files


def play_sound_clip(clip):
    pygame.mixer.music.load(clip)
    pygame.mixer.music.set_volume(volume/10.0)
    pygame.mixer.music.play()
    # while pygame.mixer.music.get_busy() == True:
    #     continue

def play_sounds(button1, button2):
    # button1 plays the wall-e name file
    # button2 plays a random file from the list
    global audio_files
    button1_value = button_press(button1)
    button2_value = button_press(button2)

    if button1_value == True:
        play_sound_clip(wall_e_name_sound)
        # while pygame.mixer.music.get_busy() == True:
        #     continue
        time.sleep(button_delay)
    if button2_value == True:
        random_clip = audio_files[random.randrange(0,len(audio_files),1)]
        print(random_clip)
        play_sound_clip('./sounds/' + random_clip)
        # while pygame.mixer.music.get_busy() == True:
        #     continue
        time.sleep(button_delay)
    

def cleanup():
    pygame.quit()
    sys.exit()

############################################################
#---------- Initialise ----------

pygame.init()
pygame.mixer.init()
j, num_axes, num_buttons = connect_controller()
audio_files = get_list_of_sound_clips()

play_sound_clip(wall_e_startup_sound)
time.sleep(wall_e_startup_sound_time)

ser = connect_serial(port, baud_rate)


#############################################################
#---------- Main loop ----------
try:
    running = True
    while running:
        ser.flushInput()
        motors()
        process_servo_mode(SELECT)
        head_direction()
        neck_top()
        left_arm()
        right_arm()
        preset_animations(SQUARE, TRIANGLE, CIRCLE) # Takes 3 input. First = A0, Second = A1, Third = A2
        play_sounds(CROSS, R_3_BUTTON) # Takes 2 input. 1 for the walle name, 1 for random file
        # hard_reset(PS_BUTTON)
        time.sleep(loop_delay)

except KeyboardInterrupt:
    print('The program was stopped manually')
    cleanup()

# except:
#     print('Some other error has occured.')
#     cleanup()

finally:
    cleanup()

