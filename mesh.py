from PIL import Image, ImageDraw
import random

NUM_NODES_WIDE = 128
NUM_NODES_HIGH = 72
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

def calculatePolyColour(nodes, pix):
    maxX = 0
    maxY = 0
    minX = WIDTH
    minY = HEIGHT
    
    redAverage = 0
    blueAverage = 0
    greenAverage = 0

    numPixels = 0
    
    for node in nodes:
        if node[0] > maxX:
            maxX = node[0]
        if node[0] < minX:
            minX = node[0]

        if node[1] > maxY:
            maxY = node[1]
        if node[1] < minY:
            minY = node[1]

    #print(str(maxX) + " " + str(minX) + " " + str(maxY) + " " + str(minY) + "\n")

    for x in range(minX, maxX):
        for y in range(minY, maxY):
            if pixelInPolygon(nodes, [x, y]):
                redAverage += pix[x, y][0]
                blueAverage += pix[x, y][1]
                greenAverage += pix[x, y][2]
                numPixels += 1

    redAverage /= numPixels
    blueAverage /= numPixels
    greenAverage /= numPixels

    return (redAverage, blueAverage, greenAverage)

#########################################################################################
##          Main start
#########################################################################################

targetImage = Image.open("test.jpg")
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
        
img = Image.new('RGB', (WIDTH, HEIGHT))
drw = ImageDraw.Draw(img, "RGBA")

drawNodeList(nodeList, polyColourDict, drw)

img.save("out.png")

