from Point import *
import random
import math

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

class Cluster:
	def Cluster(self):
		self
	  
#Eenvoudiger om eps density clustering te setten
def prepareBorder(pob):
	pob = np.copy(pob)
	range = 100 
	minX,maxX,minY,maxY = minMaxXY(pob)
	rangeX = maxX-minX
	rangeY = maxY-minY

	if rangeX > rangeY: #eig niet nodig want wordt enkel maar gebruikt voor pob1 en pob3
		pob[:,0] = range * (pob[:,0]-minX)/rangeX
		#herschaal van 0 tot 1 zodat neigborhood functie in DBSCAN voornamelijk 
		#afhangt van de dominate richting
		pob[:,1] = (pob[:,1]-minY)/( rangeY + 1)
	else:
		pob[:,1] = range * (pob[:,1]-minY)/rangeY
		pob[:,0] = (pob[:,0]-minX)/(rangeX + 1)


	return pob

def clusterBorders(pob):


	if pob.shape[0] <= 1:
		return pob

	pob1 = prepareBorder(pob)


	ranges = 100
	#Meestal is er maar een punt dat moet afgescheden worden
	#afstand tot dichtsbijzijnde punt gaat op deze manier groter zijn dan eps
	#1.2 => om een bepaalde marge te hebben (nog steeds nodig ook met een verafwijkend punt)
	eps = 1.4*ranges/(float(pob1.shape[0])-1) 

	db = DBSCAN(eps=eps, min_samples=2).fit(pob1)
	labels = db.labels_  # 0 of -1
	print labels
	if not -1 in labels:
		return pob

	index = labels.shape[0]-1
	previous = labels[-1]
	if not previous == -1:
		return pob

	while True:
		current = labels[index]

		if not current == -1:
			return pob[0:index+1]
		else:
			index = index - 1
	
	#return pob
	'''
	iStart = -1  #Eerste 0 
	iStop = -1  #Laatste 0
	for i in range(0,labels.shape[0]):
		if iStart == -1 and labels[i] == 0:
			iStart = i
		if iStart > -1 and labels[i] == -1:
			iStop = i
			break

	a = pob[iStart:iStop,:]
	return pob[iStart:iStop,:]
	'''