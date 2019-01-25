import numpy as np
from Point import *

class TablePoint:
	def __init__(self, point,image):
		self.point = point
		self.directions = determineDirections(point,image)
		self.amount = len(self.directions)

		#Amount tables that can be constructed with an edge
		self.s = [0,0,0,0]

		if 1 in self.directions:
			if 2 in self.directions:
				self.s[0] = self.s[0] + 1
			if 4 in self.directions:
				self.s[0] = self.s[0] + 1
		if 2 in self.directions:
			if 1 in self.directions:
				self.s[1] = self.s[1] + 1
			if 3 in self.directions:
				self.s[1] = self.s[1] + 1
		if 3 in self.directions:
			if 2 in self.directions:
				self.s[2] = self.s[2] + 1
			if 4 in self.directions:
				self.s[2] = self.s[2] + 1
		if 4 in self.directions:
			if 1 in self.directions:
				self.s[3] = self.s[3] + 1
			if 3 in self.directions:
				self.s[3] = self.s[3] + 1



	def removeDirection(self,dir):
		self.s[dir - 1] = self.s[dir - 1] - 1
		if self.s[dir - 1] == 0:
			self.directions.remove(dir)
			self.amount = len(self.directions)

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

	#Returns 10000 if point isn't on the same vertical, horizontal
	#Depending on the direction
	#Only to return valid points (Line needs to exist)
	#Notes 25/1 p2
	def distanceToTablePoint(self, tp,direction,directionContraint):
		offset = 2
		xSelf = self.point.x
		ySelf = self.point.y

		xTP = tp.point.x
		yTP = tp.point.y

		if not tp.containsDirection(directionContraint):
			return 10000

		if direction == 1:
			if ySelf-offset <= yTP and yTP <= ySelf + offset:
				if xSelf > xTP:
					return xSelf - xTP
		elif direction == 2:
			if xSelf-offset <= xTP and xTP <= xSelf + offset:
				if ySelf < yTP:
					return yTP-ySelf
		elif direction == 3:
			if ySelf-offset <= yTP and yTP <= ySelf + offset:
				if xSelf < xTP:
					return xTP - xSelf
		elif direction == 4:
			if xSelf-offset <= xTP and xTP <= xSelf + offset:
				if ySelf > yTP:
					return ySelf - yTP
		return 10000

	def directionCombos(self):
		param1= []
		param2 = []

		if 1 in self.directions:
			param1.append(1)
		if 2 in self.directions:
			param2.append(2)
		if 3 in self.directions:
			param1.append(3)
		if 4 in self.directions:
			param2.append(4)
		return param1, param2

	def directionCombos2(self):
		temp = []
		param1 = []
		param2 = []

		if 1 in self.directions:
			param1.append(1)
		if 2 in self.directions:
			param2.append(2)
		if 3 in self.directions:
			param1.append(3)
		if 4 in self.directions:
			param2.append(4)

		for i in param1:
			for j in param2:
				temp.append([i,j])

		return temp
	
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



