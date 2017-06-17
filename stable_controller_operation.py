import sys
sys.path.append('/home/pi/Xbox')

import xbox
import serial
from time import time

joy = xbox.Joystick()
ser = serial.Serial('/dev/ttyACM0')

# espeak -vlv+m3 -s300 "Semiautomatik"
# espeak -vlv+m3 -s300 "Automatik"

#define MAX_TILT_UP   2000
#define MAX_TILT_DOWN 1300
#define MAX_PAN_LEFT   800
#define MAX_PAN_RIGHT 2200
#define TILT_MIDPOINT 1500
#define PAN_MIDPOINT  1455

x = 0
y = 0

def pan(val):
    return 1455 + val * 745

def tilt(val):
    return 1650 + val * 350

def send_command(action_code, argument):
    argument=int(argument)
    print('sending %s %d'%(action_code,argument))
    ser.write(bytes([115, ord(action_code), (argument & 0b1111111100000000) >> 8, argument & 0b11111111, 101]))
    return

time1 = time()
time2 = time()
time3 = time()
while not joy.Back():
    if joy.rightTrigger() > .5 and time() > time1 + 1.5:
        send_command('f', 1)
        time1 = time()
    x_p, y_p = joy.leftStick()
    if time() > time2 + .1:
        x += x_p / 10
        x = max(x, -1); x = min(x, 1)
        send_command('p', pan(x))
        time2 = time()
    if time() > time3 + .1:
        y += y_p / 10
        y = max(y, -1); y = min(y, 1)
        send_command('t', pan(y))
        time3 = time()
joy.close()
