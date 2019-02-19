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


saveImage = True
savePathBorder = ''
class TableConstruct:
	global tollerance
	tollerance = 5
	#Eventueel alle keypoints filteren
	def __init__(self):
		self

def constructTable(pob1,pob2,pob3,pob4,keypoints,border,image,number):
	savePathBorder = 'C:\\Users\\MarijnFerrari\\Documents\\Thesis\\Extraction\\Extraction\\save\\{}\\border\\'.format(number)
	savePath = 'C:\\Users\\MarijnFerrari\\Documents\\Thesis\\Extraction\\Extraction\\save\\{}\\'.format(number)
	keypoints = keypoints[:]
	tables = []
	#Seperate distant points that don't belong to any table
	pob1 = Cluster.clusterBorders(pob1) 
	pob3 = Cluster.clusterBorders(pob3)

	'''
	image1 = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)
	for tp in keypoints:
		cv2.circle(image1, (tp.x,tp.y), 5, (255,0,0), 1)
	showImage(image1,'1',5)
	'''

	c2 = pob3[-1,:]
	possibleC3 = pointsInInterval(0,c2[0],c2[1],keypoints)

	try:
		possibleC3 = np.vstack((pob1[-1,:],possibleC3))
		possibleC4 = np.vstack((border.p2.pointToArray(),pob2))
	except:
		possibleC4 = pob2


	table1, c11,c12,c13,c14 = findCorners(border.p3.pointToArray(),c2,possibleC3, possibleC4,image)
	tables.append(table1)

	if pob1.size <= 2:
		minHeigth = pob3[-1,1]

	elif pob1[-1,1] < pob3[-1,1]:
		minHeigth = pob1[-1,1]
	else:  
		minHeigth = pob3[-1,1]
		
	pointsAbovePob2 = sortPointsAbovePOB2(pob2,keypoints,border.p2.pointToArray(),pob1,minHeigth)
	'''
	image1 = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)
	for a in pointsAbovePob2:
		for p in a:
			cv2.circle(image1, (int(p[0]),int(p[1])), 5, (255,0,0), 1)
	showImage(image1,'2',1)
	'''

	#Search next point on pob to start searching from

	index,_ = np.where(pob2 == c13)
	if not index.size == 0: # if 0 => 1 table spans the entire border
		index = index[0]

		tables = findTables(pointsAbovePob2,index,tables,image,pob3) 
	
	img =  cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)

	for i in range(0,len(tables)):
			#loc = savePathBorder + '{}.png'.format(i)
			tables[i].draw(img)

	showImage(img,'tables',0.3)



	
	sortedPoints = sortPointsTables(tables,keypoints,pob1,pob2,pob3,border)
	
	'''
	image1 = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)
	for p in sortedPoints[0]:
		cv2.circle(image1, (p.x,p.y), 5, (255,0,0), 1)
	showImage(image1,'3',1)
	'''

	#Convert points to tablePoints + remove unrelevant points
	tablePoints = []

	for i in range(0,len(sortedPoints)):
		sp = sortedPoints[i]
		temp = []
		for p in sp:
			temp.append(TablePoint(p,image))
		temp = removeUnrelevantPoints(temp,tables[i])
		tablePoints.append(temp)
	
	'''
	image1 = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2RGB)
	for p in tablePoints[0]:
		cv2.circle(image1, (p.point.x,p.point.y), 5, (255,0,0), 1)
	showImage(image1,'4',1)
	'''

	formattedTables = []
	for i in range(0,len(tables)):
		formattedTables.append(constructTables(tablePoints[i],tables[i],image))

	
	img =  cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)
	for i in range(0,len(tables)):
	
			for j in range(0,len(formattedTables[i])):
				formattedTables[i][j].draw(img)
				
	showImage(img,'aaaa',1)

	
	#Draw borders and tables
	if saveImage:
		files = glob.glob(savePathBorder + '*')
		for f in files:
			os.remove(f)

		for i in range(0,len(tables)):
			loc = savePathBorder + '{}.png'.format(i)
			img =  cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)
			tables[i].draw(img)
			
			cv2.imwrite(loc,img)    

			for j in range(0,len(formattedTables[i])):
				loc = savePathBorder + '{} {}.png'.format(i,j)
				img2 = np.copy(img)

				formattedTables[i][j].draw(img2)
				
				cv2.imwrite(loc,img2)
	
	#i = 0
	#tableHierachy(tables[i],formattedTables[i],image)
	


	return formattedTables

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
			showImage(imageDraw,'matches',1)
	
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
		borders.append(Rectangle.Rectangle(ml[i-1][0],ml[i-1][1],ml[i][0],ml[i][1]))
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
	
		tt = TableTemplate.formatTable(groupedTables[indexStart:indexStop+1],borders[indexStart:indexStop+1])
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
				b = Rectangle.combine(borders[indexStart],borders[indexStop+1])
				resultingTables.append(Table.Table(None,groupedTables[indexStart:indexStop+1],False,b))
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
	for i in range(0,len(matchlist)-1):
		b = Rectangle.Rectangle(matchlist[i][0],matchlist[i][1],matchlist[i+1][0],matchlist[i+1][1])
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
		showImage(image,'groupedTables',1)


	return sortedTables

def sortMatchList(matchlist,direction):
	if direction:
		return sorted(matchlist,key = lambda e: e[0].y)
	else: 
		return sorted(matchlist,key = lambda e: e[0].x)



#To decide to continu in horizontal or vertical direction
#True = continue horizontal; False = vertical
#Add cases during testing !!!!
#Werken met het minste verschil in matchListen sizes (indien links/rechts, b/o zelde grootte hebben)
def continueDirection(pob1,pob2,pob3,pob4,matchListHor,matchListVer):
	# 1. Only 2 matches => continue with the order one
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
		showImage(image,'',1)
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

def test(tablePoints):
	for tp in tablePoints:
		if tp.point.x == 18:
			if tp.point.y == 1065:
				return True
	return False
#25/01
def constructTables(tablePoints,tableBorder,image):
	img = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2BGR)


	for tp in tablePoints:
		tp.draw(img)
	showImage(img,'tps',1)

	tables = []
	img = np.copy(image)
	
	startIndex = 0
	directionsIndex = 0
	completlySearched = True
	directionsTransform = [3,4,1,2]     
	tables = []
	done = False
	aa = False
	
	try:
		while not done:
			if completlySearched:
				startPoint = tablePoints[0]
	
				tablePoints.remove(startPoint) 
				directions = startPoint.directionCombos2()
				directionsIndex = 0
				directionsIndexMax = len(directions) - 1
				sortedDirections = sortInToDirections(tablePoints)
				completlySearched  = False
			

			while True:
				if test(tablePoints)==False:
					a = 0
				if len(tables) == 9:
						a = 0
				image1 = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)
				dirHor = directions[directionsIndex][0]
				dirVer = directions[directionsIndex][1]

				cv2.circle(image1, (startPoint.point.x,startPoint.point.y), 3, (255,0,0), 3)
				edges1 = searchClosestPointsss(startPoint,sortedDirections,dirHor,dirVer)
				
				if edges1 is None:
					if directionsIndex == directionsIndexMax:
						completlySearched = True
						break
					directionsIndex = directionsIndex + 1
					continue
					
								
				edges2 = searchClosestPointsss(startPoint,sortedDirections,dirVer,dirHor)   

				if edges2 is None:
					if directionsIndex == directionsIndexMax:
						completlySearched = True
						break
					directionsIndex = directionsIndex + 1
					continue

				aa = False
				for ii in range(0,len(edges1)):
					if (aa): 
						break
					edge1 = edges1[ii]
					if not edge1.containsDirection(dirVer):
						if directionsIndex == directionsIndexMax:
							completlySearched = True
							break

						directionsIndex = directionsIndex + 1
						#showImage(image1,'hor',0.3)
						continue

					for jj in range(0,len(edges2)):
						if (aa):
							break
						edge2 = edges2[jj]
						if not edge2.containsDirection(dirHor):
							if directionsIndex == directionsIndexMax:
								completlySearched = True
								break

							directionsIndex = directionsIndex + 1
							#showImage(image1,'ver',0.3)
							continue
						image1 = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)
						cv2.circle(image1, (startPoint.point.x,startPoint.point.y), 3, (0,255,255), 4)
						cv2.circle(image1, (edge1.point.x,edge1.point.y), 3, (255,0,0), 4)
						cv2.circle(image1, (edge2.point.x,edge2.point.y), 3, (0,255,0), 4)

						try:
							edge3 = searchClosestPoint(edge1,sortedDirections,dirVer,directionsTransform[dirHor-1])
						
							table = Rectangle.Rectangle(startPoint,edge1,edge2,edge3)
							cv2.circle(image1, (edge3.point.x,edge3.point.y), 3, (0,0,255), 4)
							#showImage(image1,'3',1)
							tables.append(table)

							image1 = cv2.cvtColor(np.copy(image),cv2.COLOR_GRAY2RGB)
							table.draw(image1)
							#showImage(image1,'fff',1)
			
							tablePoints = removeDirections(table,tablePoints)
							sortedDirections = sortInToDirections(tablePoints)
						
							aa = True
						except:
							a = 0
		

					

					


						#Points with any directions to search are removed by removeDirections
						#If a point is completly searched, remove it from tablePoints

					
				if directionsIndex == directionsIndexMax:
						completlySearched = True
						break
							
				directionsIndex = directionsIndex + 1
	except:
		return tables
	return tables
					
						
	

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

def searchClosestPoint(tp,sortedDirections,direction,directionContraint):
	wantedDirections = [3,4,1,2]
	dir = sortedDirections[wantedDirections[direction-1]-1]

	distances = np.zeros((len(dir)))
	
	for i in range(0,len(dir)):
		tablep = dir[i]
		distances[i] = tp.distanceToTablePoint(tablep,direction,directionContraint)




	minIndex = np.argmin(distances)
	closest = sortedDirections[wantedDirections[direction-1]-1][minIndex]
	
	#Prevent returning first tp when all distances are 1OOOO
	if distances[minIndex] == 10000:
		return None

	return closest

def searchClosestPointsss(tp,sortedDirections,direction,directionContraint):
	wantedDirections = [3,4,1,2]
	dir = sortedDirections[wantedDirections[direction-1]-1]

	distances = []#np.zeros((len(dir)))
	
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
# 1. Repair: punten die sterk afwijken bv als deze als enigste waarde afwijkt in een kolom/rij => pas waarden aan
# 2. Exploit kolom info 
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
				if tp.containsDirection(needToContain[b-1]): #needToContain[b-1]
					temp.append(tp)
					a = True
		if a == False:
			gg  =0

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

def findTables(pointsAbovePob2,index,tables,image,pob3):
	if index == len(pointsAbovePob2)-1:
		return tables

	try:
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
	except:
		doNoting = True
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
			if abs(p.x - pob2[i,0]) <= 2:
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
	for i in range(len(above)-1,0,-1):
		if above[i].size <= 4:
			above.pop(i)
		else:
			break



	return above

def findCorners(c1,c2,c3,c4,image):
	#c1 and c2 are always specified as np array
	#c3 and c4 are np arrays of points

	
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
	'''
	for a in corner3:
		cv2.circle(img, (int(a[0]),int(a[1])), 5, (255,0,0), 1)
	
	for a in corner4:
		cv2.circle(img, (int(a[0]),int(a[1])), 5, (255,0,0), 1)
	showImage(img,'',1)
	'''

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
	'''
	for b in borders:
		img = np.copy(image)
		b.draw(img)
		showImage(img,'',1)
	'''


	if found:
		b = Rectangle.largerstBorder(borders)
		
		return b,c1,c2,c3,c4
		
	else:
		print("Corner3 and 4 don't match")
		exit()

#Gray images!!
def lineDetector(p1,p2,image):
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
	fx = 1000/float(image.shape[0])

	cv2.imshow(title,cv2.resize(image,(0,0),fx=fx,fy=fx))
	cv2.waitKey(0)
	cv2.destroyAllWindows()			

			


	  