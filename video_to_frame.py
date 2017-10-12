# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 15:43:23 2017

@author: lenovo-4
"""
#
#import cv2
#print(cv2.__version__)
#vidcap = cv2.VideoCapture('video.avi')
#success,image = vidcap.read()
#count = 0
#success = True
#while success:
#  success,image = vidcap.read()
#  print 'Read a new frame: ', success
#  cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file
#  count += 1
  
import cv2
print(cv2.__version__)  # my version is 3.1.0
vidcap = cv2.VideoCapture('video2.avi')
count = 0
while True:
    success,image = vidcap.read()
    if not success:
        break
    cv2.imwrite("output/frame%d.jpg" % count, image)     # save frame as JPEG file
    count += 1
