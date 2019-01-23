from math import sqrt
import cv2
from numpy.linalg import norm
import numpy as np

class Point:
    def __init__(self,x_init,y_init):
        self.x = x_init
        self.y = y_init

    def pointUnpack(self):
        return self.x,self.y

    def __repr__(self):
        return "".join(["Point(", str(self.x), ",", str(self.y), ")"])

    def pointToArray(self):
        array = np.zeros(2)
        array[0] = self.x
        array[1] = self.y
        return array


    def distanceToLine(self,p1,p2):
        p3 = self.pointToArray()
        p2 = p2.pointToArray()
        p1 = p1.pointToArray()

        #negatieve afstand      np.cross(p2-p1,p3-p1)/norm(p2-p1)
        return norm(np.cross(p2-p1, p1-p3))/norm(p2-p1) #positieve afstand


def distance(a, b):
    return sqrt((a.x-b.x)**2+(a.y-b.y)**2)

def equalX(x,pointList, allowedDeviation):
    temp = []
    for point in pointList:
        if abs(x-point.x) <= allowedDeviation:
            temp.append(point)
    return temp

def equalY(y,pointList,allowedDeviation):
    temp = []
    for point in pointList:
        if abs(y-point.y) <= allowedDeviation:
            temp.append(point)
    return temp

def arrayToPoint(array):
    return Point(array[0],array[1])

# Eventueel mogelijk afwijkingen in rekening brengen 
# Daarom geen x == x1 en y == y1
def pointOccursInList(p,list, allowedDeviation):
    for i in range(0,len(list)):
        point = list[i]
        if distance(p,point) <= allowedDeviation:
            return i
    return -1


def drawLine(point1,point2,image):
    image = cv2.line(image,(int(point1.x),int(point1.y)),(int(point2.x),int(point2.y)),(255,0,0),5)
    return image

def minMaxXY(numpyAr):
    minX = np.min(numpyAr[:,0])
    maxX = np.max(numpyAr[:,0])
    minY = np.min(numpyAr[:,1])
    maxY = np.max(numpyAr[:,1])

    return minX,maxX,minY,maxY


def minimumY(list):
    temp = []
    smallest = 999999
    for point in list:
        if point.y <= smallest:
            smallest = point.y
    return smallest

def maximumY(list):
    temp = []
    largest = 0
    for point in list:
        if point.y >= largest:
           largest = point.y
    return largest

def minimumX(list):
    temp = []
    smallest = 999999
    for point in list:
        if point.x <= smallest:
            smallest = point.x
    return smallest

def maximumX(list):
    largest = 0
    for point in list:
        if point.x >= largest:
           largest = point.x
    return largest

def pointToArrayList(list):
    temp = np.zeros((len(list),2))
    
    for i in range(0,len(list)):
        temp[i, 0] = list[i].x
        temp[i, 1] = list[i].y

    return temp


def boundaries(p1,p2):
    if p1.x >= p2.x:
        maxx = p1.x
        minx = p2.x
    else:
        maxx = p2.x
        minx = p1.x

    if p1.y >= p2.y:
        maxy = p1.y
        miny = p2.y
    else:
        maxy = p2.y
        miny = p1.y

    return minx,maxx, miny, maxy

def averagePoint(list):
    x = 0
    y = 0
    for p in list:
        x += p.x
        y += p.y
    return Point(x/len(list),y/len(list))

def distancePointToLine(p1,p2,x,y):
    d1 = (p2.x-p1.x)*(y - p1.y) - (x-p1.x)*(p2.y - p1.y)
    d1 = abs(d1)/ ((p2.x-p1.x)**2+(p2.y-p1.y)**2)
    return d1