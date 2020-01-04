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

	def __repr__(self):
		return "".join(["Point(", str(self.x), ",", str(self.y), ")"])

	def pointToArray(self):
		array = np.zeros(2)
		array[0] = self.x
		array[1] = self.y
		return array


	def distanceToLine(self,p1,p2):
		p3 = self.pointToArray()
		p2 = p2.pointToArray()
		p1 = p1.pointToArray()

		#negatieve afstand      np.cross(p2-p1,p3-p1)/norm(p2-p1)
		return norm(np.cross(p2-p1, p1-p3))/norm(p2-p1) #positieve afstand

	def transpose(self,x,y):
		return Point(self.x+x,self.y+y)


def distance(a, b):
	return sqrt((a.x-b.x)**2+(a.y-b.y)**2)

def equalX(x,pointList, allowedDeviation):
	temp = []
	for point in pointList:
		if abs(x-point.x) <= allowedDeviation:
			temp.append(point)
	return temp

def equalY(y,pointList,allowedDeviation):
	temp = []
	for point in pointList:
		if abs(y-point.y) <= allowedDeviation:
			temp.append(point)
	return temp

def arrayToPoint(array):
	return Point(array[0],array[1])

# Eventueel mogelijk afwijkingen in rekening brengen 
# Daarom geen x == x1 en y == y1
def pointOccursInList(p,list, allowedDeviation):
	for i in range(0,len(list)):
		point = list[i]
		if distance(p,point) <= allowedDeviation:
			return i
	return -1


def drawLine(point1,point2,image):
	image = cv2.line(image,(int(point1.x),int(point1.y)),(int(point2.x),int(point2.y)),(255,255,0),2)
	return image

def drawLineColor(point1,point2,image,color):
	image = cv2.line(image,(int(point1.x),int(point1.y)),(int(point2.x),int(point2.y)),color,3)
	return image

def minMaxXY(numpyAr):
	minX = np.min(numpyAr[:,0])
	maxX = np.max(numpyAr[:,0])
	minY = np.min(numpyAr[:,1])
	maxY = np.max(numpyAr[:,1])

	return minX,maxX,minY,maxY


def minimumY(list):
	temp = []
	smallest = 999999
	for point in list:
		if point.y <= smallest:
			smallest = point.y
	return smallest

def maximumY(list):
	temp = []
	largest = 0
	for point in list:
		if point.y >= largest:
		   largest = point.y
	return largest

def minimumX(list):
	temp = []
	smallest = 999999
	for point in list:
		if point.x <= smallest:
			smallest = point.x
	return smallest

def maximumX(list):
	largest = 0
	for point in list:
		if point.x >= largest:
		   largest = point.x
	return largest

def pointToArrayList(list):
	temp = np.zeros((len(list),2))
	
	for i in range(0,len(list)):
		temp[i, 0] = list[i].x
		temp[i, 1] = list[i].y

	return temp


def boundaries(p1,p2):
	if p1.x >= p2.x:
		maxx = p1.x
		minx = p2.x
	else:
		maxx = p2.x
		minx = p1.x

	if p1.y >= p2.y:
		maxy = p1.y
		miny = p2.y
	else:
		maxy = p2.y
		miny = p1.y

	return minx,maxx, miny, maxy

def averagePoint(list):
	x = 0
	y = 0
	for p in list:
		x += p.x
		y += p.y
	return Point(x/len(list),y/len(list))

def distancePointToLine(p1,p2,x,y):
	d1 = (p2.x-p1.x)*(p1.y-y) - (p1.x-x)*(p2.y - p1.y)
	d1 = abs(d1)/ ((p2.x-p1.x)**2+(p2.y-p1.y)**2)**0.5
	return d1


def lineDetector(p1,p2,image):
	if isinstance(p1,Point):
		p1 = p1.pointToArray()
		p2 = p2.pointToArray()

	if abs(p1[0] - p2[0]) >= 8 and abs(p1[1] - p2[1]) >= 8:
		return False #vertical or horizontal

	array = np.vstack((p1,p2))
	array = array.astype(int)
	minX,maxX, minY, maxY = minMaxXY(array)


	'''
	if minX == maxX:
		rx1 = minX - 1
		rx2 = minX + 2
	else:
		rx1 = minX
		rx2 = maxX

	if minY == maxY:
		ry1 = minY - 1
		ry2 = minY + 2
	else:
		ry1 = minY
		ry2 = maxY
	'''
	rx1 = minX - 2
	rx2 = maxX + 3
	ry1 = minY - 2
	ry2 = maxY + 3
	segment = image[ry1:ry2,rx1:rx2]
   
	if segment.shape[0] > segment.shape[1]:
		line = np.max(segment,axis=1)
	else:
		line = np.max(segment,axis=0)
	###########
	'''
	cv2.imshow("",cv2.resize(segment,(0,0),fx=1,fy=1))
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	'''
	

	filled = np.count_nonzero(line) / float(line.shape[0])
	if filled >= 0.80: ###
		return True
   
	return False