import nerf_turret
import math
import numpy as np
import argparse
import imutils
import time
import cv2

PROTOTXT = 'deploy.prototxt.txt'
MODEL = 'res10_300x300_ssd_iter_140000.caffemodel'
CONFIDENCE = 0.5

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] starting video stream...")
camera = cv2.VideoCapture(0)
time.sleep(1.0)

time_per_frame = 1 / 20
lastUpdate = time.time()
last_ball_time = 0
# loop over the frames from the video stream
while True:
    if time.time() - lastUpdate < time_per_frame:
        time.sleep(time_per_frame / 5)
        continue
    lastUpdate = time.time()
    (grabbed, frame) = camera.read()
    # frame = imutils.resize(frame, width=400)

    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))

    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()

    best_detection = None
    best_confidence = None

    # loop over the detections
    for i in range(0, detections.shape[2]):
        detection = detections[0, 0, i, :]
        confidence = detection[2]

        if confidence < CONFIDENCE:
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
        dx, dy = 150-x, y-115
        vx, vy = 50 * dx // 300, 50 * dy // 300
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 5:
            nerf_turret.set_velocity(0, 0)
        else:
            nerf_turret.set_velocity(vx, vy)
        # # draw the bounding box of the face along with the associated
        # # probability
        # text = "{:.2f}%".format(confidence * 100)
        # y = startY - 10 if startY - 10 > 10 else startY + 10
        # cv2.rectangle(frame, (startX, startY), (endX, endY),
        #               (0, 0, 255), 2)
        # cv2.putText(frame, text, (startX, y),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    # show the output frame
    cv2.imshow("Frame", frame)
    print(text)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

camera.release()