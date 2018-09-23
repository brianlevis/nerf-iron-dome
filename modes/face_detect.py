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
time_since_face = time.time()
revving = False
# loop over the frames from the video stream
while True:
    if time.time() - time_since_face > 3 and revving:
        print("Haven't seen a face in a while...")
        nerf_turret.rev(0)
        revving = False
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
    time_since_face = time.time()
    print("Found {} faces".format(len(faces)))
    (fx, fy, fw, fh) = faces[0]
    x, y = int(round(fx + fw / 2)), int(round(fy + fh / 2))
    print("Face at", (x, y))
    # Center: (216, 157)
    dx, dy = x-216, 100-y # 5 for gravity
    set_change(int(math.ceil(dx*8/10)), int(dy*8/10))
    # dx, dy = 150-x, y-115
    # vx, vy = dx // 100, dy // 100
    distance = math.sqrt(dx**2 + dy**2)
    revving = distance <= 80
    if distance > 80:
        nerf_turret.rev(0)
    elif distance > 70:
        nerf_turret.rev(40)
    elif distance > 60:
        nerf_turret.rev(80)
    elif distance > 50:
        nerf_turret.rev(120)
    else:
        nerf_turret.rev(160)
    if distance < 35:
        time.sleep(0.1)
        nerf_turret.fire(5)
        time.sleep(0.2)
        nerf_turret.rev(120)
    time.sleep(0.1)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# camera.release()
vs.stop()
