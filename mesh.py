from PIL import Image, ImageDraw
import random
from multiprocessing import Process
from threading import Thread
import cProfile
import pstats
import StringIO
import sys

NUM_NODES_WIDE = 320
NUM_NODES_HIGH = 180
WIDTH = 500
HEIGHT = 500

random.seed()

#########################################################################################
##          Draws a polygon
#########################################################################################
def drawPolygon(poly, colour, drw):
    drw.polygon(poly, (colour[0], colour[1], colour[2]))

#########################################################################################
##          Draws all the nodes
#########################################################################################
def drawNodeList(nodeList, polyColourDict, drw):
    for x in range(0, NUM_NODES_WIDE - 1):
        for y in range(0, NUM_NODES_HIGH - 1):
            drawPolygon([nodeList[x][y], nodeList[x][y + 1], nodeList[x + 1][y + 1]], polyColourDict[tuple(sorted([(x, y), (x, y + 1), (x + 1, y + 1)], key=lambda x: (x[0], x[1])))], drw)
            drawPolygon([nodeList[x][y], nodeList[x + 1][y], nodeList[x + 1][y + 1]], polyColourDict[tuple(sorted([(x, y), (x + 1, y), (x + 1, y + 1)], key=lambda x: (x[0], x[1])))], drw)

#########################################################################################
##          Checks of points p1 and p2 are the same side of line a->b
#########################################################################################
#We can tell if the two points p1 and p2 are on the same side of the line a->b using cross products. (a->b)x(a->p1) should have the same z direction as (a->b)x(a->p2)
def sameSide(a, b, p1, p2):
    ab = [a[0] - b[0], a[1] - b[1]] #get vector a->b
    ap1 = [a[0] - p1[0], a[1] - p1[1]] #get vector a->p1
    ap2 = [a[0] - p2[0], a[1] - p2[1]] #get vector a->p2
    cp1 = ab[0]*ap1[1] - ab[1]*ap1[0] #z direction of ab x ap1
    cp2= ab[0]*ap2[1] - ab[1]*ap2[0] #z direction of ab x ap2

    if cp1 * cp2 > 0: #test that the two numbers have the same sign ie the z is in the same direction
        return True
    else:
        return False

#########################################################################################
##          Checks if a pixels is in a polygon
#########################################################################################
def pixelInPolygon(nodes, pixel):
    if sameSide(nodes[0], nodes[1], nodes[2], pixel) and sameSide(nodes[0], nodes[2], nodes[1], pixel) and sameSide(nodes[2], nodes[1], nodes[0], pixel):
		return True
    return False

#########################################################################################
##          Gets the smallest box that surrounds a polygon
#########################################################################################
def getPolyBox(poly):
    maxX = 0
    maxY = 0
    minX = WIDTH
    minY = HEIGHT

    for node in poly:
        if node[0] > maxX:
            maxX = node[0]
        if node[0] < minX:
            minX = node[0]

        if node[1] > maxY:
            maxY = node[1]
        if node[1] < minY:
            minY = node[1]
    return minX, maxX, minY, maxY
    
#########################################################################################
##          Calculates the colour a polygon should be
#########################################################################################
def calculatePolyColour(nodes, pix): #List of tuples of pixel coordinates, image pixels
    maxX = 0
    maxY = 0
    minX = WIDTH
    minY = HEIGHT
    
    redAverage = 0
    blueAverage = 0
    greenAverage = 0

    pixelList = []
    numPixels = 0
    
    minX, maxX, minY, maxY = getPolyBox(nodes)

    for x in range(minX, maxX):
        for y in range(minY, maxY):
            if pixelInPolygon(nodes, [x, y]):
                pixelList.append([x, y])
                redAverage += pix[x][y][0]
                blueAverage += pix[x][y][1]
                greenAverage += pix[x][y][2]
                numPixels += 1

    if numPixels > 0:
        redAverage /= numPixels
        blueAverage /= numPixels
        greenAverage /= numPixels

    difference = 0
    for pixel in pixelList:
        difference += abs(pix[pixel[0]][pixel[1]][0] - redAverage)
        difference += abs(pix[pixel[0]][pixel[1]][1] - blueAverage)
        difference += abs(pix[pixel[0]][pixel[1]][2] - greenAverage)

    if numPixels > 0:
        difference /= numPixels**0.7

    return (redAverage, blueAverage, greenAverage, int(difference))

#########################################################################################
##          Returns a list of node references connected to provided node
#########################################################################################
def getPolyList(x, y): #In: grid ref, out: list of tuple of grid references
    return [((x, y), (x - 1, y - 1), (x - 1, y)),
            ((x, y), (x, y - 1), (x - 1, y - 1)),
            ((x, y), (x, y - 1), (x + 1, y)),
            ((x, y), (x + 1, y), (x + 1, y + 1)),
            ((x, y), (x + 1, y + 1), (x, y + 1)),
            ((x, y), (x, y + 1), (x - 1, y))]


#########################################################################################
##          Move a node
#########################################################################################
def moveNode(x, y, nodeList, polyColourDict, pix):
    worstDif = 0
    bestDif = 100000
    worstPoly = ()
    worstRealPoly = ()
    polyList = getPolyList(x, y)
    realPolyList = []
    for poly in polyList:
        realPoly = (nodeList[poly[0][0]][poly[0][1]], nodeList[poly[1][0]][poly[1][1]], nodeList[poly[2][0]][poly[2][1]])
        realPolyList.append(realPoly)
        dif = polyColourDict[tuple(sorted(poly, key=lambda x: (x[0], x[1])))][3]
        if dif < bestDif:
            bestDif = dif
        if dif > worstDif:
            worstPoly = poly
            worstRealPoly = realPoly
            worstDif = dif

    scaleFactor = worstDif / max(bestDif, 1)
    scaleFactor = max(min(scaleFactor, 4), 2)
    scaleFactor = 6 - scaleFactor
    if worstDif > 0:
        midpoint = ((worstRealPoly[0][0] + worstRealPoly[1][0] + worstRealPoly[2][0]) / 3, (worstRealPoly[0][1] + worstRealPoly[1][1] + worstRealPoly[2][1]) / 3)
        nodeList[x][y] = ((nodeList[x][y][0] + ((midpoint[0] - nodeList[x][y][0]) / scaleFactor)), (nodeList[x][y][1] + ((midpoint[1] - nodeList[x][y][1]) / scaleFactor)))


    for poly in polyList:
        polyColourDict[tuple(sorted(poly, key=lambda x: (x[0], x[1])))] = calculatePolyColour([nodeList[poly[0][0]][poly[0][1]], nodeList[poly[1][0]][poly[1][1]], nodeList[poly[2][0]][poly[2][1]]], pix)


#########################################################################################
##          Main start
#########################################################################################

targetImagePath = "test.jpg"
if len(sys.argv) > 1:
    targetImagePath = sys.argv[1]

targetImage = Image.open(targetImagePath)
pixels = targetImage.load()
WIDTH = targetImage.size[0]
HEIGHT = targetImage.size[1]

pix = []
for x in range(WIDTH):
    pixRow = []
    for y in range(HEIGHT):
        pixRow.append(pixels[x, y])
    pix.append(pixRow)

nodeList = []
polyColourDict = {}
for x in range(0, NUM_NODES_WIDE):
    nodeRow = []
    for y in range(0, NUM_NODES_HIGH):
        nodeRow.append((int(x * (WIDTH / float(NUM_NODES_WIDE - 1))), int(y * (HEIGHT / float(NUM_NODES_HIGH - 1)))))

    nodeList.append(nodeRow)

for x in range(0, NUM_NODES_WIDE - 1):
    for y in range(0, NUM_NODES_HIGH - 1):
        polyColourDict[tuple(sorted([(x, y), (x, y + 1), (x + 1, y + 1)], key=lambda x: (x[0], x[1])))] = calculatePolyColour([nodeList[x][y], nodeList[x][y + 1], nodeList[x + 1][y + 1]], pix)
        polyColourDict[tuple(sorted([(x, y), (x + 1, y), (x + 1, y + 1)], key=lambda x: (x[0], x[1])))] = calculatePolyColour([nodeList[x][y], nodeList[x + 1][y], nodeList[x + 1][y + 1]], pix)

pr= cProfile.Profile()

count = 0
for i in range(0, 100):
    count = 0
    xList = range(1, NUM_NODES_HIGH - 1)
    random.shuffle(xList)
    yList = range(1, NUM_NODES_WIDE - 1)
    random.shuffle(yList)
    for y in xList:
        count += 1
        f = open("progress.txt", 'w')
        f.write(str(i) + ", " + str(count) + "\n")
        f.close()
        threadList = []
        for x in yList:
            moveNode(x, y, nodeList, polyColourDict, pix)

img = Image.new('RGB', (WIDTH, HEIGHT))
drw = ImageDraw.Draw(img, "RGB")

drawNodeList(nodeList, polyColourDict, drw)

outImagePath = targetImageString.split(".")[0] + "_mesh.png"
img.save(outImagePath)

