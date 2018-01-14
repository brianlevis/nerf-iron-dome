import serial
from time import time

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

# x = 0
# y = 0
# auto = False
#
# def pan(val):
#     return 1455 + val * 745
#
# def tilt(val):
#     return 1650 + val * 350

last_command_time = time()
def send_command(action_code, argument):

    global last_command_time
    while time() - last_command_time < COMMAND_RATE:
        pass
    last_command_time = time()
    status = ser.read()
    if status == b'\x00':
        status = ser.read()
    elif status == b't':
        print(serial.readline())
        return
    if status == b'x':
        print('ERROR:', serial.readline())
        exit(1)
    elif status != b'w':
        print('Incorrect message prefix:', status)
        exit(1)
    argument = int(argument)
    print('sending %s %d'%(action_code, argument))
    ser.write(bytes([115, ord(action_code), (argument & 0xff00) >> 8, argument & 0xff, 101]))

def send_v(pan_velocity, tilt_velocity):
    pan_velocity, tilt_velocity = pan_velocity & 0xff, tilt_velocity & 0xff # truncate to byte size
    arg = (pan_velocity << 8) + tilt_velocity
    send_command('v', arg)

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

def velocity(pan, tilt):
    if -128 > pan or pan > 127:
        print("Pan velocity %s out of range [-127, 128]", str(pan))
    elif type(pan) != int:
        print("Pan velocity must be of type int, not %s", str(type(pan)))
    if -128 > tilt or tilt > 127:
        print("Tilt velocity %s out of range [-127, 128]", str(tilt))
    elif type(tilt) != int:
        print("Tilt velocity must be of type int, not %s", str(type(tilt)))
    else:
        send_command(velocityCode, ((0xff & pan) << 8) + (0xff & tilt))

# time0 = time()
# time1 = time()
# time2 = time()
# time3 = time()
# auto_firing = False
# auto_revving = False
# while not joy.Back():
#     if auto:
#         if joy.rightTrigger() > .5 and not auto_firing and auto_revving:
#             send_command('f', 65535)
#             auto_firing = True
#         elif joy.rightTrigger() < .5 and auto_firing:
#             send_command('f', 0)
#             auto_firing = False
#         if joy.leftTrigger() > .5 and not auto_revving:
#             send_command('r', 65535)
#             auto_revving = True
#         elif joy.leftTrigger() < .5 and auto_revving:
#             send_command('r', 0)
#             auto_revving = False
#         if joy.X() and time() > time0 + 1 and not auto_firing and not auto_revving:
#             subprocess.call(semiauto_cmd)
#             time0 = time()
#             auto = False
#     else:
#         if joy.rightTrigger() > .5 and time() > time1 + 1.5:
#             send_command('f', 1)
#             time1 = time()
#         if joy.X() and time() > time0 + 1:
#             subprocess.call(auto_cmd)
#             time0 = time()
#             auto = True
#     x_p, y_p = joy.leftStick()
#     if time() > time2 + .1:
#         x += x_p / 10
#         x = max(x, -1); x = min(x, 1)
#         send_command('p', pan(x))
#         time2 = time()
#     if time() > time3 + .1:
#         y += y_p / 10
#         y = max(y, -1); y = min(y, 1)
#         send_command('t', pan(y))
#         time3 = time()
# joy.close()
