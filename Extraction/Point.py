from math import sqrt
import cv2
from numpy.linalg import norm
import numpy as np

class Point:
	def __init__(self,x_init,y_init):
		self.x = int(x_init)
		self.y = int(y_init)

	def pointUnpack(self):
		return self.x,self.y

	def pointToArray(self):
		array = np.zeros(2)
		array[0] = self.x
		array[1] = self.y
		return array

	#Calulates distance from self to line (p1,p2)
	def distanceToLine(self,p1,p2):
		p3 = self.pointToArray()
		p2 = p2.pointToArray()
		p1 = p1.pointToArray()

		return norm(np.cross(p2-p1, p1-p3))/norm(p2-p1) 

	def transpose(self,x,y):
		return Point(self.x+x,self.y+y)


#Distance from point a to b
def distance(a, b):
	return sqrt((a.x-b.x)**2+(a.y-b.y)**2)

#Determine all points with equal x taking allowDeviation into account
def equalX(x,pointList, allowedDeviation):
	temp = []
	for point in pointList:
		if abs(x-point.x) <= allowedDeviation:
			temp.append(point)
	return temp

#Determine all points with equal y taking allowDeviation into account
def equalY(y,pointList,allowedDeviation):
	temp = []
	for point in pointList:
		if abs(y-point.y) <= allowedDeviation:
			temp.append(point)
	return temp

def arrayToPoint(array):
	return Point(array[0],array[1])


#Determine all points to are less than allowedDeviation removed from p
def pointOccursInList(p,list, allowedDeviation):
	for i in range(0,len(list)):
		point = list[i]
		if distance(p,point) <= allowedDeviation:
			return i
	return -1


def drawLine(point1,point2,image):
	image = cv2.line(image,(int(point1.x),int(point1.y)),(int(point2.x),int(point2.y)),(255,255,0),10)
	return image

def drawLineColor(point1,point2,image,color):
	image = cv2.line(image,(int(point1.x),int(point1.y)),(int(point2.x),int(point2.y)),color,10)
	return image

#Determine minimum - maximum x - y values of array of points
def minMaxXY(numpyAr):
	minX = np.min(numpyAr[:,0])
	maxX = np.max(numpyAr[:,0])
	minY = np.min(numpyAr[:,1])
	maxY = np.max(numpyAr[:,1])

	return minX,maxX,minY,maxY

#Determine minimum y-coordinate of all points in the list
def minimumY(list):
	temp = []
	smallest = 999999
	for point in list:
		if point.y <= smallest:
			smallest = point.y
	return smallest

#Determine maximum y-coordinate of all points in the list
def maximumY(list):
	temp = []
	largest = 0
	for point in list:
		if point.y >= largest:
		   largest = point.y
	return largest

#Determine minimum x-coordinate of all points in the list
def minimumX(list):
	temp = []
	smallest = 999999
	for point in list:
		if point.x <= smallest:
			smallest = point.x
	return smallest

#Determine maximum x-coordinate of all points in the list
def maximumX(list):
	largest = 0
	for point in list:
		if point.x >= largest:
		   largest = point.x
	return largest

def pointsToArrayList(list):
	temp = np.zeros((len(list),2))
	
	for i in range(0,len(list)):
		temp[i, 0] = list[i].x
		temp[i, 1] = list[i].y

	return temp

def distancePointToLine(p1,p2,x,y):
	d1 = (p2.x-p1.x)*(p1.y-y) - (p1.x-x)*(p2.y - p1.y)
	d1 = abs(d1)/ ((p2.x-p1.x)**2+(p2.y-p1.y)**2)**0.5
	return d1

#Determine if an actual line is present on the image
def lineDetector(p1,p2,image):
	if isinstance(p1,Point):
		p1 = p1.pointToArray()
		p2 = p2.pointToArray()

	if abs(p1[0] - p2[0]) >= 8 and abs(p1[1] - p2[1]) >= 8:
		return False 

	array = np.vstack((p1,p2))
	array = array.astype(int)
	minX,maxX, minY, maxY = minMaxXY(array)


	rx1 = minX - 2
	rx2 = maxX + 3
	ry1 = minY - 2
	ry2 = maxY + 3
	segment = image[ry1:ry2,rx1:rx2]
   
	if segment.shape[0] > segment.shape[1]:
		line = np.max(segment,axis=1)
	else:
		line = np.max(segment,axis=0)
	

	filled = np.count_nonzero(line) / float(line.shape[0])
	if filled >= 0.80: 
		return True
   
	return False