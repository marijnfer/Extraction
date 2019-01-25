from Point import *
import Cluster
import cv2
import Rectangle
from TablePoint import *

class TableConstruct:
	global tollerance
	tollerance = 3
	#Eventueel alle keypoints filteren
	def __init__(self):
		self
		
def constructTable(pob1,pob2,pob3,pob4,keypoints,border,image):
	keypoints = keypoints[:]
	tables = []
	#Seperate distant points that don't belong to any table
	pob1 = Cluster.clusterBorders(pob1) 
	pob3 = Cluster.clusterBorders(pob3)

	c2 = pob3[-1,:]
	possibleC3 = pointsInInterval(0,c2[0],c2[1],keypoints)
	
	#End can also be on pob2
	for i in range(0,pob2.shape[0]):
		x = pob2[i,0]
		y = pob2[i,1]
		if (c2[1] - tollerance) <= y and y <= (c2[1] + tollerance):
			possibleC3 = np.vstack(np.array(x,y), possibleC3)
			break
	
	table1, c11,c12,c13,c14 = findCornersSimple(border.p3.pointToArray(),c2,possibleC3, pob2, image)
	tables.append(table1)

	pointsAbovePob2 = sortPointsAbovePOB2(pob2,keypoints,border.p2.pointToArray(),pob1)

	#Search next point on pob to start searching from
	index,_ = np.where(pob2 == c13)
	index = index[0]

	tables = findTables(pointsAbovePob2,index,tables,image,pob3)
	sortedPoints = sortPointsTables(tables,keypoints,pob1,pob2,pob3,border)

	image1 = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)
	image2 = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)

	#Convert points to tablePoints + remove unrelevant points
	tablePoints = []
	for i in range(0,len(sortedPoints)):
		sp = sortedPoints[i]
		temp = []
		for p in sp:
			temp.append(TablePoint(p,image))
		temp = removeUnrelevantPoints(temp,tables[i])
		tablePoints.append(temp)

	image1 = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)
	for tp in tablePoints[0]:
		tp.draw(image1)
	
	showImage(image1,'',0.3)

	image1 = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)
	for tp in tablePoints[1]:
		tp.draw(image1)
	
	showImage(image1,'',0.3)

	image1 = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)
	for tp in tablePoints[2]:
		tp.draw(image1)
	
	showImage(image1,'',0.3)
	
	


	'''
	for p in test:

		a = tables[2].pointOnBorder(p.point)
		print a, p.point
		point = Point(int(p.point.x),int(p.point.y))

		if  a == 1:
			cv2.circle(image1, (point.x,point.y), 25, (255,0,0), 3)
		if  a == 2:
			cv2.circle(image1, (point.x,point.y), 25, (0,255,0), 3)
		if  a == 3:
			cv2.circle(image1, (point.x,point.y), 25, (0,0,255), 3)
		if  a == 4:
			cv2.circle(image1, (point.x,point.y), 25, (255,255,0), 3)
	print ""
	
	showImage(image1,'',0.3)
	for tp in test:
		tp.draw(image2)
	showImage(image2,'',0.3)
	'''

	
	
	

	for tp in test:
		tp.draw(image2)
	
	showImage(image2,'',0.3)



	i = 0
	
	'''
	image2 = np.copy(image)
	image3 = np.copy(image)
	for p in sortedPoints[0]:
		cv2.circle(image, (int(p.x),int(p.y)), 25, a[i], 3)

	i=1	
	for p in sortedPoints[1]:
		cv2.circle(image2, (int(p.x),int(p.y)), 25, a[i], 3)
	

	i = 2
	for p in sortedPoints[2]:
		cv2.circle(image3, (int(p.x),int(p.y)), 25, a[i], 3)
	
	
		
	showImage(image,'',0.3)
	showImage(image2,'',0.3)
	showImage(image3,'',0.3)
	'''
	

	return 0

#Zie notes 24/1, 25/1
def removeUnrelevantPoints(tablePoints,border):
	temp = []
	for tp in tablePoints:
		
		b = border.pointOnBorder(tp.point)
		print b, tp.point
		if b == 0: # => tp always relevant for table construction
			temp.append(tp)
		else:
			#needToContain = [1,2,3,4]#[3,4,1,2] #Needs to have this direction otherwise not relevant for construction
			needToContain = [3,4,1,2]
			if tp.containsDirection(needToContain[b-1]): #needToContain[b-1]
				temp.append(tp)
				a = "add"
			else:
				a ="not"
			#print a, b, needToContain[b-1], tp.directions
		

	print len(temp), len(tablePoints)
	return temp


def sortPointsTables(tables,keypoints,pob1,pob2,pob3,border):
	sorted = []

	for t in tables:
		sorted.append([])

	for kp in keypoints:
		for i in range(0,len(tables)):
			if tables[i].containsPoint(kp):
				sorted[i].append(kp)

	for i in range(0,pob1.shape[0]):
		for j in range(0,len(tables)):
			if tables[j].containsPoint(pob1[i,:]):
				sorted[j].append(arrayToPoint(pob1[i,:]))

	for i in range(0,pob2.shape[0]):
		for j in range(0,len(tables)):
			if tables[j].containsPoint(pob2[i,:]):
				sorted[j].append(arrayToPoint(pob2[i,:]))

	for i in range(0,pob3.shape[0]):
		for j in range(0,len(tables)):
			if tables[j].containsPoint(pob3[i,:]):
				sorted[j].append(arrayToPoint(pob3[i,:]))


	if tables[0].containsPoint(border.p3):
		sorted[0].append(border.p3)

	if tables[-1].containsPoint(border.p2):
		sorted[-1].append(border.p2)


	return sorted

def findTables(pointsAbovePob2,index,tables,image,pob3):
	while True:
		matchList = findMatches(pointsAbovePob2[index],pointsAbovePob2[index + 1],image)

		pressed = True #True if 2 different tables are adjacent
		if matchList.size == 2:
			pressed = False
			index = index + 1

		lastColomnIndex = searchEnd(index,pointsAbovePob2,pob3,image)
		lastColomn = pointsAbovePob2[lastColomnIndex]

		corner2 = findMissingPoint(lastColomn[-1,:],pointsAbovePob2[index],image)

		tableTemp = Rectangle.Rectangle(pointsAbovePob2[index][0,:],corner2,lastColomn[-1,:],lastColomn[0,:])
		tables.append(tableTemp)

		#image = tableTemp.draw(np.copy(image))
		#showImage(image,'',0.3)

		index = lastColomnIndex
		if index == len(pointsAbovePob2)-1:
			break
	return tables

def findMissingPoint(corner3,colomn,image):
	if colomn.size == 2:
		if lineDetector(corner3,colomn,image):
			return colomn
	else:
		for i in range(0,colomn.shape[0]):
			if lineDetector(corner3,colomn[i,:],image):
				return colomn[i,:]
	return None

#Assumed that points in list are sorted
#Only for control
def checkIfMatch(list1,list2,image):
	if abs(list1[0,0] - list2[0,0]) <= 3:
		if abs(list1[-1,0] - list2[-1,0]) <= 3:
			return True
	return False

def searchEnd(start,pointsAbovePob2,pob3,image):
	stop = False
	while not stop:
		if findMatches(pointsAbovePob2[start],pointsAbovePob2[start + 1],image).size > 2:
			if start == len(pointsAbovePob2) -2:
				return start + 1
			else:
				start = start + 1
		else:
			return start
		
	
	return -1

#Possible problems: handle list of size 1
def findMatches(list1,list2,image):
	matchList = None

	for i in range(0,list1.shape[0]):
		for j in range(0,list2.shape[0]):
			if lineDetector(list1[i,:],list2[j,:],image):
				if matchList is None:
					matchList = list1[i,:]
				else:
					matchList = np.vstack((matchList,list1[i,:]))

	return matchList

#pob2 include
def sortPointsAbovePOB2(pob2,points,p2,pob1):
	above = []

	for i in range(0,pob2.shape[0]):
		temp = []
		for p in points:
			if abs(p.x - pob2[i,0]) <= 3:
				temp.append(p)

		temp = pointToArrayList(temp)
		temp = np.vstack((temp,pob2[i,:]))
		temp = np.sort(temp,axis = 0)[::-1]
		above.append(temp)

	temp = np.vstack((p2,pob1))
	temp = np.sort(temp,axis = 0)[::-1]

	above.append(temp)

	return above

def findCornersComplex(c1,c2,c3,c4,image):
	#c1 is always specified as np array
	#c1, c3 and c4 are np arrays of single or multiple points

	#Compute canidates c3
	corner3 = []
	if c3.size == 2:
		if lineDetector(c2,c3,image):
			corner3.append(c3)
	else:
		for i in range(0,c3.shape[0]):
			if lineDetector(c2,c3[i,:],image):
				corner3.append(c3[i,:])
	
	if len(corner3) == 0:
		print("Corner 3 not found")
		exit()

	#Compute canidates c4
	corner4 = []
	if c4.size == 2:
		if lineDetector(c1,c4,image):
			corner4.append(c4)
	else:
		for i in range(0,c4.shape[0]):
			if lineDetector(c1,c4[i,:],image):
				corner4.append(c4[i,:])
	
	if len(corner3) == 0:
		print("Corner 4 not found")
		exit()

	found = False
	for cor3 in corner3:
		for cor4 in corner4:
			if lineDetector(cor3,cor4,image):
				corner3 = cor3
				corner4 = cor4
				found = True
				break

	if found:
		b = Rectangle.Rectangle((c1),(c2),(corner3),(corner4))
		return b,c1,c2,corner3,corner4
	else:
		print("Corner3 and 4 don't match")
		exit()

def findCornersSimple(c1,c2,c3,c4,image):
	#c1 and c2 are always specified as np array
	#c3 and c4 are np arrays of points

	#Compute canidates c3
	corner3 = []
	if c3.size == 2:
		if lineDetector(c2,c3,image):
			corner3.append(c3)
	else:
		for i in range(0,c3.shape[0]):
			if lineDetector(c2,c3[i,:],image):
				corner3.append(c3[i,:])
	
	if len(corner3) == 0:
		print("Corner 3 not found")
		exit()

	#Compute canidates c4
	corner4 = []
	if c4.size == 2:
		if lineDetector(c1,c4,image):
			corner4.append(c4)
	else:
		for i in range(0,c4.shape[0]):
			if lineDetector(c1,c4[i,:],image):
				corner4.append(c4[i,:])
	
	if len(corner3) == 0:
		print("Corner 4 not found")
		exit()

	found = False
	for cor3 in corner3:
		for cor4 in corner4:
			if lineDetector(cor3,cor4,image):
				corner3 = cor3
				corner4 = cor4
				found = True
				break

	if found:
		b = Rectangle.Rectangle((c1),(c2),(corner3),(corner4))
		return b,c1,c2,corner3,corner4
	else:
		print("Corner3 and 4 don't match")
		exit()

def lineDetector(p1,p2,image):
	if abs(p1[0] - p2[0]) >= 5 and abs(p1[1] - p2[1]) >= 5:
		return False #vertical or horizontal

	array = np.vstack((p1,p2))
	array = array.astype(int)
	minX,maxX, minY, maxY = minMaxXY(array)

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

	segment = image[ry1:ry2,rx1:rx2]
   

	line = np.max(segment,axis=0)

	filled = np.count_nonzero(line) / line.shape[0]
	if filled >= 0.995:
		return True
   
	return False

def pointsInInterval(minX,maxX,ySearch,points):
	global tollerance
	interval = []
	for p in points:
		x, y = p.pointUnpack()

		contains = False
		if (ySearch - tollerance) <= y and y <= (ySearch + tollerance):
			if (minX - tollerance) <= x and x <= (maxX + tollerance):
				interval.append(p)
	
	if len(interval) == 1:
		return interval[0].pointToArray()

	return pointToArrayList(interval)
			
def pointsInInterval2(minY,maxY,xSearch,points):
	global tollerance
	remaining = []
	interval = []
	for p in points:
		x, y = p.pointUnpack()

		contains = False
		if (xSearch - tollerance) <= x and x <= (xSearch + tollerance):
			if (minY - tollerance) <= y and y <= (maxY + tollerance):
				contains = True

		if contains:
			interval.append(p)
		else:
			remaining.append(p)

	temp = pointToArrayList(interval)
	temp = np.sort(temp,axis = 0)
	return temp, remaining

def showImage(image,title,scale):
	cv2.imshow(title,cv2.resize(image,(0,0),fx=scale,fy=scale))
	cv2.waitKey(0)
	cv2.destroyAllWindows()			

			


	  