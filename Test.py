import cv2
import numpy as np
import os
import glob 
import math
from Rectangle import *
from Point import *
import shutil
import Cluster
import time

saveImages = False
savePath = 'C:\\Users\\MarijnFerrari\\Documents\\Thesis\\Extraction\\Extraction\\save\\'
mainPath = 'C:\\Users\\MarijnFerrari\\Documents\\Thesis\\Drawings\\2.png'



def application(path):
	start = time.clock()
	'''
	if saveImages:
		for root, dirs, files in os.walk(savePath):
			for f in files:
				os.unlink(os.path.join(root, f))
		
	img_initial = prepare(path)
	print "%.2gs" % (time.clock() - start)
	img_crosspoints = crosspointDetection(img_initial)
	print "%.2gs" % (time.clock() - start)
	keypoints = blobDetection(img_crosspoints)
	print "%.2gs" % (time.clock() - start)
	cornerpoints = getCornerPoints(img_crosspoints,keypoints)
	print "%.2gs" % (time.clock() - start)
	border = determineBoundingBox(img_crosspoints,cornerpoints)
	print "%.2gs" % (time.clock() - start)
	pob1,pob2,pob3,pob4 = keypointsOnBorder(keypoints, border,2,img_crosspoints)
	print "%.2gs" % (time.clock() - start)
	keypoints = deleteBorderFromKeypoints(border,keypoints,pob1,pob2,pob3,pob4,img_crosspoints)
	print "%.2gs" % (time.clock() - start)

	pob1 = pointToArrayList(pob1)
	pob2 = pointToArrayList(pob2)
	pob3 = pointToArrayList(pob3)
	pob4 = pointToArrayList(pob4)

	TableConstruct.constructTable(pob1,pob2,pob3,pob4,keypoints,border,img_initial)
	

	print "%.2gs" % (time.clock() - start)
	#border1 = determineBoundingBox1(img_crosspoints,keypoints)
	'''

	print("done")
	

application(mainPath)

