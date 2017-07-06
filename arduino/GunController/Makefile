# Arduino compilation Makefile
# run with -Wwrite-strings to suppress warnings
# pi alias verify, upload, restart
#
# make – no upload
# make upload – compile and upload
# make clean – remove all our dependencies
# make depends – update dependencies
# make reset – reset the Arduino by tickling DTR on the serial port
# make raw_upload – upload without first resetting
# make show_boards – list all the boards defined in boards.txt

ARDUINO_DIR = /usr/share/arduino
BOARD_TAG    = uno
ARDUINO_PORT = /dev/ttyACM*
ARDUINO_LIBS =
include /usr/share/arduino/Arduino.mk
