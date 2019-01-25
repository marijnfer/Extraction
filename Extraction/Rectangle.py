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
		if not isinstance(p1,Point):
			p1 = arrayToPoint(p1)

		if not isinstance(p2,Point):
			p2 = arrayToPoint(p2)

		if not isinstance(p3,Point):
			p3 = arrayToPoint(p3)

		if not isinstance(p4,Point):
			p4 = arrayToPoint(p4)



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

		

	def containsPoint(self,point):
		if isinstance(point,Point):
			x = point.x
			y = point.y
		else:
			x = point[0]
			y = point[1]

		#Quick check if points lies between border
		if self.p1.x <= x and x <= self.p4.x:
			if self.p1.y <= y and self.p2.y:
				return True
		
		'''
		#Points near 
		if distancePointToLine(self.p1,self.p2,x,y) <= 2:
			return True
		if distancePointToLine(self.p2,self.p3,x,y) <= 2:
			return True
		if distancePointToLine(self.p3,self.p4,x,y) <= 2:
			return True
		if distancePointToLine(self.p4,self.p1,x,y) <= 2:
			return True
		return False
		'''


		
	def pointBelongsToBorder(self,point):
		if distance(self.p1,point) == 0:
			return True
		elif distance(self.p2,point) == 0:
			return True
		elif distance(self.p3,point) == 0:
			return True
		elif distance(self.p4,point) == 0:
			return True
		return False

	def pointOnBorder(self,point):
		if self.pointBelongsToBorder(point):
			return 0


		if distancePointToLine(self.p1,self.p2,point.x,point.y) <=2:
			return 1
		if distancePointToLine(self.p2,self.p3,point.x,point.y) <=2:
			return 2
		if distancePointToLine(self.p3,self.p4,point.x,point.y) <=2:
			return 3
		if distancePointToLine(self.p4,self.p1,point.x,point.y) <=2:
			return 4
		return 0


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

	
