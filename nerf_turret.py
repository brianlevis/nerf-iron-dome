import serial
import sys
from time import sleep, time

MIN_PYTHON = (3, 3)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)


ser = serial.Serial('/dev/ttyACM0', 9600)

COMMAND_RATE = 0.005

waitCode      = 'w'
errorCode     = 'x'
invalidCode   = 'i'
startCode     = 's'
endCode       = 'e'
revCode       = 'r'
fireCode      = 'f'
tiltCode      = 't'
panCode       = 'p'
velocityCode  = 'v'
heartbeatCode = 'h'
killCode      = 'k'

# Example usage:
# set_velocity(10, 10); sleep(1);
# set_velocity(-20,-20); sleep(1);
# fire(5); sleep(3);
# pan(0); tilt(0);

last_command_time = time()
def send_command(action_code, argument):

    global last_command_time
    while time() - last_command_time < COMMAND_RATE:
        pass
    last_command_time = time()
    status = ser.read()
    if status == b'\x00':
        exit()
    if status == b't':
        print(serial.readline())
        return
    elif status == b'x':
        print('ERROR:', serial.readline())
        exit(1)
    elif status != b'w':
        print('Incorrect message prefix:', status)
        exit(1)
    argument = int(argument)
    print('sending %s %d'%(action_code, argument))
    ser.write(bytes([115, ord(action_code), (argument & 0xff00) >> 8, argument & 0xff, 101]))

# [0, 127], [0, 127]
def set_velocity(pan_velocity, tilt_velocity):
    pan_velocity, tilt_velocity = pan_velocity & 0xff, tilt_velocity & 0xff # truncate to byte size
    arg = (pan_velocity << 8) + tilt_velocity
    send_command('v', arg)

def move(pan_location, tilt_location):
    send_command('p', pan_location)
    send_command('t', tilt_location)

# [0, 255]
def rev(rev_speed):
    send_command('r', rev_speed << 8)

def patrol():
    send_command('a', 1 << 8)

def fire(num_shots):
    send_command('f', num_shots << 8)

def printy():
    while True:
        print(ser.readline())

def pan(position):
    if -700 > position or position > 700:
        print("Position %s out of range [-700, 700]", str(position))
    elif type(position) != int:
        print("Position must be of type int, not %s", str(type(position)))
    else:
        send_command(panCode, position)

def tilt(position):
    if -300 > position or position > 500:
        print("Position %s out of range [-300, 500]", str(position))
    elif type(position) != int:
        print("Position must be of type int, not %s", str(type(position)))
    else:
        send_command(tiltCode, position)

# def velocity(pan, tilt):
#     if -128 > pan or pan > 127:
#         print("Pan velocity %s out of range [-127, 128]", str(pan))
#     elif type(pan) != int:
#         print("Pan velocity must be of type int, not %s", str(type(pan)))
#     if -128 > tilt or tilt > 127:
#         print("Tilt velocity %s out of range [-127, 128]", str(tilt))
#     elif type(tilt) != int:
#         print("Tilt velocity must be of type int, not %s", str(type(tilt)))
#     else:
#         send_command(velocityCode, ((0xff & pan) << 8) + (0xff & tilt))
