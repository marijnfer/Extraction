import numpy as np
from Point import *

class TablePoint:
	def __init__(self, point,image):
		self.point = point
		self.directions = determineDirections(point,image)

	def removeDirection(self,dir):
		self.directions.remove(dir)

	def containsDirection(self,dir):
		if dir in self.directions:
			return True
		return False

	'''
	If points have a line above,.. point
	1 = left
	2 = below
	3 = right
	4 = above
	'''
	
	def draw(self,image):
		if 1 in self.directions:
			drawLine(self.point,self.point.transpose(-20,0),image)
		if 2 in self.directions:
			drawLine(self.point,self.point.transpose(0,20),image)
		if 3 in self.directions:
			drawLine(self.point,self.point.transpose(20,0),image)
		if 4 in self.directions:
			drawLine(self.point,self.point.transpose(0,-20),image)

def determineDirections(point,image):
	directions = []

	x = int(point.x)
	y = int(point.y)

	#img1 = image[y-1:y + 2,x-20:x]
	#img2 = np.transpose(image[y:y+20,x-1:x + 2])
	#img3 = image[y-1:y + 2,x:x+20]
	#img4 = np.transpose(image[y-20:y,x-1:x + 2])
	#Geen interval nemen: zie notes 24/
	img1 = image[y,x-20:x]
	img2 = np.transpose(image[y:y+20,x])
	img3 = image[y,x:x+20]
	img4 = np.transpose(image[y-20:y,x])

	#line1 = np.max(img1,axis=0)
	#line2 = np.max(img2,axis=0)
	#line3 = np.max(img3,axis=0)
	#line4 = np.max(img4,axis=0)

	#filled1 = float(np.count_nonzero(line1)) / line1.shape[0]
	#filled2 = float(np.count_nonzero(line2)) / line2.shape[0]
	#filled3 = float(np.count_nonzero(line3)) / line3.shape[0]
	#filled4 = float(np.count_nonzero(line4)) / line4.shape[0]

	filled1 = float(np.count_nonzero(img1)) / img1.shape[0]
	filled2 = float(np.count_nonzero(img2)) / img2.shape[0]
	filled3 = float(np.count_nonzero(img3)) / img3.shape[0]
	filled4 = float(np.count_nonzero(img4)) / img4.shape[0]

	if filled1 >= 0.995:
		directions.append(1)
		
	if filled2 >= 0.995:
		directions.append(2)

	if filled3 >= 0.995:
		directions.append(3)

	if filled4 >= 0.995:
		directions.append(4)

	return directions


