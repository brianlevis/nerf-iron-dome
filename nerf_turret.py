import serial
from time import time

ser = serial.Serial('/dev/ttyACM0', 9600)

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

command_queue = []
p.insert(0,obj)

def process_queue():
    if len(command_queue) == 0:
        return
    command = command_queue.pop()
    send_command(command)

# x = 0
# y = 0
# auto = False
#
# def pan(val):
#     return 1455 + val * 745
#
# def tilt(val):
#     return 1650 + val * 350

def send_command(command):
    action_code, argument = command
    status = serial.read()
    if status == 'x':
        print('ERROR:', serial.readline())
        exit(1)
    elif status != 'w':
        print('Incorrect message prefix:', status)
        exit(1)
    argument = int(argument)
    print('sending %s %d'%(action_code, argument))
    ser.write(bytes([115, ord(action_code), (argument & 0b1111111100000000) >> 8, argument & 0b11111111, 101]))

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
