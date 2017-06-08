#!/usr/bin/env python
import freenect
import cv
import frame_convert
import numpy as np

spread = 4
midx = 320
midy = 240
sense_pt1 = (midx - spread, midy - spread)
sense_pt2 = (midx + spread, midy + spread)
sense_rect = (sense_pt1[0], sense_pt1[1], sense_pt2[0] - sense_pt1[0], sense_pt2[1] - sense_pt1[1])

def show_depth():
    global threshold
    global current_depth

    depth, timestamp = freenect.sync_get_depth()
    viewable = frame_convert.full_depth_cv (depth)
    cv.Rectangle (viewable, sense_pt1, sense_pt2, (255, 0, 0), 1)
    cv.ShowImage ('Depth', viewable)
    roi = cv.GetSubRect (frame_convert.raw_depth_cv (depth), sense_rect)
    pix = cv.Avg (roi)[0]
    (roimin, roimax, a, b) = cv.MinMaxLoc (roi)
    if roimax < 1090:
      dist = 350.0 / (1091 - pix)
      print "%f %i %i" % (dist, roimin, roimax)
    else:
      print "XX"

def show_video():
    cv.ShowImage('Video', frame_convert.video_cv(freenect.sync_get_video()[0]))


cv.NamedWindow('Depth')
#cv.NamedWindow('Video')

print('Press ESC in window to stop')


while 1:
    show_depth()
    #show_video()
    if cv.WaitKey(200) == 27:
        break
