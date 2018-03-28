# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py
# must run sudo modprobe bcm2835-v4l2

from collections import deque
import numpy as np
import argparse
import imutils
import cv2

import math
import time
import nerf_turret

# CV2 code taken from https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
# "Ball Tracking with OpenCV" by Adrian Rosebrock, 9/14/2015

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
pts = deque(maxlen=args["buffer"])

camera = cv2.VideoCapture(0)

time_per_frame = 1 / 20
lastUpdate = time.time()
last_ball_time = 0
while True:
    if time.time() - lastUpdate < time_per_frame:
        time.sleep(time_per_frame / 5)
        continue
    lastUpdate = time.time()
    (grabbed, frame) = camera.read()

    frame = imutils.resize(frame, width=600)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
    if len(cnts) > 0 and radius >= 10:
        last_ball_time = time.time()
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        dx, dy = 300-center[0], center[1]-230
        vx, vy = 50 * dx // 300, 50 * dy // 300
        print(dx, dy)
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 5:
            nerf_turret.set_velocity(0, 0)
        else:
            nerf_turret.set_velocity(vx, vy)
        print('>>>', distance)
        #continue
        if distance > 50:
            nerf_turret.rev(0)
        elif distance > 40:
            nerf_turret.rev(50)
        elif distance > 30:
            nerf_turret.rev(100)
        elif distance > 20:
            nerf_turret.rev(150)
        else:
            nerf_turret.rev(150)
            nerf_turret.fire(1)

        # # only proceed if the radius meets a minimum size
        # if radius > 10:
        #     # draw the circle and centroid on the frame,
        #     # then update the list of tracked points
        #     cv2.circle(frame, (int(x), int(y)), int(radius),
        #         (0, 255, 255), 2)
        #     cv2.circle(frame, center, 5, (0, 0, 255), -1)
    else:
        nerf_turret.rev(0)
        if time.time() - last_ball_time > 10:
            nerf_turret.patrol()
        else:
            nerf_turret.set_velocity(0, 0)
    # update the points queue
    pts.appendleft(center)

    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the frame to our screen
    # cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
# cv2.destroyAllWindows()
