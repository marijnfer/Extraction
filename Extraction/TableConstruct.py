from Point import *
import Cluster
import cv2
import Rectangle
from TablePoint import *
import random

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



	for tp in tablePoints[0]:
		#tp.draw(image2)
		print tp.point
	#showImage(image2,'',0.3)



	constructTables(tablePoints[0],image1)


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

	return 0

#25/01
def constructTables(tablePoints,image):
	tables = []
	img = np.copy(image)
	
	startIndex = 0
	directionsIndex = 0
	completlySearched = True
	directionsTransform = [3,4,1,2]		
	tables = []

	while True:
		

		if completlySearched:
			startPoint = tablePoints[0]
			tablePoints.remove(startPoint) 
			directions = startPoint.directionCombos2()
			directionsIndex = 0
			directionsIndexMax = len(directions) - 1
			sortedDirections = sortInToDirections(tablePoints)
			printSizeTP(tablePoints,sortedDirections)
			completlySearched  = False
		

		while True:
			image1 = np.copy(image)

			dirHor = directions[directionsIndex][0]
			dirVer = directions[directionsIndex][1]

			cv2.circle(image1, (startPoint.point.x,startPoint.point.y), 25, (255,0,0), 3)

			edge1 = searchClosestPoint(startPoint,sortedDirections,dirHor,dirVer)
			cv2.circle(image1, (edge1.point.x,edge1.point.y), 25, (0,255,0), 3)
			if not edge1.containsDirection(dirVer):
				if directionsIndex == directionsIndexMax:
					completlySearched = True
					break

				directionsIndex = directionsIndex + 1
				#showImage(image1,'hor',0.3)
				continue

			edge2 = searchClosestPoint(startPoint,sortedDirections,dirVer,dirHor)	
			cv2.circle(image1, (edge2.point.x,edge2.point.y), 25, (0,0,255), 3)
			if not edge2.containsDirection(dirHor):
				if directionsIndex == directionsIndexMax:
					completlySearched = True
					break

				directionsIndex = directionsIndex + 1
				#showImage(image1,'ver',0.3)
				continue
			#showImage(image1,'end',0.3)
			
			edge3 = searchClosestPoint(edge1,sortedDirections,dirVer,directionsTransform[dirHor-1])
			edge4 = searchClosestPoint(edge2,sortedDirections,dirHor,directionsTransform[dirVer-1])


			#Should never be the case because of the direction constraint (Just to be sure)
			if not distance(edge3.point,edge4.point) == 0:
				print "Found edges don't match"
				exit()

			table = Rectangle.Rectangle(startPoint,edge1,edge2,edge3)
			tables.append(table)
			image3 = np.copy(image)
			table.draw(image3)
			showImage(image3,'',0.3)

			tablePoints = removeDirections(table,tablePoints)
			sortedDirections = sortInToDirections(tablePoints)
			printSizeTP(tablePoints,sortedDirections)

			#Points with any directions to search are removed by removeDirections
			#If a point is completly searched, remove it from tablePoints
			if directionsIndex == directionsIndexMax:
					completlySearched = True
					break
			directionsIndex = directionsIndex + 1

			#Controleer als niet alles gezocht is, te starten vanaf de huidige index hor en ver bij de volgende iteratie


			a = 0
			

		
		#showImage(image,'',0.3)



def removeDirections(table,tablePoints):
	for tp in tablePoints:
		if distance(table.p1,tp.point) == 0:
			tp.removeDirection(2)
			tp.removeDirection(3)
			if tp.amount == 0:
				tablePoints.remove(tp)
		elif distance(table.p2,tp.point) == 0:
			tp.removeDirection(3)
			tp.removeDirection(4)
			if tp.amount == 0:
				tablePoints.remove(tp)
		elif distance(table.p3,tp.point) == 0:
			tp.removeDirection(1)
			tp.removeDirection(4)
			if tp.amount == 0:
				tablePoints.remove(tp)
		elif distance(table.p4,tp.point) == 0:
			tp.removeDirection(1)
			tp.removeDirection(2)
			if tp.amount == 0:
				tablePoints.remove(tp)
	return tablePoints

def printSizeTP(tablePoints,sortedtablePoints):
	print len(tablePoints), len(sortedtablePoints[0]), len(sortedtablePoints[1]), len(sortedtablePoints[2]), len(sortedtablePoints[3])


#Start point is not necessairy to find last point
#Assumption: uncessairy points are removed
def findLastPoint(p1,p2,dir1,dir2):
	if dir1 == 1 or dir1 == 3:
		x = p1.point.x
	elif dir1 == 2 or dir1 == 4:
		y = p1.point.y

	if dir2 == 1 or dir4 == 3:
		x = p2.point.x
	elif dir2 == 2 or dir2 == 4:
		y = p2.point.y
		


def searchClosestPoint(tp,sortedDirections,direction,directionContraint):
	wantedDirections = [3,4,1,2]
	dir = sortedDirections[wantedDirections[direction-1]-1]

	distances = np.zeros((len(dir)))
	
	for i in range(0,len(dir)):
		tablep = dir[i]
		distances[i] = tp.distanceToTablePoint(tablep,direction,directionContraint)

	minIndex = np.argmin(distances)
	closest = sortedDirections[wantedDirections[direction-1]-1][minIndex]
	
	return closest






#Zie notes 24/1, 25/1
def removeUnrelevantPoints(tablePoints,border):
	sortedDirections = sortInToDirections(tablePoints)
	temp = []
	for tp in tablePoints:
		
		b = border.pointOnBorder(tp.point)
		if b == 0: # => tp always relevant for table construction
			temp.append(tp)
		else:
			needToContain = [3,4,1,2] #Needs to have this direction otherwise not relevant for construction
			if tp.containsDirection(needToContain[b-1]): #needToContain[b-1]
				temp.append(tp)

	return temp

def sortInToDirections(tablePoints):
	temp = []
	for i in range(0,4):
		temp.append([])
	
	for tp in tablePoints:
		for dir in tp.directions:
			temp[dir-1].append(tp)
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

			


	  