'''
Source: https://codereview.stackexchange.com/questions/151309/check-if-two-rectangles-overlap
'''
from Point import *
import cv2
import numpy as np

class Rectangle:
	# 4 punten genomen ipv 2 omdat de rechthoeken een beetje kunnen afwijken
	# Bij init: punten formatten zodat p1 altijd het punt links boven,...
	def __init__(self, p1,p2,p3,p4):
		points = [p1,p2,p3,p4]
		dis = np.zeros(4)

		#punt dichste bij 0,0 is het punt links boven
		for i in range(0,4):
			dis[i] = distance(points[i],Point(0,0))

		index = np.argmin(dis)
		self.p1 = points[index]
		points.remove(points[index])

		self.p2 = equalX(self.p1.x,points,5)[0]
		points.remove(self.p2)

		self.p4 = equalY(self.p1.y,points,5)[0]
		points.remove(self.p4)

		self.p3 = points[0]
		
		'''
		# ensure that all points are in the correct order
		if x1 < x2:
			if y1 < y2:
				self.p1 = Point(x1,y1)
				self.p2 = Point(x2,y2)
			else:
				self.p1 = Point(x1,y2)
				self.p2 = Point(x2,y1)
		else:
			if y1 < y2:
				self.p1 = Point(x2,y1)
				self.p2 = Point(x1,y2)
			else:
				self.p1 = Point(x2,y2)
				self.p2 = Point(x1,y1)
		'''
   
	def onBorder(self,point):
		if distance(self.p1,point) == 0:
			return True
		elif distance(self.p2,point) == 0:
			return True
		elif distance(self.p3,point) == 0:
			return True
		elif distance(self.p4,point) == 0:
			return True
		return False


	def draw(self,image):
		image = drawLine(self.p1,self.p2,image)
		image = drawLine(self.p2,self.p3,image)
		image = drawLine(self.p3,self.p4,image)
		image = drawLine(self.p4,self.p1,image)
		return image

	#True als de eerste rechthoek de tweede volledig omvat (mogen samenvallen maar niet kruisen)
	def contains(self,r):
		if distance(self.p1,Point(0,0)) <= distance(r.p1,Point(0,0)):
			if distance(self.p2,Point(0,0)) >= distance(r.p2,Point(0,0)):
				return True
		return False

	def is_intersect(self, other):
		if self.min_x > other.max_x or self.max_x < other.min_x:
			return False
		if self.min_y > other.max_y or self.max_y < other.min_y:
			return False
		return True

	def __and__(self, other):
		if not self.is_intersect(other):
			return Rectangle()
		min_x = max(self.min_x, other.min_x)
		max_x = min(self.max_x, other.max_x)
		min_y = max(self.min_y, other.min_y)
		max_y = min(self.max_y, other.max_y)
		return Rectangle(min_x, max_x, min_y, max_y)

	intersect = __and__

	def __or__(self, other):
		min_x = min(self.min_x, other.min_x)
		max_x = max(self.max_x, other.max_x)
		min_y = min(self.min_y, other.min_y)
		max_y = max(self.max_y, other.max_y)
		return Rectangle(min_x, max_x, min_y, max_y)

	union = __or__

	def __str__(self):
		return 'Rectangle({self.min_x},{self.max_x},{self.min_y},{self.max_y})'.format(self=self)

	@property
	def area(self):
		return (self.p3.x - self.p2.x) * (self.p2.y - self.p1.y)

