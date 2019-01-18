from Point import *
import random
import math
class Cluster:
    def Cluster(self):
        self

def showImage(image,title,scale):
    cv2.imshow(title,cv2.resize(image,(0,0),fx=scale,fy=scale))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def determineTables(pob1,pob2,keypoints,saveImages, image,path, img_initial):
    img = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2BGR)

    clusters = oneDimCluster(pob1)
    drawClusters(img,clusters)
    clusters = filterClusters(clusters)

    groupBorders(clusters,pob2,keypoints,img,img_initial)

    





    return clusters

def groupBorders(clusters,pob2,keypoints,image,img_initial):
    #Kleine verschillen worden toegelaten (mogelijke breedere kollomen)
    allowedMedianDeviation = 1.5 

    pob2 = pointToArrayList(pob2)
    pob2 = np.sort(pob2,axis = 1)[::-1]
    tablePoints = np.zeros(0)

    verticales = []
    lengthVerticales = None

    tablePoints = []
    
    #Bij verticale borders bevinden de kolommen zo goed als altijd vanonder (=> 1 cluster)
    if len(clusters) == 1:
        clusters = clusters[0]
        verticales.append(clusters)
        minX = np.min(clusters[:,0])
        maxX = np.max(clusters[:,0])
        minY = np.min(clusters[:,1])
        maxY = np.max(clusters[:,1])

        for i in range(0,pob2.shape[0]):
            point = pob2[i,:]
            v,keypoints = pointsInRangeY(keypoints,minY,maxY,point)
            length = len(v)

            if i == 0:
                verticales
                lengthVerticales = np.zeros(1)
                lengthVerticales[0] = length
            else:
                #Plotse daling aantal punten => mogelijk geen kolom
                median = np.median(lengthVerticales)
                length = len(v)
                print median,length

                if median/allowedMedianDeviation >= length or length >= median*allowedMedianDeviation:
                    checkIfSameTable(verticales[i-1],v)

            
            
                verticales.append(v)

            
                lengthVerticales = np.vstack((lengthVerticales,len(v)),img_initial)
            




    print ''
           
def checkIfSameTable(colom1,colom2,img_initial):
    #Zoek vanuit kleinste kolom
    # Ook mogelijk om point te matchen maar dit geeft geen 100% zekerheid
    if len(colom1) <= len(colom2):
        first = colom1[0]
        last = colom1[-1]

        
        avgColom2 = averagePoint(colom1) #defines search bounds

        c1 = img_initial[first.x:]


   

def pointsInRangeY(keypoints,minY,maxY,point):
    pts = []
    allowedInterval = 3

    i = 0
    toDelete = [] #points only can occur once (save search time)
    for p in keypoints:
        
        if abs(p.x - point[0]) <= allowedInterval:
            if p.y >= minY and p.y <= maxY:
                toDelete.append(i)
                pts.append(p)
        i +=1


    for i in reversed(toDelete):
        del keypoints[i]

    return pts,keypoints
        

    


def oneDimCluster(pob1):
    size = len(pob1)-1
    innerDistance = np.zeros(size)    
    pob1 = pointToArrayList(pob1)

    pob1 = np.sort(pob1,axis = 1)
    
    for i in range(0,size):
        innerDistance[i] = pob1[i,1] - pob1[i+1,1]

    median = np.median(innerDistance)

    clusters = []
    tempCluster = pob1[0,:]
    medianTolerance = 2.5
    for i in range(0,size):
        diff = innerDistance[i]
        if diff < medianTolerance*median:
            tempCluster = np.vstack((tempCluster,pob1[i+1,:]))
        else:
            clusters.append(tempCluster)
            tempCluster = pob1[i+1,:]
    clusters.append(tempCluster)
    return clusters

# Momenteel nog simple maar ev intelligent maken
def filterClusters(clusters):
    temp = []
    for c in clusters:
        if np.prod(c.shape) > 2:
            temp.append(c)
    return temp

def drawClusters(image,clusters):
    img = np.copy(image)
    for cluster in clusters:
        color =  list(np.random.choice(range(256), size=3))
        size1 = np.prod(cluster.shape)/2
            
        if size1 == 1:
            cv2.circle(img, (int(cluster[0]),int(cluster[1])), 25, color, 3)
        else:
            cv2.circle(img, (int(cluster[0,0]),int(cluster[0,1])), 25, color, 3)
            for i in range(1,cluster.shape[0]):
                cv2.circle(img, (int(cluster[i,0]),int(cluster[i,1])), 25, color, 3)
        
    showImage(img,'',0.4)

