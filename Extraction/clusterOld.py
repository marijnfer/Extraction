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


def oneDimCluster(pob,saveImages, image,path):
    image = cv2.cvtColor(np.copy(image), cv2.COLOR_GRAY2BGR)

    innerDistance = np.zeros(len(pob)-1)    
    pob = pointToArrayList(pob)

    pob = np.sort(pob,axis = 1)#Sort voor snelle cluster convergentie (1)
    
    for i in range(0,len(pob)-1):
        innerDistance[i] = pob[i,1] - pob[i+1,1]

    median = np.median(innerdistance)


    
    
    clusterSize = 3
    clusters = []
    colors = [(255,0,0),(0,255,0),(0,0,255)]
    #for i in range(0,clusterSize):
     #   colors.append(list(np.random.choice(range(256), size=3)))


    # sort clusters(2)
    # Combinatie van 1 en 2 => punten worden sneller aan de juist cluster toegewezen
    # Ev geen random punten voor init clusters
    randoms = []
    temp = []
    size = np.prod(pob.shape)/2
    '''
    2 volgende fors: geen dubbele punten voor clusters 
    en mogelijkheid tot sorteren voor snellere convergentie
    '''
    for i in range(0,size): 
        temp.append(i)

    for i in range(clusterSize):
        r = random.randint(0,len(temp)-1)
        randoms.append(temp[r])
        del temp[r]

    randoms = sorted(randoms,reverse = True) # (1)
    for r in randoms:
        clusters.append(pob[r,:])

    iteration = 1
    while True:
        print len(pob)
        for i in range(0,size):
            cl = clostestToCluster(clusters,pob[i,:])
            if cl !=-1:
                clusters[cl] = np.vstack((clusters[cl],pob[i,:]))
            
        
        img = np.copy(image)
        j = 0
        ii =0
        print ''
        for cluster in clusters:
            print cluster
            

            size1 = np.prod(cluster.shape)/2
            
            if size1 == 1:
                cv2.circle(img, (int(cluster[0]),int(cluster[1])), 25, colors[j], 7)
                ii+=1
            else:
                cv2.circle(img, (int(cluster[0,0]),int(cluster[0,1])), 25, colors[j], 7)
                ii+=1
                for i in range(1,cluster.shape[0]):
                     cv2.circle(img, (int(cluster[i,0]),int(cluster[i,1])), 25, colors[j], 3)
                     ii+=1
            j += 1    
        print ii,ii
        
        title = '{:d}'.format(iteration)
        showImage(img,title,0.4)
        

        
        clusters = prepareClusters(clusters)  
        

    print ''

def drawClusters(clusters,saveImage,path):
    todo = True

# Bepaald de nieuwe middelpunten van de clusters 
def prepareClusters(clusters):
    newClusters = []
    for c in clusters:
        size = np.prod(c.shape)/2
        if size == 1:
            newClusters.append(c)
        else:
            newClusters.append(closestToCentre(c))
    return newClusters
            
def closestToCentre(points):
    expFactor = 1
    mu = 0.5
    sigma = 1
    
    centre = np.sum(points,axis = 0)/points.shape[0]
    distance = np.zeros(points.shape[0])
    distanceOr = np.zeros(points.shape[0])
    print ''
    print ''
    print ''
    print ''

    for i in range(0,points.shape[0]):
        d = ((points[i,0]-centre[0])**2 + (points[i,1]-centre[1])**2)**0.5/1000
        r = 5 + random.gammavariate(mu,sigma) 
        distance[i] =r*d
        distanceOr[i] = d

    print points
    
    #if distance.shape[0] == 2
    index = np.argmin(distance)
    '''print centre
    print distanceOr
    print points[index,:]'''
    return points[index,:]

def clostestToCluster1(clusters,point):
    mins = np.zeros(len(clusters))
    for j in range(0,len(clusters)):
        c = clusters[j]
        size = np.prod(c.shape)/2
        min = np.zeros(size)
        if size == 1: # Determine minimum distance to points in cluster
            if np.array_equal(c,point):
                return -1 #min[0] = 99999999999999999
            else:
                min[0] = (c[0]-point[0])**2 + (c[1]-point[1])**2
        else: # Determine minimum distance to points in cluster
            for i in range(0,size): 
                p = c[i,:]
                # Prevents doubles (first element aren't deleted from pob)
                if np.array_equal(p,point):  
                    return -1#min[i] = 99999999999999999
                else:
                    min[i] = (p[0]-point[0])**2 + (p[1]-point[1])**2
        mins[j] = (np.min(min))
    
    return np.argmin(mins)

def clostestToCluster(clusters,point):
    mins = np.zeros(len(clusters))
    for j in range(0,len(clusters)):
        c = clusters[j]
        size = np.prod(c.shape)/2
        min = np.zeros(size)
        if size == 1: # Determine minimum distance to points in cluster
            
            mins[j] = (c[0]-point[0])**2 + (c[1]-point[1])**2
            print mins[j] 
        else: # Determine minimum distance to points in cluster
        
            centre = c[0,:]#np.sum(c,axis = 0)/c.shape[0]
            mins[j] = (centre[0]-point[0])**2 + (centre[1]-point[1])**2
            print centre
         
    print  np.argmin(mins)                  
    return np.argmin(mins)

