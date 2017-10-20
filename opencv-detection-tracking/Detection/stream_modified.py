import numpy as np
import cv2

### This works better for streaming ###

body_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0) # make input video name to load file, 0 is face cam if you have one

ret, frame = cap.read()
tol = 0

while(ret):
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	body = body_cascade.detectMultiScale(gray,1.1,5)

	if body != ():
		#tol makes sure no random detects pop up
		tol += 1
		if tol > 2:
			x,y,w,h = body[0]
			cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0),2)
	else:
		tol = 0;

	cv2.imshow('stream', frame)

	# q button quits
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

	ret, frame = cap.read()

cv2.destroyAllWindows()