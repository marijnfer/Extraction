'''
Sources:
General: https://medium.com/coinmonks/a-box-detection-algorithm-for-any-image-containing-boxes-756c15d7ed26
https://stackoverflow.com/questions/45088134/extracting-table-structures-from-image
blobDetection: https://www.learnopencv.com/blob-detection-using-opencv-python-c/
delete files: https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder-in-python
'''

import cv2
import numpy as np
import os
import glob 
import math
from Rectangle import *
from Point import *
import shutil
import Cluster
import time
import TableConstruct

saveImages = True
savePath = 'C:\\Users\\MarijnFerrari\\Documents\\Thesis\\Extraction\\Extraction\\save\\'
mainPath = 'C:\\Users\\MarijnFerrari\\Documents\\Thesis\\Drawings\\2.png'

def showImage(image,title,scale):
	cv2.imshow(title,cv2.resize(image,(0,0),fx=scale,fy=scale))
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def keypointsToList(keypoints):
	list = []
	for kp in keypoints:
		x = int(kp.pt[0])
		y = int(kp.pt[1])
		list.append(Point(x,y))
	return list

def prepare(path):
	img = cv2.imread(path, 0)  # Read the image
	(thresh, img_bin) = cv2.threshold(img, 128, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Thresholding the image

	img_bin = 255 - img_bin  # Invert the image
	
	if saveImages:
		loc = savePath + '1 initial.png'
		cv2.imwrite(loc,img_bin)

	return img_bin

def crosspointDetection(image):
	  #showImage(img_bin)
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
	
	i = 40
	kleineKernel = 3

	# Defining a kernel length
	kernel_lengthX = np.array(image).shape[1] // i
	kernel_lengthY = np.array(image).shape[0] // i

	# A verticle kernel of (1 X kernel_length), which will detect all the verticle
	# lines from the image.
	verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,kernel_lengthY))
	verticle_kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kleineKernel))

	# A horizontal kernel of (kernel_length X 1), which will help to detect all
	# the horizontal line from the image.
	hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_lengthX, 1))
	hori_kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (kleineKernel, 1))

	# A kernel of (3 X 3) ones.
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))

	# Morphological operation to detect verticle lines from an image
	img_temp1 = cv2.erode(image, verticle_kernel, iterations=1)
	showImage(img_temp1,"",0.3)#[1838:2338,2508:3308]

	img_temp1 = cv2.dilate(img_temp1, verticle_kernel, iterations=1)
	showImage(img_temp1,"",0.3)
	img_verticle_lines = cv2.dilate(img_temp1, verticle_kernel1, iterations=3)
	showImage(img_temp1,"",0.3)
	# Morphological operation to detect horizontal lines from an image
	img_temp2 = cv2.erode(image, hori_kernel, iterations=1)
	img_temp2 = cv2.dilate(img_temp2, hori_kernel, iterations=1)
	img_horizontal_lines = cv2.dilate(img_temp2, hori_kernel1, iterations=3)

	#combined = np.concatenate((verticle_lines_img,horizontal_lines_img),axis = 1)

	alpha = 0.5
	beta = 1.0 - alpha
	#Horizontale en verticale lijnen samenvoegen
	img_final_bin = cv2.addWeighted(img_verticle_lines, alpha, img_horizontal_lines, beta, 0.0)
	

	#Thresholden om snijpunten over te houden (hoogste I)
	(thresh, img_cross) = cv2.threshold(img_final_bin, 200, 255, cv2.THRESH_BINARY)
	#showImage(img_cross,'cross',0.3)
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

def blobDetection(image): 
	#Snijpunten zijn blobs van witte pixels
	params = cv2.SimpleBlobDetector_Params()
 
	# Change thresholds
	#params.minThreshold = 10;
	#params.maxThreshold = 200;
 
	# Filter by Area.
	params.filterByArea = False
	params.minArea = 1
 
	# Filter by Circularity
	params.filterByCircularity = False
	params.minCircularity = 0.0000001
 
	# Filter by Convexity
	params.filterByConvexity = False
	params.minConvexity = 0.0000001
 
	# Filter by Inertia
	params.filterByInertia = False
	params.minInertiaRatio = 0.0000001

	detector = cv2.SimpleBlobDetector_create(params)
 
	keypoints = detector.detect(cv2.bitwise_not(image))

	keypoints = keypointsToList(keypoints)
	img_keypoints = np.copy(image)
	
	if saveImages:
		for point in keypoints:
			cv2.circle(img_keypoints, (point.x,point.y), 25, (255,0,0), 3)

		loc = savePath + '6 keypoints.png'
		cv2.imwrite(loc,img_keypoints)

		#showImage(img_keypoints,"keypoints",0.3)
	
	return keypoints

def getCornerPoints(image,keypoints):
	sizeY = image.shape[0]
	sizeX = image.shape[1]

	# maximale afstand kader => opzoeken in bin normen
	# beter vaste grootste werken (dus vaste image size)?
	# verschillende cornersize voor x en y ?
	cornerSize = 0.1
	
	windowX = int(cornerSize * sizeX)
	windowY = int(cornerSize * sizeY)

	corners = []
	image = np.copy(image)
	for point in keypoints:
		x = point.x
		y = point.y
		if (0 <= y and y <= windowY) or (sizeY - windowY <= y):
			if (0 <= x and x <= windowX) or (x >= sizeX - windowX):
				corners.append(Point(x,y))

	if saveImages:
		for point in corners:
			cv2.circle(image, (point.x,point.y), 25, (255,0,0), 3)
	
		#showImage(image,"cornerpoints",0.3)
		loc = savePath + '7 corners.png'
		cv2.imwrite(loc,image)

	return corners

def determineBoundingBox(image,cornerpoints):
	sizeY = image.shape[0]
	sizeX = image.shape[1]
	
	# methode2 tijdscomlexiteits is slecht maar detecteerd wel alle mogelijke
	# rechthoeken
	possibleBorders = []
	start = 0

	for i in range(0,len(cornerpoints)):
		point = cornerpoints[i]
		x,y = point.pointUnpack()
		eqX = equalX(x,cornerpoints[i + 1:len(cornerpoints)],1)
		eqY = equalY(y,cornerpoints[i + 1:len(cornerpoints)],1)
	   
		for p1 in eqX:
			for p2 in eqY:
				extractedPoint = Point(p2.x,p1.y)
				index = pointOccursInList(extractedPoint,cornerpoints,1)
				if index != -1:
					possibleBorders.append(Rectangle(point,p1,p2,cornerpoints[index]))


	if saveImages:
		i = 0
		for r in possibleBorders:

				
			img = np.copy(image)
			img = r.draw(img)
			#showImage(img,"",0.3)


			loc = savePath + 'bordersCross\\{}.png'.format(i)
			files = glob.glob(loc)
			for f in files:
				os.remove(f)

			cv2.imwrite(loc,img)         
			loc = savePath + 'orignalCross\\{}.png'.format(i)

			files = glob.glob(loc)
			for f in files:
				os.remove(f)

			img = np.copy(cv2.imread(mainPath))
			img = r.draw(img)
			cv2.imwrite(loc,img)
			i+=1
	  
	#Alle kleine rechthoeken weg => kunnen nooit een rand zijn
	minArea = 0.7 * image.shape[0] * image.shape[1]
	possibleBorders = [rect for rect in possibleBorders if rect.area > minArea]

	border = None
	if len(possibleBorders) == 1:
		border = possibleBorders[0]
	elif len(possibleBorders) == 2:
	   r1 = possibleBorders[0]
	   r2 = possibleBorders[1]

		
	   if r1.area > r2.area:
		   if r1.contains(r2):
				border = r2
	   else:
		   if r2.contains(r1):
				border = r1

	'''
	Tekeningen hebben typisch een primary en secondare rand (check als dit ook effectief zo is)
	Indien er iets niet aan de voorwaarden voldoet => border blijft None
	Bewust gedaan => indien het crasht zijn mijn voorwaarden slecht en moet ik deze herzien
	'''
	
	if saveImages:
		loc = savePath + '8 border final.png'
		img = np.copy(cv2.imread(mainPath))
		img = border.draw(img)
		cv2.imwrite(loc,img)

	return border

def inInterval(value, ref, interval):
	if value >= ref - interval and value <= ref + interval:
		return True
	else: 
		return False

def keypointsOnBorder(keypoints, border,allowedDeviation,image):
	pob1 = [] # linkse verticale
	pob2 = [] # onderste horizontale
	pob3 = [] # rechtse verticale
	pob4 = [] # bovenste horizontale
	kps = []
	# Indien een punt dichtbij een hoekpunt ligt => ligt het kort bij twee rechtes
	# If structuur kan dus problemen opleverne
	# Maar komt dit wel voor bij grote tekeningen en <= 2 ?
	for point in keypoints:
		if border.onBorder(point):
			a = 0
		elif point.distanceToLine(border.p1,border.p2) <= 2:
			pob1.append(point)
		elif point.distanceToLine(border.p2,border.p3) <= 2:
			pob2.append(point)
		elif point.distanceToLine(border.p3,border.p4) <= 2:
			pob3.append(point)
		elif point.distanceToLine(border.p4,border.p1) <= 2:
			pob4.append(point)
		else:
			kps.append(point)

	if saveImages:
		image = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)
		for point in pob1:
			cv2.circle(image, (point.x,point.y), 25, (255,0,0), 3)
		for point in pob2:
			cv2.circle(image, (point.x,point.y), 25, (0,255,0), 3)
		for point in pob3:
			cv2.circle(image, (point.x,point.y), 25, (0,0,255), 3)
		for point in pob4:
			cv2.circle(image, (point.x,point.y), 25, (255,255,0), 3)

		loc = savePath + '8 points on border.png'
		cv2.imwrite(loc,image)


	return pob1, pob2, pob3, pob4

def deleteBorderFromKeypoints(border,keypoints, pob1,pob2,pob3,pob4,image):
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

	img = cv2.cvtColor(np.zeros_like(image),cv2.COLOR_GRAY2RGB)

	for point in temp:
		cv2.circle(img, (point.x,point.y), 25, (255,255,255), 3)
		

	for point in pob1:
		cv2.circle(img, (point.x,point.y), 25, (255,0,0), 3)
	for point in pob2:
		cv2.circle(img, (point.x,point.y), 25, (0,255,0), 3)
	for point in pob3:
		cv2.circle(img, (point.x,point.y), 25, (0,0,255), 3)
	for point in pob4:
		cv2.circle(img, (point.x,point.y), 25, (255,255,0), 3)

	loc = savePath + '9 delete outside border.png'
	cv2.imwrite(loc,img)
   


		
	return temp
	 




def application(path):
	start = time.clock()
	if saveImages:
		for root, dirs, files in os.walk(savePath):
			for f in files:
				os.unlink(os.path.join(root, f))
		
	img_initial = prepare(path)
	print "%.2gs" % (time.clock() - start)
	img_crosspoints = crosspointDetection(img_initial)
	print "%.2gs" % (time.clock() - start)
	keypoints = blobDetection(img_crosspoints)
	print "%.2gs" % (time.clock() - start)
	cornerpoints = getCornerPoints(img_crosspoints,keypoints)
	print "%.2gs" % (time.clock() - start)
	border = determineBoundingBox(img_crosspoints,cornerpoints)
	print "%.2gs" % (time.clock() - start)
	pob1,pob2,pob3,pob4 = keypointsOnBorder(keypoints, border,2,img_crosspoints)
	print "%.2gs" % (time.clock() - start)
	keypoints = deleteBorderFromKeypoints(border,keypoints,pob1,pob2,pob3,pob4,img_crosspoints)
	print "%.2gs" % (time.clock() - start)

	pob1 = pointToArrayList(pob1)
	pob2 = pointToArrayList(pob2)
	pob3 = pointToArrayList(pob3)
	pob4 = pointToArrayList(pob4)

	TableConstruct.constructTable(pob1,pob2,pob3,pob4,keypoints,border,img_initial)
	

	print "%.2gs" % (time.clock() - start)
	#border1 = determineBoundingBox1(img_crosspoints,keypoints)


	print("done")
	

application(mainPath)

