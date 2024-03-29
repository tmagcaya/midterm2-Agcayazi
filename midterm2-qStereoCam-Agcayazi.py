#!/usr/bin/env python
# /* -*-  indent-tabs-mode:t; tab-width: 8; c-basic-offset: 8  -*- */
# /*
# Copyright (c) 2014, Daniel M. Lofaro <dan (at) danLofaro (dot) com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# */
import diff_drive
import ach
import sys
import time
from ctypes import *
import socket
import cv2.cv as cv
import cv2
import numpy as np
import math

dd = diff_drive
ref = dd.H_REF()
tim = dd.H_TIME()

ROBOT_DIFF_DRIVE_CHAN   = 'robot-diff-drive'
ROBOT_CHAN_VIEW_R   = 'robot-vid-chan-r'
ROBOT_CHAN_VIEW_L   = 'robot-vid-chan-l'
ROBOT_TIME_CHAN  = 'robot-time'
# CV setup 
cv.NamedWindow("wctrl_L", cv.CV_WINDOW_AUTOSIZE)
cv.NamedWindow("wctrl_R", cv.CV_WINDOW_AUTOSIZE)
#capture = cv.CaptureFromCAM(0)
#capture = cv2.VideoCapture(0)

# added
##sock.connect((MCAST_GRP, MCAST_PORT))
newx = 320
newy = 240

nx = 320
ny = 240

r = ach.Channel(ROBOT_DIFF_DRIVE_CHAN)
r.flush()
vl = ach.Channel(ROBOT_CHAN_VIEW_L)
vl.flush()
vr = ach.Channel(ROBOT_CHAN_VIEW_R)
vr.flush()
t = ach.Channel(ROBOT_TIME_CHAN)
t.flush()

i=0


print '======================================'
print '============= Robot-View ============='
print '========== Daniel M. Lofaro =========='
print '========= dan@danLofaro.com =========='
print '======================================'
while True:
    # Get Frame
    imgL = np.zeros((newx,newy,3), np.uint8)
    imgR = np.zeros((newx,newy,3), np.uint8)
    c_image = imgL.copy()
    c_image = imgR.copy()
    vidL = cv2.resize(c_image,(newx,newy))
    vidR = cv2.resize(c_image,(newx,newy))
    [status, framesize] = vl.get(vidL, wait=False, last=True)
    if status == ach.ACH_OK or status == ach.ACH_MISSED_FRAME or status == ach.ACH_STALE_FRAMES:
        vid2 = cv2.resize(vidL,(nx,ny))
        imgL = cv2.cvtColor(vid2,cv2.COLOR_BGR2RGB)
        cv2.imshow("wctrl_L", imgL)
        cv2.waitKey(10)
    else:
        raise ach.AchException( v.result_string(status) )
    [status, framesize] = vr.get(vidR, wait=False, last=True)
    if status == ach.ACH_OK or status == ach.ACH_MISSED_FRAME or status == ach.ACH_STALE_FRAMES:
        vid2 = cv2.resize(vidR,(nx,ny))
        imgR = cv2.cvtColor(vid2,cv2.COLOR_BGR2RGB)
        cv2.imshow("wctrl_R", imgR)
        cv2.waitKey(10)
    else:
        raise ach.AchException( v.result_string(status) )


    [status, framesize] = t.get(tim, wait=False, last=True)
    if status == ach.ACH_OK or status == ach.ACH_MISSED_FRAME or status == ach.ACH_STALE_FRAMES:
        pass
        #print 'Sim Time = ', tim.sim[0]
    else:
        raise ach.AchException( v.result_string(status) )

#-----------------------------------------------------
#-----------------------------------------------------
#-----------------------------------------------------
    # Def:
    # ref.ref[0] = Right Wheel Velos
    # ref.ref[1] = Left Wheel Velos
    # tim.sim[0] = Sim Time
    # imgL       = cv image in BGR format (Left Camera)
    # imgR       = cv image in BGR format (Right Camera)
    greenR = cv2.inRange(imgR, np.array([0,0,0], dtype = np.uint8), np.array([0,255,0], dtype = np.uint8));
    greenL = cv2.inRange(imgL, np.array([0,0,0], dtype = np.uint8), np.array([0,255,0], dtype = np.uint8));
    
    cntRGBR, h = cv2.findContours(greenR, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cntRGBL, h = cv2.findContours(greenL, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    check=0
    xR = 0
    xL = 0
    centerx = 320/2
    centery = 240/2
    for cntR in cntRGBR:
	(x, y), radius = cv2.minEnclosingCircle(cntR)
	xR = x
	center = (int(x), int(y))
	centery = int(y) 
	radius = int(radius)
	check=1
	print 'Right obj x, y, radius:', x, y, radius
	circle = cv2.circle(imgR, center, radius, (0, 255, 0), 2)
    if(check == 1):
	    for cntL in cntRGBL:
		(x, y), radius = cv2.minEnclosingCircle(cntL)
		xL = x
		center = (int(x), int(y))
		centery = int(y) 
		radius = int(radius)
		check=2
		print 'Left obj x, y, radius: ', x, y, radius
		circle = cv2.circle(imgR, center, radius, (0, 255, 0), 2)
    #center = cv2.circle(imgR, (centerx, centery), 10, (0, 0, 255), 2)
    


    if(check==2):
	offset = abs(xL - xR) 
	offsetmm = offset*280/1000
	theta1 = math.atan(offsetmm/85) #85 is the focal length in mm
	theta2 = math.pi/2-theta1
	dist = math.tan(theta2)*0.4 # so we get the dist in meters
	print 'offset, ', offset
	print 'offsetmm, ', offsetmm
	print 'theta1, ', theta1
	print 'theta2, ', theta2
	print 'distance, ', dist
    	err = (nx/2) - x;
    	#print 'error in pixels = ',err
	#print 'error in percent = ', err/640
	# k = 2 (max speed before we get vision problems)/320(max error)
    if(check == 3): # which is never in this program.    	
	kp = 0.00625
	P = kp*err
	#Derivative
	kd = 0  #I tried making a PD controller but it did not work as good as the P
		# controller therefore I set the kd values to 0
	[status, framesize] = t.get(tim, wait=False, last=True)
	dt = (tim.sim[0] - oldtime)
	D = abs(kd*err)#/dt
	ref.ref[0] = P+D
	ref.ref[1] = -P-D
    cv2.namedWindow("green", cv2.WINDOW_AUTOSIZE);
    cv2.imshow("green", imgR);
    
    print 'Sim Time = ', tim.sim[0]
    print 'Engine Values', ref.ref[0],ref.ref[1]

    # Sleeps
    time.sleep(0.1)  
#-----------------------------------------------------
#-----------------------------------------------------
#-----------------------------------------------------
