# must run sudo modprobe bcm2835-v4l2

from imutils.video import VideoStream
import nerf_turret
import math
import numpy as np
import argparse
import imutils
import time
import cv2

PROTOTXT = 'deploy.prototxt.txt'
MODEL = 'res10_300x300_ssd_iter_140000.caffemodel'
CONFIDENCE = 0.4

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

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] starting video stream...")
# camera = cv2.VideoCapture(0)
vs = VideoStream(src=0).start()
time.sleep(2.0)

# loop over the frames from the video stream
while True:
    print("[INFO] starting loop...")
    lastUpdate = time.time()
    frame = vs.read()
    frame = cv2.resize(frame, (400, 300))
    frame = cv2.flip(frame, -1)

    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (w, h), (104.0, 177.0, 123.0))

    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    print("[INFO] running net...")
    detections = net.forward()
    print("[INFO] processing detections...")

    best_detection = None
    best_confidence = None

    # loop over the detections
    for i in range(0, detections.shape[2]):
        detection = detections[0, 0, i, :]
        confidence = detection[2]

        if confidence >= CONFIDENCE:
            print("Detected face with confidence", confidence)

        if confidence < CONFIDENCE or (best_confidence is not None and confidence < best_confidence):
            continue
        best_detection = detection
        best_confidence = confidence

        # compute the (x, y)-coordinates of the bounding box for the
        # object
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        x, y = int(round((box[0] + box[2]) / 2)), int(round((box[1] + box[3]) / 2))

        print("Best face at", (x, y))
        (startX, startY, endX, endY) = box.astype("int")
        # Center: (216, 157)
        dx, dy = x-216, y-157
        print("dx:", dx)
        set_change(dx, 0)
        time.sleep(0.3)
        # dx, dy = 150-x, y-115
        # vx, vy = dx // 100, dy // 100
        # distance = math.sqrt(dx**2 + dy**2)
        # if distance < 5:
        #     nerf_turret.set_velocity(0, 0)
        # else:
        #     nerf_turret.set_velocity(vx, vy)
        # # draw the bounding box of the face along with the associated
        # # probability
        text = "{:.2f}%".format(confidence * 100)
        y_ = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(frame, (startX, startY), (endX, endY),
                      (0, 0, 255), 2)
        cv2.putText(frame, text, (startX, y_),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        cv2.imwrite("img/frame{}_{}.png".format(x, y), frame)

    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# camera.release()
vs.stop()
