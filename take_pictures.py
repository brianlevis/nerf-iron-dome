import cv2
import time

import nerf_turret

nerf_turret.patrol()

camera = cv2.VideoCapture(0)

for i in range(10):
    time.sleep(3)
    (grabbed, frame) = camera.read()
    frame = imutils.resize(frame, width=600)
    cv2.imwrite('images/cap%d.png' % i, frame)

nerf_turret.pan(0)
nerf_turret.tilt(0)