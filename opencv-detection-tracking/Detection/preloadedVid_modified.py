import numpy as np
import cv2

### This works better for my precompiled vid, seems to be bad for streaming ###

body_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture("Video_1.MOV")  # make input video name to load file, 0 is face cam if you have one

ret, frame = cap.read()
tol = 0
latFrame = 0

while(ret):
	#frame = cv2.transpose(frame) #transposed because of my shitty iphone video

	if latFrame % 4 == 0: #takes every fourth frame
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		body = body_cascade.detectMultiScale(gray,1.1,5)

	if body != ():
		#if fourth frame and face detect set tolerance += 1
		if latFrame % 4 == 0:
			tol += 1

		#tol > 2 and latency not too far from original face detect
		if tol > 2 and latFrame % 2 < 2:
			x,y,w,h = body[0]
			cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0),2)
	else:
		tol = 0;

	latFrame += 1
	cv2.imshow('stream', frame)

	# q button quits
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

	ret, frame = cap.read()

cv2.destroyAllWindows()
