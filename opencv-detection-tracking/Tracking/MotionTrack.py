import imutils
import cv2
import numpy as np

cap = cv2.VideoCapture("Still.MOV")    # currently streaming, jitters a bit, works best mid range
body_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

ret, frame = cap.read()
frame = cv2.transpose(frame)   #transposed becuase iphone vid
frame = imutils.resize(frame, width=500)    # you might have to download imutils yourself via py pip
gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)   # blur away random high intesity vals

ret, frame = cap.read()
delt = gray1                                   # keeps track of frame difference
sizes = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]        # remember last three motion frames, so error doesnt explode
lastSize = [0,0,0,0]
sameSizeCounter = 0
foundSubject = True
i = 0
xmin = -1
while(ret):
	frame = cv2.transpose(frame)
	frame = imutils.resize(frame, width=500)   # change this how you see fit/runs best on your comp
	gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)


	if sameSizeCounter > 4:
		if sameSizeCounter % 4 == 0:
			body = body_cascade.detectMultiScale(gray2,1.1,5)
		else:
			body = ()

		if body != ():
			x,y,w,h = body[0]
			cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0),2)
		else:
			foundSubject = False

	delt = cv2.absdiff(gray1, gray2)           # taking differnce
	thresh = cv2.threshold(delt, 10, 255, cv2.THRESH_BINARY)[1]     # set very low intesity pixels to zero
	thresh = cv2.dilate(thresh, None, iterations=10)                # blows up difference we do have for better body encompass
	(_, cnts, _) = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)   # contour lines, the actual important stuff

	if cnts:  # start body figure based on contour lines
		(xmin,ymin,_,_) = cv2.boundingRect(cnts[0]) # commented out is an alternative way but seems to be less stable
		#xmin = cnts[0][0,0,0]
		#ymin = cnts[0][0,0,1]
		xmax = xmin
		ymax = ymin
		for c in cnts:
			(x,y,w,h) = cv2.boundingRect(c)
			xmin = x if x < xmin else xmin
			xmax = x+w if x+w > xmax else xmax
			ymin = y if y < ymin else ymin
			ymax = y+h if y+h > ymax else ymax
			#xmin = min(min(c[:,0,0]),xmin)
			#ymin = min(min(c[:,0,1]),ymin)
			#xmax = max(max(c[:,0,0]),xmax)
			#ymax = max(max(c[:,0,1]),ymax)
		area = (xmax-xmin)*(ymax-ymin)
		arr = sizes[i-1]
		areaPrev = (arr[2]-arr[0])*(arr[3]-arr[1])

		if area < areaPrev*0.4:  # make sure rectangle does not get too big
			xmin = arr[0]
			ymin = arr[1]
			xmax = arr[2]
			ymax = arr[3]
		else:                    # saves this frame for reference
			sizes[i][0] = xmin
			sizes[i][1] = ymin
			sizes[i][2] = xmax
			sizes[i][3] = ymax

		i = (i+1)%3

	if lastSize != [xmin, ymin, xmax, ymax]:
		lastSize = [xmin, ymin, xmax, ymax]
		sameSizeCounter = 0
		foundSubject = True
	else:
		sameSizeCounter += 1

	if xmin != - 1 and (foundSubject or body != ()):
		cv2.rectangle(frame, (xmin,ymin), (xmax,ymax),(0,255,0),2)
	cv2.imshow("Src", frame)
	#cv2.imshow("Thresh", thresh)
	#cv2.imshow("Frame Delta", delt)

	key = cv2.waitKey(20) & 0xFF
	# q to quit
	if key == ord('q'):
		break
	foundSubject = True
	gray1 = gray2.copy() # frame switch for new delta later
	ret, frame = cap.read()

cv2.destroyAllWindows()
