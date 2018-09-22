import cv2
import time
import imutils

#import nerf_turret

#nerf_turret.pan(120)
#nerf_turret.patrol()

camera = cv2.VideoCapture(0)

for i in range(20):
    time.sleep(0.5)
    (grabbed, frame) = camera.read()
    frame = imutils.resize(frame, width=600)
    cv2.imwrite('images/cap%d.png' % i, frame)

#nerf_turret.pan(0)
#nerf_turret.tilt(0)
