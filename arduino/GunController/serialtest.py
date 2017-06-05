import serial
ser = serial.Serial('/dev/ttyACM0')
b=bytes([115,102,0,1,101])
ser.write(b)
