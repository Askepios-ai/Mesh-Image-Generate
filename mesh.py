from PIL import Image, ImageDraw
import random

NUM_NODES_WIDE = 64
NUM_NODES_HIGH = 36
WIDTH = 500
HEIGHT = 500

random.seed()

def drawPolygon(poly, colour, drw):
    drw.polygon(poly, colour)

def drawNodeList(nodeList, polyColourDict, drw):
    for x in range(0, NUM_NODES_WIDE - 1):
        for y in range(0, NUM_NODES_HIGH - 1):
            drawPolygon([nodeList[x][y], nodeList[x][y + 1], nodeList[x + 1][y + 1]], polyColourDict[tuple(sorted([(x, y), (x, y + 1), (x + 1, y + 1)], key=lambda x: (x[0], x[1])))], drw)
            drawPolygon([nodeList[x][y], nodeList[x + 1][y], nodeList[x + 1][y + 1]], polyColourDict[tuple(sorted([(x, y), (x + 1, y), (x + 1, y + 1)], key=lambda x: (x[0], x[1])))], drw)

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

def pixelInPolygon(nodes, pixel):
    if sameSide(nodes[0], nodes[1], nodes[2], pixel) and sameSide(nodes[0], nodes[2], nodes[1], pixel) and sameSide(nodes[2], nodes[1], nodes[0], pixel):
        return True
    else:
        return False

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
    
def calculatePolyColour(nodes, pix): #List of tuples of pixel coordinates, image pixels
    maxX = 0
    maxY = 0
    minX = WIDTH
    minY = HEIGHT
    
    redAverage = 0
    blueAverage = 0
    greenAverage = 0

    numPixels = 0
    
    minX, maxX, minY, maxY = getPolyBox(nodes)

    for x in range(minX, maxX):
        for y in range(minY, maxY):
            if pixelInPolygon(nodes, [x, y]):
                redAverage += pix[x, y][0]
                blueAverage += pix[x, y][1]
                greenAverage += pix[x, y][2]
                numPixels += 1
                
    if numPixels > 0:
        redAverage /= numPixels
        blueAverage /= numPixels
        greenAverage /= numPixels

    return (redAverage, blueAverage, greenAverage)

def getPolyList(x, y): #In: grid ref, out: list of tuple of grid references
    return [((x, y), (x - 1, y - 1), (x - 1, y)),
            ((x, y), (x, y - 1), (x - 1, y - 1)),
            ((x, y), (x, y - 1), (x + 1, y)),
            ((x, y), (x + 1, y), (x + 1, y + 1)),
            ((x, y), (x + 1, y + 1), (x, y + 1)),
            ((x, y), (x, y + 1), (x - 1, y))]

def getPolyColourDif(poly, realPoly, polyColourDict, pix): #In: List of tuple of grid ref, colour dictionary, image pixels
    minX, maxX, minY, maxY = getPolyBox(realPoly)
    difference = 0
    numPixels = 0

    for x in range(minX, maxX):
        for y in range(minY, maxY):
            if pixelInPolygon(realPoly, [x, y]):
                numPixels += 1
                difference += abs(pix[x, y][0] - polyColourDict[tuple(sorted(poly, key=lambda x: (x[0], x[1])))][0])
                difference += abs(pix[x, y][1] - polyColourDict[tuple(sorted(poly, key=lambda x: (x[0], x[1])))][1])
                difference += abs(pix[x, y][2] - polyColourDict[tuple(sorted(poly, key=lambda x: (x[0], x[1])))][2])


##    if numPixels > 0:
##        difference /= float(3*numPixels)

    return difference

def moveNode(x, y, nodeList, polyColourDict, pix):
    worstDif = 0
    worstPoly = ()
    worstRealPoly = ()
    polyList = getPolyList(x, y)
    realPolyList = []
    for poly in polyList:
        realPoly = (nodeList[poly[0][0]][poly[0][1]], nodeList[poly[1][0]][poly[1][1]], nodeList[poly[2][0]][poly[2][1]])
        dif = getPolyColourDif(poly, realPoly, polyColourDict, pix)
        if dif > worstDif:
            worstPoly = poly
            worstRealPoly = realPoly
            worstDif = dif

    nodeList[x][y] = ((worstRealPoly[0][0] + worstRealPoly[1][0] + worstRealPoly[2][0]) / 3, (worstRealPoly[0][1] + worstRealPoly[1][1] + worstRealPoly[2][1]) / 3)

    for poly in realPolyList:
        polyColourDict[tuple(sorted(poly, key=lambda x: (x[0], x[1])))] = calculatePolyColour(poly, pix)
    

#########################################################################################
##          Main start
#########################################################################################

targetImage = Image.open("test.png")
pix = targetImage.load()
WIDTH = targetImage.size[0]
HEIGHT = targetImage.size[1]

nodeList = []
polyColourDict = {}
for x in range(0, NUM_NODES_WIDE):
    nodeRow = []
    for y in range(0, NUM_NODES_HIGH):
    	nodeRow.append((x * (WIDTH / (NUM_NODES_WIDE - 1)), y * (HEIGHT / (NUM_NODES_HIGH - 1))))

    nodeList.append(nodeRow)

for x in range(0, NUM_NODES_WIDE - 1):
    for y in range(0, NUM_NODES_HIGH - 1):
        polyColourDict[tuple(sorted([(x, y), (x, y + 1), (x + 1, y + 1)], key=lambda x: (x[0], x[1])))] = calculatePolyColour([nodeList[x][y], nodeList[x][y + 1], nodeList[x + 1][y + 1]], pix)
        polyColourDict[tuple(sorted([(x, y), (x + 1, y), (x + 1, y + 1)], key=lambda x: (x[0], x[1])))] = calculatePolyColour([nodeList[x][y], nodeList[x + 1][y], nodeList[x + 1][y + 1]], pix)

count = 0
for i in range(0, 10):
    count = 0
    print i
    xList = range(1, NUM_NODES_WIDE - 1)
    random.shuffle(xList)
    yList = range(1, NUM_NODES_HIGH - 1)
    random.shuffle(yList)
    for x in xList:
        print count
        count += 1
        for y in yList:
            moveNode(x, y, nodeList, polyColourDict, pix)

    img = Image.new('RGB', (WIDTH, HEIGHT))
    drw = ImageDraw.Draw(img, "RGBA")

    drawNodeList(nodeList, polyColourDict, drw)

    img.save("out" + str(i) + ".png")

