from Point import *
import Cluster
import cv2
import Rectangle
from TablePoint import *
import random
import glob
import os
from random import randint
import TableTemplate
import Table
import time

saveImages = True
showImages = False
scale = 0.7

class TableConstruct:
	global tollerance
	tollerance = 5
	def __init__(self):
		self

def constructTable(pob1,pob2,pob3,pob4,keypoints,border,image,savePath,cellSavePath ):


	start  = time.clock()

	keypoints = keypoints[:]
	tables = []

	#Remove centering marks on left and right border
	midLeft = Point(border.p1.x,(border.p1.y + border.p2.y) / 2)
	midRight = Point(border.p3.x,(border.p3.y + border.p4.y) / 2)

	pob1 = [p for p in pob1 if distance(p,midLeft) > 0.03 * image.shape[0]]
	pob3 = [p for p in pob3 if distance(p,midRight) > 0.03 * image.shape[0]]
	
	pob1.sort(key = lambda p: p.y,reverse = True)
	pob2.sort(key = lambda p: p.x,reverse = True)
	pob3.sort(key = lambda p: p.y,reverse = True)
	pob4.sort(key = lambda p: p.x,reverse = True)

	pob1 = pointToArrayList(pob1)
	pob2 = pointToArrayList(pob2)
	pob3 = pointToArrayList(pob3)
	pob4 = pointToArrayList(pob4)

	c2 = pob3[-1,:]
	possibleC3 = pointsInInterval(0,c2[0],c2[1],keypoints)

	if possibleC3.size == 0: 
		possibleC3 = pob1[-1,:]
	elif pob1.size > 0:
		possibleC3 = np.vstack((pob1[-1,:],possibleC3))

	possibleC4 = np.vstack((pob2,border.p2.pointToArray()))

	table1 = findTitleBlock(border.p3.pointToArray(),c2,possibleC3, possibleC4,image)
	tables.append(table1)

	print "Title block detection			", "%.3gs" % (time.clock() - start)
	start = time.clock()

	if pob1.size <= 2:
		minHeigth = pob3[-1,1]

	elif pob1[-1,1] < pob3[-1,1]:
		minHeigth = pob1[-1,1]
	else:  
		minHeigth = pob3[-1,1]
		

	pointsAbovePob2 = sortPointsAbovePOB2(pob2,keypoints,border.p2.pointToArray(),pob1,minHeigth)
	pob2 = np.vstack((pob2,border.p2.pointToArray()))

	#Search next point on pob to start searching from
	for index in range(pob2.shape[0]):
		if pob2[index,0] == table1.p2.x:
			break

	tables = findSubTables(pointsAbovePob2,index,tables,image,pob3) 

	img = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)
	for t in tables:
			t.draw(img)
	if saveImages:
		loc = savePath + '12 detected tables.png'
		cv2.imwrite(loc,img)    
	showImage(img,"Detected tables")

	print "Detect substables			", "%.3gs" % (time.clock() - start)
	start = time.clock()

	sortedPoints = addBorderPointsToSortedPoints(tables,keypoints,pob1,pob2,pob3,border)
		
	#Convert points to tablePoints + remove unrelevant points
	tablePoints = []

	for i in range(0,len(sortedPoints)):
		sp = sortedPoints[i]
		temp = []
		for p in sp:
			temp.append(TablePoint(p,image))
		temp = removeUnrelevantPoints(temp,tables[i])
		tablePoints.append(temp)
	
	img = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)	
	for table in tablePoints:
		for tp in table:
			tp.draw(img)

	if saveImages:
		loc = savePath + '13 cell points with direction.png'.format(i)
		cv2.imwrite(loc,img)    
	showImage(img,'Cells points')
		

	formattedTables = []
	for i in range(0,len(tables)):
		formattedTables.append(constructCells(tablePoints[i],tables[i],image))

	
	img = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)
	for i in range(0,len(tables)):
	
			for j in range(0,len(formattedTables[i])):
				formattedTables[i][j].draw(img)
				

	
	#Draw borders and tables
	if saveImages:
		img0  = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)
		for i in range(0,len(tables)):
			loc = cellSavePath + '{}.png'.format(i)
			img1 = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)
			tables[i].draw(img0)
			tables[i].draw(img1)
			cv2.imwrite(loc,img1)    
			for j in range(0,len(formattedTables[i])):
				loc = cellSavePath + '{} {}.png'.format(i,j)
				img2 = np.copy(img1)
				formattedTables[i][j].draw(img0)	
				formattedTables[i][j].draw(img2)	
				cv2.imwrite(loc,img2)
		loc = savePath + "14 Detected tabels and cells.png"
		cv2.imwrite(loc,img0)

	print "Detect cells				", "%.3gs" % (time.clock() - start)

	
	#tableHierachy(tables[i],formattedTables[i],image)

	return formattedTables



#Construct title block based on known points c1 and c2 (leftside) 
#c3 c4: array of possible points
def findTitleBlock(c1,c2,c3,c4,image):
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

	img = np.copy(image)
	
	#Compute canidates c4
	corner4 = []
	if c4.size == 2:
		if lineDetector(c1,c4,image):
			corner4.append(c4)
	else:
		for i in range(0,c4.shape[0]):
			if lineDetector(c1,c4[i,:],image):
				corner4.append(c4[i,:])

	if len(corner4) == 0:
		print("Corner 4 not found")
		exit()

	found = False
	borders = []


	for cor3 in corner3:
		for cor4 in corner4:
			if lineDetector(cor3,cor4,image):
				c3 = cor3
				c4 = cor4
				b = Rectangle.Rectangle((c1),(c2),(c3),(c4))
				borders.append(b)
				found = True
	
	if found:
		b = Rectangle.largestRectangle(borders) 
		
		return b
		
	else:
		print("Corner3 and 4 don't match")
		exit()

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


#31/01
def tableHierachy(tableBorder,tables,image):
	tempTables = [Table.Table(None,tables,False,tableBorder)]
	#tempBorders = [tableBorder]

	while True:
		imageDraw = np.copy(cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB))

		currentTable = tempTables.pop()
		points = relevantPoints(currentTable.table)
		pob1,pob2,pob3,pob4 = pointsOnBorder(currentTable.border,points,imageDraw)
		matchListHor = findMatchesHierachy(pob1,pob3,image)
		matchListVer = findMatchesHierachy(pob2,pob4,image)

		if True:
			tableBorder.draw(imageDraw)
			if not matchListHor is None:
				for m in matchListHor:
					cv2.line(imageDraw,(m[0].x,m[0].y),(m[1].x,m[1].y),(255,0,0),3)
			if not matchListVer is None:
				for m in matchListVer:
					cv2.line(imageDraw,(m[0].x,m[0].y),(m[1].x,m[1].y),(0,255,0),3)
			#showImage(imageDraw,'matches',1)
	
		direction = continueDirection(pob1,pob2,pob3,pob4,matchListHor,matchListVer)

		if direction: #True = horizontal
			matchListHor = sortMatchList(matchListHor,direction)
			groupedTables = groupTables(matchListHor,tables,imageDraw)
			borders = determineBordersFromMatchList(matchListHor)

			formattedTables, unformattedTables = clusterTables(groupedTables,direction,borders)
			tempTables = unformattedTables + tempTables
		else:
			matchListVer = sortMatchList(matchListVer,direction)
			groupedTables = groupTables(matchListVer,tables,imageDraw)
			borders = determineBordersFromMatchList(matchListVer)

			formattedTables, unformattedTables = clusterTables(groupedTables,direction,borders)
			tempTables = unformattedTables + tempTables

		#formattedTables, unformattedTables = clusterTables(groupedTables,direction)
		#formattedTables = clusterTables(groupedTables,direction)

		'''
		ii = -1
		points = relevantPoints(groupedTables[ii])

		pob1,pob2,pob3,pob4 = pointsOnBorder(borders[ii],points,imageDraw)
		matchListHor = findMatchesHierachy(pob1,pob3,image)
		matchListVer = findMatchesHierachy(pob2,pob4,image)

		if True:
			imageDraw = np.copy(cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB))
			tableBorder.draw(imageDraw)
			if not matchListHor is None:
				for m in matchListHor:
					cv2.line(imageDraw,(m[0].x,m[0].y),(m[1].x,m[1].y),(255,0,0),3)
			if not matchListVer is None:
				for m in matchListVer:
					cv2.line(imageDraw,(m[0].x,m[0].y),(m[1].x,m[1].y),(0,255,0),3)
			showImage(imageDraw,'matches',1)
		'''

	

	return 0

def determineBordersFromMatchList(ml):
	borders = []
	for i in range(1,len(ml)):
		borders.append(Rectangle.Rectangle(ml[i - 1][0],ml[i - 1][1],ml[i][0],ml[i][1]))
	return borders

def clusterTables(groupedTables,direction,borders):
	
	#Combine sequent rows/colomns with eachother
	indexStart = 0
	indexStop = 1
	indexMax = len(groupedTables)

	resultingTables = []
	ttPrevious = None
	while True:#Handle formatted table outputed by tableTemplate
		# indexStart,indexStop
	
		tt = TableTemplate.formatTable(groupedTables[indexStart:indexStop + 1],borders[indexStart:indexStop + 1])
		if not tt is None:
			indexStop = indexStop + 1	
		else:
			if indexStop - indexStart >= 2:
				#Handle formatted table outputed by tableTemplate
				resultingTables.append(ttPrevious)
				indexStart = indexStop
				indexStop = indexStart + 1
				
			else: 
				resultingTables.append(tt)
				indexStart = indexStart + 1
				indexStop = indexStop + 1

		if indexStop == indexMax:
			if not tt is None:
				resultingTables.append(tt)
			else:
				b = Rectangle.combine(borders[indexStart],borders[indexStop + 1])
				resultingTables.append(Table.Table(None,groupedTables[indexStart:indexStop + 1],False,b))
			break

		ttPrevious = tt
		#When does do two colomn and rows belong to the same

	for ft in resultingTables:
		ft.setDirection(direction)

	return TableTemplate.seperateFormatedUnformatted(resultingTables)

def groupTables(matchlist,tables,image):
	image = np.copy(image)
	#Construct borders
	borders = []
	sortedTables = []
	for i in range(0,len(matchlist) - 1):
		b = Rectangle.Rectangle(matchlist[i][0],matchlist[i][1],matchlist[i + 1][0],matchlist[i + 1][1])
		borders.append(b)
		sortedTables.append([])
		#b.drawColor(image, (randint(0,255),randint(0,255),randint(0,255)))

	for t in tables:
		for i in range(0,len(borders)):
			if borders[i].contains2(t):
				sortedTables[i].append(t)
				break
	temp = []
	for st in sortedTables:
		 temp.append(sorted(st,key = lambda e: e.p1.x))
	sortedTables = temp

	if True:
		for s in sortedTables:
			color = (randint(0,255),randint(0,255),randint(0,255))
			for t in s:
				t.drawColor(image,color)
		#showImage(image,'groupedTables',1)


	return sortedTables

def sortMatchList(matchlist,direction):
	if direction:
		return sorted(matchlist,key = lambda e: e[0].y)
	else: 
		return sorted(matchlist,key = lambda e: e[0].x)



#To decide to continu in horizontal or vertical direction
#True = continue horizontal; False = vertical
#Add cases during testing !!!!
#Werken met het minste verschil in matchListen sizes (indien links/rechts, b/o
#zelde grootte hebben)
def continueDirection(pob1,pob2,pob3,pob4,matchListHor,matchListVer):
	# 1.  Only 2 matches => continue with the order one
	if len(matchListHor) == 2 and len(matchListVer) > 2:
		return False
	if len(matchListVer) == 2 and len(matchListHor) > 2:
		return True
	return 

def pointsOnBorder(border,points,image):
	pob1 = []
	pob2 = []
	pob3 = []
	pob4 = []

	pob1.append(border.p1)
	pob2.append(border.p2)
	pob3.append(border.p3)
	pob4.append(border.p4)
	pob1.append(border.p2)
	pob2.append(border.p3)
	pob3.append(border.p4)
	pob4.append(border.p1)
	

	for p in points:
		b = border.pointOnBorder(p)
		if b == 1:
			pob1.append(p)
		elif b == 2:
			pob2.append(p)
		elif b == 3:
			pob3.append(p)
		elif b == 4:
			pob4.append(p)


	if False:
		border.draw(image)
		for p in pob1:
			cv2.circle(image, (p.x,p.y), 25, (255,0,0), 3)
		for p in pob2:
			cv2.circle(image, (p.x,p.y), 25, (0,255,0), 3)
		for p in pob3:
			cv2.circle(image, (p.x,p.y), 25, (0,0,255), 3)
		for p in pob4:
			cv2.circle(image, (p.x,p.y), 25, (255,255,0), 3)
		#showImage(image,'',1)
	return pob1,pob2,pob3,pob4

#Points needed to construct the border
def relevantPoints(tables):
	points = []
	for t in tables:
		points.append(t.p1)
		points.append(t.p2)
		points.append(t.p3)
		points.append(t.p4)

	points = set(points)

	return points


#25/01
def constructCells(tablePoints,tableBorder,image):
	img = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2BGR)


	
	tables = []
	
	startIndex = 0
	directionsIndex = 0
	completlySearched = True
	directionsTransform = [3,4,1,2] #Opposite if [1,2,3,4] to determine which direction to search
	tables = []
	done = False
	

	while not done:
		if completlySearched:
			if len(tablePoints) == 0: break;

			startPoint = tablePoints[0]
			tablePoints.remove(startPoint) 
			directions = startPoint.directionCombos2()
			directionsIndex = 0
			directionsIndexMax = len(directions) - 1
			sortedDirections = sortInToDirections(tablePoints)
			completlySearched = False

		while True:				
			dirHor = directions[directionsIndex][0]
			dirVer = directions[directionsIndex][1]


			edges1 = searchValidEdges(startPoint,sortedDirections,dirHor,dirVer) #Search horizontally
			if not edges1 == None and len(edges1) > 1:
				
				img =  cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2BGR)
				startPoint.draw(img)
				cv2.circle(img, (startPoint.point.x,startPoint.point.y), 10, (255,0,0), 4)

				for e in edges1:
					e.draw(img)
				#showImage(img,"edges1",1)
					


			if edges1 is None:
				if directionsIndex == directionsIndexMax:
					completlySearched = True
					break
				directionsIndex = directionsIndex + 1
				continue
							
			edges2 = searchValidEdges(startPoint,sortedDirections,dirVer,dirHor) #Search vertically
			if not edges2 == None and len(edges2) > 1:
				img =  cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2BGR)
				startPoint.draw(img)
				cv2.circle(img, (startPoint.point.x,startPoint.point.y), 10, (255,0,0), 4)

				for e in edges2:
					e.draw(img)
				#showImage(img,"edges2",1)


			if edges2 is None:
				if directionsIndex == directionsIndexMax:
					completlySearched = True
					break
				directionsIndex = directionsIndex + 1
				continue

			stop = False


			for i in range(0,len(edges1)):
				if(stop): break;

				edge1 = edges1[i]

				for j in range(0,len(edges2)):
					edge2 = edges2[j]
					
					edge3 = searchEdge3(edge1,edge2, sortedDirections, dirVer,directionsTransform[dirHor - 1])

					if edge3 is None:
						break		
					table = Rectangle.Rectangle(startPoint,edge1,edge2,edge3)
					tables.append(table)
					img = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2BGR)
					

					if i > 0 or j > 0:
						img = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2BGR)
						startPoint.draw(img)
						cv2.circle(img, (startPoint.point.x,startPoint.point.y), 10, (255,0,0), 4)

						for e in edges2:
							e.draw(img)
						for e in edges1:
							e.draw(img)
						showImage(img,"ff")

					tablePoints = removeDirections(table,tablePoints)
					sortedDirections = sortInToDirections(tablePoints)
						
					stop = True #To break outer loop
					break;

					#Points with any directions to search are removed by removeDirections
					#If a point is completly searched, remove it from tablePoints				
			if directionsIndex == directionsIndexMax:
					completlySearched = True
					break
							
			directionsIndex = directionsIndex + 1

	return tables
					
						
def printTP(tp):
	print ""
	for t in tp:
		print t.point.x,t.point.y
	print ""

def removeDirections(table,tablePoints):
	for tp in tablePoints:
		if distance(table.p1,tp.point) == 0:
			tp.removeDirection(2)
			tp.removeDirection(3)
			if tp.amount == 0:
				tablePoints.remove(tp)
				#print 'remove'
		elif distance(table.p2,tp.point) == 0:
			tp.removeDirection(3)
			tp.removeDirection(4)
			if tp.amount == 0:
				tablePoints.remove(tp)
				#print 'remove'
		elif distance(table.p3,tp.point) == 0:
			tp.removeDirection(1)
			tp.removeDirection(4)
			if tp.amount == 0:
				tablePoints.remove(tp)
				#print 'remove'
		elif distance(table.p4,tp.point) == 0:
			tp.removeDirection(1)
			tp.removeDirection(2)
			if tp.amount == 0:
				tablePoints.remove(tp)
				#print 'remove'
	return tablePoints


def searchEdge3(edge1,edge2,sortedDirections,direction, directionContraint):
	wantedDirections = [3,4,1,2]
	sortedPoints = sortedDirections[wantedDirections[direction - 1] - 1]

	proposal  = Point(edge1.point.x, edge2.point.y)

	for i in range(0,len(sortedPoints)):
		if distance(proposal,sortedPoints[i].point) < 5:
				if edge1.distanceToTablePoint(sortedPoints[i],direction,directionContraint) < 10000: # <10000 => contains wanted directions
					return sortedPoints[i]
				else:
					return None
	return None

	

def searchClosestPoint(tp,sortedDirections,direction,directionContraint):
	wantedDirections = [3,4,1,2]
	dir = sortedDirections[wantedDirections[direction - 1] - 1]

	distances = np.zeros((len(dir)))
	
	for i in range(0,len(dir)):
		tablep = dir[i]
		distances[i] = tp.distanceToTablePoint(tablep,direction,directionContraint)




	minIndex = np.argmin(distances)
	closest = sortedDirections[wantedDirections[direction - 1] - 1][minIndex]
	
	#Prevent returning first tp when all distances are 1OOOO
	if distances[minIndex] == 10000:
		return None

	return closest


#Searches valid edges using the given horizontal and vertical direction
#Multiple edges are returned: usually the closest is needed. 
#Low resolution images and near by text ==> unwanted crossings ==> multiple edges avoid missed detection of a cell


#### 1 geval waar het mis gaat omdat alles toevallig uitlijnt (slechte crossing omw lage resolutie) 
def searchValidEdges(tp,sortedDirections,direction,directionContraint):
	wantedDirections = [3,4,1,2]
	dir = sortedDirections[wantedDirections[direction - 1] - 1]

	distances = []
	
	for i in range(0,len(dir)):
		tablep = dir[i]

		dis = tp.distanceToTablePoint(tablep,direction,directionContraint)
		if dis < 10000:
			temp = [tablep,dis]

			distances.append(temp)

	if len(distances) == 0:
		return None


	distances.sort(key = lambda x: x[1])
	closest = zip(*distances)[0]

	'''
	closest = []
	for i in possibleIndexes:
		closest.append(dir[i])
	'''
	return closest

def printTables(tables):
	i = 1
	for p in tables:
		print i, p.p1, p.p2, p.p3, p.p4
		i = i + 1

#Zie notes 24/1, 25/1
#Verwijderd punten die sterk afwijken omdat deze mogelijk geen directions heeft
# 2 Mogelijkheden:
# 1.  Repair: punten die sterk afwijken bv als deze als enigste waarde afwijkt
# in een kolom/rij => pas waarden aan
# 2.  Exploit kolom info
def removeUnrelevantPoints(tablePoints,border):
	sortedDirections = sortInToDirections(tablePoints)
	temp = []
	for tp in tablePoints:
		a = False
		if border.pointBelongsToBorder(tp.point):
			temp.append(tp)
			a = True
		elif tp.validCorner():
			b = border.pointOnBorder(tp.point)
			if b == 0: # => tp always relevant for table construction
				temp.append(tp)
				a = True
			else:
				needToContain = [3,4,1,2] #Needs to have this direction otherwise not relevant for construction
				if tp.containsDirection(needToContain[b - 1]): #needToContain[b-1]
					temp.append(tp)
					a = True
		if a == False:
			gg = 0

	return temp

def sortInToDirections(tablePoints):
	temp = []
	for i in range(0,4):
		temp.append([])
	
	for tp in tablePoints:
		for dir in tp.directions:
			temp[dir - 1].append(tp)
	return temp

def addBorderPointsToSortedPoints(tables,keypoints,pob1,pob2,pob3,border):
	sorted = []

	for t in tables:
		sorted.append([])

	for kp in keypoints:
		for i in range(0,len(tables)):
			if tables[i].containsPoint(kp,2):
				sorted[i].append(kp)

	for i in range(0,pob1.shape[0]):
		for j in range(0,len(tables)):
			if tables[j].containsPoint(pob1[i,:],2):
				sorted[j].append(arrayToPoint(pob1[i,:]))

	for i in range(0,pob2.shape[0]):
		for j in range(0,len(tables)):
			if tables[j].containsPoint(pob2[i,:],2):
				sorted[j].append(arrayToPoint(pob2[i,:]))

	for i in range(0,pob3.shape[0]):
		for j in range(0,len(tables)):
			if tables[j].containsPoint(pob3[i,:],2):
				sorted[j].append(arrayToPoint(pob3[i,:]))


	if tables[0].containsPoint(border.p3,2):
		sorted[0].append(border.p3)

	if tables[-1].containsPoint(border.p2,2):
		sorted[-1].append(border.p2)


	return sorted

def findSubTables(pointsAbovePob2,index,tables,image,pob3):
	if index == len(pointsAbovePob2) - 1:
		return tables

	while True:
		matchList = findMatches(pointsAbovePob2[index],pointsAbovePob2[index + 1],image)

		adjacent = True #True if 2 different tables are adjacent
		if matchList.size == 2: #only 1 match
			adjacent = False
			index = index + 1

		lastColomnIndex = searchEnd(index,pointsAbovePob2,pob3,image)

		if lastColomnIndex == -1 or lastColomnIndex == index:
			return tables

		lastColomn = pointsAbovePob2[lastColomnIndex]
		c1 = pointsAbovePob2[index][0]

		newSubTable = constructSubtable(c1,pointsAbovePob2[index],lastColomn,image)
		tables.append(newSubTable)

		#corner2 = findMissingPoint(lastColomn[-1,:],pointsAbovePob2[index],image)

		#tableTemp =
		#Rectangle.Rectangle(pointsAbovePob2[index][0,:],corner2,lastColomn[-1,:],lastColomn[0,:])


		image = newSubTable.draw(np.copy(image))
		#showImage(image,'',0.3)

		index = lastColomnIndex
		if index == len(pointsAbovePob2) - 1:
			break
	#except:
		#doNoting = True
	return tables

def constructSubtable(c1,colomn1, colomn2,image):
	colomn1 = checkLineConnectivity(colomn1,image)
	colomn2 = checkLineConnectivity(colomn2,image)
	c2,c3 = findTopMatchColomn(colomn1, colomn2, image)
	c4 = colomn2[0,:]
	return Rectangle.Rectangle(c1,c2,c3,c4)

def checkLineConnectivity(points,image):
	a  = 0
	for i in range(points.shape[0]-1):
		p1 = points[i,:]
		p2 = points[i+1,:]
		if not lineDetector(p1,p2,image):
			return points[0:i+1]
	return points

def findTopMatchColomn(colomn1, colomn2,image):
	#List are ordered to optimize search
	#Points of subtable are both in top of colomn1 and 2
	for i in range(colomn1.shape[0] - 1,-1,-1):
		for j in range(colomn2.shape[0] - 1,-1,-1):
			if abs(colomn1[i,1] - colomn2[j,1]) <= 5:
				if lineDetector(colomn1[i,:],colomn2[j,:],image):
					p1 = colomn1[i,:]
					p2 = colomn2[j,:]
					return p1,p2

def searchEnd(start,pointsAbovePob2,pob3,image):
	stop = False
	while not stop:
		if findMatches(pointsAbovePob2[start],pointsAbovePob2[start + 1],image).size > 2:
			if abs(pointsAbovePob2[start][0,1] - pointsAbovePob2[start + 1][0,1]) > 5:
				#Large difference in length ==> new colomn
				return start
			if start == len(pointsAbovePob2) - 2:
				return start + 1
			start = start + 1
		else:
			return start ##### start
		
	
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

def findMatchesHierachy(list1,list2,image):
	matchList = []

	for p1 in list1:
		for p2 in list2:
			if lineDetector(p1,p2,image):
				matchList.append([p1,p2])
				
	return matchList


#pob2 included
def sortPointsAbovePOB2(pob2,points,p2,pob1,yMin):
	above = []

	for i in range(0,pob2.shape[0]):
		temp = []
		for p in points:
			if abs(p.x - pob2[i,0]) <= 4: ######
				if(p.y >= yMin):
					temp.append(p)

		temp = pointToArrayList(temp)
		temp = np.vstack((temp,pob2[i,:]))
		temp = np.sort(temp,axis = 0)[::-1]
		above.append(temp)

	temp = np.vstack((p2,pob1))
	temp = np.sort(temp,axis = 0)[::-1]

	above.append(temp)

	#
	for i in range(len(above) - 1,0,-1):
		if above[i].size <= 4:
			above.pop(i)
		else:
			break



	return above


#Gray images!!
def lineDetector1(p1,p2,image):
	if isinstance(p1,Point):
		p1 = p1.pointToArray()
		p2 = p2.pointToArray()

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
   
	if segment.shape[0] > segment.shape[1]:
		line = np.max(segment,axis=1)
	else:
		line = np.max(segment,axis=0)
	###########


	

	filled = np.count_nonzero(line) / line.shape[0]
	
	if filled >= 0.80: ###
		return True
   
	return False


			
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

def showImage(image,title):
	if showImages:
		cv2.imshow(title,cv2.resize(image,(0,0),fx=scale,fy=scale))
		cv2.waitKey(0)
		cv2.destroyAllWindows()			

			

