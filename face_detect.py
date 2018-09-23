# must run sudo modprobe bcm2835-v4l2

from imutils.video import VideoStream
import nerf_turret
import math
import numpy as np
import argparse
import imutils
import time
import cv2

CASCADE_PATH = 'haarcascade_frontalface_default.xml'

x_pos, y_pos = 0, 0
def set_change(x, y):
    global x_pos
    global y_pos
    new_x_pos = x_pos + x
    x_pos = max(-700, new_x_pos)
    x_pos = min(700, new_x_pos)
    new_y_pos = y_pos + y
    y_pos = max(-300, new_y_pos)
    y_pos = min(500, new_y_pos)
    nerf_turret.move(x_pos, y_pos)

faceCascade = cv2.CascadeClassifier(CASCADE_PATH)

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] starting video stream...")
# camera = cv2.VideoCapture(0)
vs = VideoStream(src=0).start()
time.sleep(2.0)

# loop over the frames from the video stream
while True:
    frame = vs.read()
    frame = cv2.resize(frame, (400, 300))
    frame = cv2.flip(frame, -1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    if len(faces) == 0:
        continue
    print("Found {} faces".format(len(faces)))
    (fx, fy, fw, fh) = faces[0]
    x, y = int(round(fx + fw / 2)), int(round(fy + fh / 2))
    print("Face at", (x, y))
    # Center: (216, 157)
    dx, dy = x-216, 130-y
    set_change(dx, dy)
    # dx, dy = 150-x, y-115
    # vx, vy = dx // 100, dy // 100
    distance = math.sqrt(dx**2 + dy**2)
    if distance > 50:
        nerf_turret.rev(0)
    elif distance > 40:
        nerf_turret.rev(50)
    elif distance > 30:
        nerf_turret.rev(100)
    elif distance > 20:
        nerf_turret.rev(150)
    elif distance > 10:
        nerf_turret.rev(255)
    else:
        nerf_turret.rev(255)
        nerf_turret.fire(1)
    time.sleep(0.1)
    # # draw the bounding box of the face along with the associated
    # # probability

    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# camera.release()
vs.stop()
