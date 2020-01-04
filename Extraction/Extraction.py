'''
Sources:
General: https://medium.com/coinmonks/a-box-detection-algorithm-for-any-image-containing-boxes-756c15d7ed26
https://stackoverflow.com/questions/45088134/extracting-table-structures-from-image
blobDetection: https://www.learnopencv.com/blob-detection-using-opencv-python-c/
delete files: https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder-in-python
'''

import numpy as np
import cv2
import os
import glob 
import math
from Rectangle import *
from Point import *
import shutil
import time
import TableConstruct

import matplotlib.pyplot as plt #importing matplotlib
saveImages = True
showImages = False
scale = 1

basePath = 'C:\\Users\\MarijnFerrari\\Desktop\\Thesis\\'
savePath = basePath + 'Drawings2\\Results\\'
mainPath = basePath + 'Drawings2\\'

def showImage(image,title):
	if showImages:
		cv2.imshow(title,cv2.resize(image,(0,0),fx=scale,fy=scale))
		cv2.waitKey(0)
		cv2.destroyAllWindows()


#Load and convert to binary
def prepare(path,savePath):
	img = cv2.imread(path, 0) 
	(thresh, img_bin) = cv2.threshold(img, 200, 255,cv2.THRESH_BINARY) 
	showImage(img_bin,"Initial image")
																																  
	img_bin = 255 - img_bin  # Invert the image

	showImage(img_bin,"Initial image")
	
	if saveImages:
		loc = savePath + '1 initial.png'
		cv2.imwrite(loc,img_bin)

	return img_bin

#Use morphological operators to extract horizontal and vertical lines
#Extract crossings by averaging horizontal and vertical line images followed by threshold
def crosspointDetection(image,savePath):
	kernel_lengthX = np.array(image).shape[1] // 45
	kernel_lengthY = np.array(image).shape[0] // 45
	kernel_length_small = 3

	verticle_kernel_L = cv2.getStructuringElement(cv2.MORPH_RECT, (1,kernel_lengthY))
	verticle_kernel_s = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length_small))

	horizontal_kernel_L = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_lengthX, 1))
	horizontal_kernel_s = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length_small, 1))

	img_verticle_lines = cv2.erode(image, verticle_kernel_L, iterations=1)
	img_verticle_lines = cv2.dilate(img_verticle_lines, verticle_kernel_L, iterations=1)
	#Extra dilations such that lines are extended to make sure vertical and horizontal lines cross
	img_verticle_lines = cv2.dilate(img_verticle_lines, verticle_kernel_s, iterations=3)

	showImage(img_verticle_lines,"Vertical lines")

	img_horizontal_lines = cv2.erode(image, horizontal_kernel_L, iterations = 1)
	img_horizontal_lines = cv2.dilate(img_horizontal_lines, horizontal_kernel_L, iterations = 1)
	#Extra dilations such that lines are extended to make sure vertical and horizontal lines cross
	img_horizontal_lines = cv2.dilate(img_horizontal_lines, horizontal_kernel_s, iterations = 3)
	showImage(img_horizontal_lines,"Horizontal lines")

	#Average vertical and horizontal images
	img_final_bin = cv2.addWeighted(img_verticle_lines, 0.5, img_horizontal_lines, 0.5, 0.0)
	showImage(img_final_bin,"Horizontal and vertical lines combined")

	#Threshold to only retain crossings
	(thresh, img_cross) = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY)
	showImage(img_cross,"Crossings")

	if saveImages:
		loc = savePath + '2 vertical lines.png'
		cv2.imwrite(loc,img_verticle_lines)

		loc = savePath + '3 horizontal lines.png'
		cv2.imwrite(loc,img_horizontal_lines)

		loc = savePath + '4 vertical and horizontal lines.png'
		cv2.imwrite(loc,img_final_bin)

		loc = savePath + '5 crossings.png'
		cv2.imwrite(loc,img_cross)

	return img_cross


#Determine locations of crossings
def blobDetection(image,savePath): 
	params = cv2.SimpleBlobDetector_Params()
	
	params.minThreshold = 1
	params.maxThreshold = 255
 
	params.filterByArea = False
	params.minArea = 0

	params.filterByCircularity = False
	params.minCircularity = 0
 
	params.filterByConvexity = False
	params.minConvexity = 0
	
	params.filterByInertia = False
	params.minInertiaRatio = 0
	
	params.minDistBetweenBlobs = 5

	detector = cv2.SimpleBlobDetector_create(params)
 
	keypoints = detector.detect(cv2.bitwise_not(image))


	temp = []
	for kp in keypoints:
		x = int(kp.pt[0])
		y = int(kp.pt[1])
		temp.append(Point(x,y))
	keypoints = temp

	img_keypoints = np.copy(image)

	for point in keypoints:
		cv2.circle(img_keypoints, (point.x,point.y), 8, (255,0,0), 3)

	if saveImages:
		loc = savePath + '6 keypoints.png'
		cv2.imwrite(loc,img_keypoints)
	showImage(img_keypoints,"Detected crossings")

	return keypoints


#Extract all crosspoints in boundingbox (10% of image size in each direction)
#for each corner
def getCornerPoints(image,keypoints,savePath):
	sizeY = image.shape[0]
	sizeX = image.shape[1]

	cornerSize = 0.1
	
	windowX = int(cornerSize * sizeX)
	windowY = int(cornerSize * sizeY)

	corners = []
	for i in range(4):
		corners.append([])

	image = np.copy(image)
	for point in keypoints:
		x = point.x
		y = point.y

		if (0 <= y and y <= windowY):
			if (0 <= x and x <= windowX):
				corners[0].append(Point(x,y))	#Top left

			elif (x >= sizeX - windowX):
				corners[1].append(Point(x,y))	#Top right
		
		elif (sizeY - windowY <= y):
			if (0 <= x and x <= windowX):
				corners[2].append(Point(x,y))	#Bottom left

			elif (x >= sizeX - windowX):
				corners[3].append(Point(x,y))	#Bottom right

	img = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB) 

	for point in corners[0]:
		cv2.circle(img, (point.x,point.y), 8, (255,0,0), 3)

	for point in corners[1]:
		cv2.circle(img, (point.x,point.y), 8, (0,255,0), 3)

	for point in corners[2]:
		cv2.circle(img, (point.x,point.y), 8, (0,0,255), 3)

	for point in corners[3]:
		cv2.circle(img, (point.x,point.y), 8, (255,255,0), 3)


	X = img.shape[1]
	Y = img.shape[0]

	sizeX = X / 10
	sizeY = Y / 10

	cv2.rectangle(img,(1,1),(sizeX,sizeY),(255,0,0),3)
	cv2.rectangle(img,(X - sizeX - 1,1),(X - 1,sizeY - 1),(0,255,0),3)
	cv2.rectangle(img,(1,Y - 1),(sizeX,Y - sizeY),(0,0,255),3)
	cv2.rectangle(img,(X - 1,Y - 1),(X - 1 - sizeX,Y - 1 - sizeY),(255,255,0),3)

	if saveImages:
		loc = savePath + '7 corners.png'
		cv2.imwrite(loc,img)
	showImage(img,"Corner points")


	return corners

#Determine border 
def determineBorder(image,cornerpoints,savePath):
	sizeY = image.shape[0]
	sizeX = image.shape[1]
	
	possibleBorders = []
	start = 0

	topLeft = cornerpoints[0]
	topRight = cornerpoints[1]
	bottomLeft = cornerpoints[2]
	bottomRight = cornerpoints[3]


	for p1 in topLeft:
		eqX = equalX(p1.x,bottomLeft,5)
		eqY = equalY(p1.y,topRight,5)

		for p2 in eqX:
			for p3 in eqY:
				index = pointOccursInList(Point(p3.x,p2.y),bottomRight,5)
				if index != -1:
					possibleBorders.append(Rectangle(p1,p2,p3,bottomRight[index]))


	temp = []
	for pb in possibleBorders:
		if pb.validBorder(image): temp.append(pb)
	possibleBorders = temp

	border = largestRectangle(possibleBorders)#########smallestRectangle(possibleBorders)

	imgBorder = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)
	imgBorders = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)

	border.drawColor(imgBorder,list(np.random.choice(range(256), size=3)))

	for r in possibleBorders:
		r.drawColor(imgBorders,list(np.random.choice(range(256), size=3)))
	
	if saveImages:
		loc = savePath + '8 detected borders.png'
		cv2.imwrite(loc,imgBorders)

		loc = savePath + '9 final border.png'
		cv2.imwrite(loc,imgBorder)


	showImage(imgBorders,"Detected borders")
	showImage(imgBorder,"Final borders")

	return border


#Determine all crossing on the border
def keypointsOnBorder(keypoints, border,allowedDeviation,image,savePath):
	pob1 = [] # Vertical left
	pob2 = [] # Horizontal bottom
	pob3 = [] # Vertical right
	pob4 = [] # Horizontal top
	kps = []
	offset = 0

	for point in keypoints:
		if border.pointBelongsToBorder(point):
			continue
		elif border.containsPoint(point,2):
			if point.distanceToLine(border.p1,border.p2) <= 4:
				pob1.append(point)
			elif point.distanceToLine(border.p2,border.p3) <= 4:
				pob2.append(point)
			elif point.distanceToLine(border.p3,border.p4) <= 4:
				pob3.append(point)
			elif point.distanceToLine(border.p4,border.p1) <= 4:
				pob4.append(point)
			else:
				kps.append(point)


	img = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)

	for point in pob1:
		cv2.circle(img, (point.x,point.y), 8, (255,0,0), 3)
	for point in pob2:
		cv2.circle(img, (point.x,point.y), 8, (0,255,0), 3)
	for point in pob3:
		cv2.circle(img, (point.x,point.y), 8, (0,0,255), 3)
	for point in pob4:
		cv2.circle(img, (point.x,point.y), 8, (255,255,0), 3)

	if saveImages:
		loc = savePath + '10 points on border.png'
		cv2.imwrite(loc,img)


	return pob1, pob2, pob3, pob4

#Determine all points inside the border 
def deleteBorderFromKeypoints(border,keypoints, pob1,pob2,pob3,pob4,image,savePath):
	del keypoints[pointOccursInList(border.p1,keypoints,0)]
	del keypoints[pointOccursInList(border.p2,keypoints,0)]
	del keypoints[pointOccursInList(border.p3,keypoints,0)]
	del keypoints[pointOccursInList(border.p4,keypoints,0)]

	# Border limits
	x1 = maximumX(pob1)
	y1 = minimumY(pob2)
	x2 = minimumX(pob3)
	y2 = maximumY(pob4)

	temp = []
	for p in keypoints:
		if p.x > x1 and p.x < x2:
			if p.y > y2 and p.y < y1:
				temp.append(p)		
	return temp

def application(path,savePath, cellSavePath,cellOCRPath):
	start = time.clock()

	try:
		for root, dirs, files in os.walk(savePath):
			for f in files:
				os.unlink(os.path.join(root, f))
	except:
		print savePath + "	file error"
		
	img_initial = prepare(path,savePath)
	
	img_crosspoints = crosspointDetection(img_initial,savePath)
	
	keypoints = blobDetection(img_crosspoints,savePath)

	cornerpoints = getCornerPoints(img_initial,keypoints,savePath)

	border = determineBorder(img_initial,cornerpoints,savePath)

	pob1,pob2,pob3,pob4 = keypointsOnBorder(keypoints, border,2,img_initial,savePath)

	keypoints = deleteBorderFromKeypoints(border,keypoints,pob1,pob2,pob3,pob4,img_initial,savePath)

	stop1 = time.clock()
	print "Preparation and border detection	%.3gs" % (stop1- start)

	TableConstruct.constructTable(pob1,pob2,pob3,pob4,keypoints,border,img_initial,savePath,cellSavePath,path,cellOCRPath)
	stop2 = time.clock()


	print "Cell detection				%.3gs" % (stop2- stop1)



	
startTotal = time.clock()
for i in range(0,180):
	print "Drawing {}					". format(i)
	start = time.clock()
	imagePath = mainPath + '{}.png'.format(i)
	resultsPath = savePath + '{}\\'.format(i)
	cellSavePath = savePath + '{}\\Cells\\'.format(i)
	cellOCRPath = savePath + '{}\\OCR\\'.format(i)

	application(imagePath,resultsPath,cellSavePath,cellOCRPath)
	print "Total proccesing time image {}		%.3gs".format(i) % ( time.clock()-start)
	print 

print
print
print "Proccesing time				%.3gs" % ( time.clock()-startTotal)



