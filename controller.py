import sys
sys.path.append('/home/pi/Xbox')

import xbox
import serial
import subprocess
from time import time
import nerf_turret

joy = xbox.Joystick()
ser = serial.Serial('/dev/ttyACM0', 9600)

semiauto_cmd = ["espeak", "-vlv+m3", "-s300", "'Semiautomatik'"]
auto_cmd = ["espeak", "-vlv+m3", "-s300", "'Automatik'"]

# USAGE: Must be run with "sudo python3 stable_controller_operation.py"

# espeak -vlv+m3 -s300 "Semiautomatik"
# espeak -vlv+m3 -s300 "Automatik"

#define MAX_TILT_UP   2000
#define MAX_TILT_DOWN 1300
#define MAX_PAN_LEFT   800
#define MAX_PAN_RIGHT 2200
#define TILT_MIDPOINT 1500
#define PAN_MIDPOINT  1455

startCode = 's'
waitCode  = 'w'
revCode   = 'r'
fireCode  = 'f'
tiltCode  = 't'
panCode   = 'p'
endCode   = 'e'
errorCode = 'x'

times = [time()] * 4
elapsed = [0] * len(times)

while not joy.Back():
    c_t = time()
    elapsed = [c_t - t for t in times]
    if elapsed[0] > 0.2 and joy.rightTrigger() > .2:
        nerf_turret.fire(1)
        times[0] = time()
    if elapsed[1] > 0.2:
        nerf_turret.rev((int) (max(0, joy.leftTrigger() - 0.2) / 0.8 * 200))
        times[1] = time()
    if elapsed[2] > 0.1:
        x_p, y_p = joy.rightStick()
        nerf_turret.set_velocity((int) (x_p * 127), (int) (y_p * 127))
        times[2] = time()
joy.close()
