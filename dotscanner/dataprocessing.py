import matplotlib
import numpy as np
from PIL import Image

# Note: Coordinates are usually stored in hashmaps mapping a y to a set of corresponding x's
# e.g., the coordinates (y1, x1) and (y1, x2) would be the following key-value pair:
# {y1 : {x1, x2}}

def addCoordinate(y, x, coordMap):
	if y not in coordMap:
		coordMap[y] = set()
	coordMap[y].add(x)

def cleanDotCoords(data, dotCoords, blobCoords, blobSize, dotSize):
	removeDotsNearBlobs(dotCoords, blobCoords, blobSize)
	removeDimmerOverlappingDots(dotCoords, data, dotSize)

def coordExists(y, x, coordMap):
	return y in coordMap and x in coordMap[y]

def coordExistsWithinRadius(y, x, coordMap, radius):
	yRange = range(y - radius, y + radius + 1)
	xRange = range(x - radius, x + radius + 1)
	for currentY in yRange:
		if currentY in coordMap:
			for currentX in xRange:
				if currentX in coordMap[currentY]:
					return True
	return False

def findIndexOfMaxElement(array):
	maxIndex = 0
	maxElement = float("-inf")
	for index, element in enumerate(array):
		if element > maxElement:
			maxElement = element
			maxIndex = index
	return maxIndex

def getCoordPairsFromCoordMap(coordMap):
	coordList = []
	for y, xSet in coordMap.items():
		for x in xSet:
			coordList.append([x, y]) # For use with set_offsets(), which expects (x, y) coords
	return coordList

def getCoords(data, sums, thresholds, dotSize):
	dotCoords = {}
	blobCoords = {}
	lowerDotThreshScale, upperDotThreshScale, lowerBlobThreshScale = thresholds
	lowerDotThresh = lowerDotThreshScale * np.std(sums)
	upperDotThresh = upperDotThreshScale * np.std(sums)
	lowerBlobThresh = lowerBlobThreshScale * upperDotThresh
	
	for y in range(len(sums)):
		for x in range(len(sums[0])):
			if sums[y][x] > lowerDotThresh:
				if sums[y][x] < upperDotThresh:
					addCoordinate(y, x, dotCoords)
				else:
					if squareSum(data, y, x, 3) > lowerBlobThresh:
						addCoordinate(y, x, blobCoords)
					else:
						addCoordinate(y, x, dotCoords)
							
	return dotCoords, blobCoords

def getCoordsInPolygon(data, points, polygonVertices):
	path = matplotlib.path.Path(polygonVertices)
	flattenedMask = path.contains_points(points)
	mask = flattenedMask.reshape(len(data), len(data[0]))
	coordsInPolygon = np.argwhere(mask)
	return coordsInPolygon

def getCoordMapsWithinPolygon(data, sums, lowerDotThresh, upperDotThresh, lowerBlobThresh, dotSize, 
								polygonCoordMap, xMin, xMax, yMin, yMax):
	dotCoords = {}
	blobCoords = {}
	for y in range(yMin, yMax + 1):
		if y in polygonCoordMap:
			for x in range(xMin, xMax + 1):
				if x in polygonCoordMap[y]:
					if sums[y][x] > lowerDotThresh:
						if sums[y][x] < upperDotThresh:
							addCoordinate(y, x, dotCoords)
						else:
							if squareSum(data, y, x, 3) > lowerBlobThresh:
								addCoordinate(y, x, blobCoords)
							else:
								addCoordinate(y, x, dotCoords)
	return dotCoords, blobCoords

def getData(directory, filename):
	image = Image.open(directory + filename)
	data = np.array(image)
	subtractedData = data - np.median(image)
	return subtractedData

def getFullDataSquareSum(data):
	sums = np.zeros_like(data)

	sums[:len(data)-1, :len(data[0]) - 1] += data[1:,             1:               ]
	sums[:len(data)-1, :                ] += data[1:,             :                ]
	sums[:len(data)-1, 1:               ] += data[1:,             :len(data[0]) - 1]

	sums[:,            :len(data[0]) - 1] += data[:,              1:               ]
	sums                                  += data
	sums[:,            1:               ] += data[:,              :len(data[0]) - 1]

	sums[1:,           :len(data[0]) - 1] += data[:len(data) - 1, 1:               ]
	sums[1:,           :                ] += data[:len(data) - 1, :                ]
	sums[1:,           1:               ] += data[:len(data) - 1, :len(data[0]) - 1]
	
	return sums

def getInPolygonCoordMap(microscopeImage):
	data = microscopeImage.data
	points = []
	for y in range(len(data)):
		for x in range(len(data[0])):
			points.append((y, x))

	path = matplotlib.path.Path(microscopeImage.polygon)
	flattenedMask = path.contains_points(points)
	mask = flattenedMask.reshape(len(data), len(data[0]))
	coordsInPolygon = np.argwhere(mask)
	
	polygonCoordMap = {}
	for coordPair in coordsInPolygon:
		y, x = coordPair
		addCoordinate(y, x, polygonCoordMap)
	
	return polygonCoordMap

def getNeighborCoords(y, x, coordMap, dotSize):
	neighborCoords = []
	yRange = range(y - dotSize, y + dotSize + 1)
	xRange = range(x - dotSize, x + dotSize + 1)
	for currentY in yRange:
		if currentY in coordMap:
			for currentX in xRange:
				if currentX in coordMap[currentY]:
					neighborCoords.append((currentY, currentX))
	return neighborCoords

def getNeighborData(neighborCoords, data):
	neighborData = []
	for coordPair in neighborCoords:
		y, x = coordPair
		neighborData.append(data[y][x])
	return neighborData

def getPolygonLimits(polygon):
	polygonXMin, polygonXMax = float("inf"), float("-inf")
	polygonYMin, polygonYMax = float("inf"), float("-inf")
	
	for coordPair in polygon:
		y, x = coordPair
		polygonYMin = min(y, polygonYMin)
		polygonYMax = max(y, polygonYMax)
		polygonXMin = min(x, polygonXMin)
		polygonXMax = max(x, polygonXMax)
	
	polygonYMin = int(round(polygonYMin, 0))
	polygonYMax = int(round(polygonYMax, 0))
	polygonXMin = int(round(polygonXMin, 0))
	polygonXMax = int(round(polygonXMax, 0))
	
	return polygonXMin, polygonXMax, polygonYMin, polygonYMax

def getSortedCoordPairsFromCoordMap(coordMap, data):
	coordList = []
	dataList = []
	for y, xSet in coordMap.items():
		for x in xSet:
			coordList.append([x, y]) # For use with set_offsets(), which expects (x, y) coords
			dataList.append(data[y][x])
	zippedLists = zip(dataList, coordList)
	sortedCoordList = [x for _, x in sorted(zippedLists)]
	return sortedCoordList[::-1]

def getThresholds(microscopeImage):
	sums = microscopeImage.sums
	lowerDotThreshScale, upperDotThreshScale, lowerBlobThreshScale = microscopeImage.thresholds
	lowerDotThresh = lowerDotThreshScale * np.std(sums)
	upperDotThresh = upperDotThreshScale * np.std(sums)
	lowerBlobThresh = lowerBlobThreshScale * upperDotThresh
	return lowerDotThresh, upperDotThresh, lowerBlobThresh

def getYAndXFromCoordList(coordList):
	yList = []
	xList = []
	for coordPair in coordList:
		y, x = coordPair
		yList.append(y)
		xList.append(x)
	return yList, xList

def removeAllButBrightestCoords(neighborCoords, indexOfBrightestSum, dotCoords):
	for index, coordPair in enumerate(neighborCoords):
		if index == indexOfBrightestSum:
			continue
		y, x = coordPair
		removeCoordinate(y, x, dotCoords)

def removeCoordinate(y, x, coordMap):
	if len(coordMap[y]) == 1:
		del coordMap[y]
	else:
		coordMap[y].remove(x)

def removeDimmerOverlappingDots(dotCoords, data, dotSize):
	coordPairs = getCoordPairsFromCoordMap(dotCoords) # Returns (x, y), not (y, x)
	# coordPairs = getSortedCoordPairsFromCoordMap(dotCoords, data) # Returns (x, y), not (y, x)
	for coordPair in coordPairs:
		x, y = coordPair
		neighborCoords = getNeighborCoords(y, x, dotCoords, dotSize)
		if len(neighborCoords) > 1:
			neighborData = getNeighborData(neighborCoords, data)
			indexOfBrightestNeighbor = findIndexOfMaxElement(neighborData)
			removeAllButBrightestCoords(neighborCoords, indexOfBrightestNeighbor, dotCoords)

def removeDotsNearBlobs(dotCoords, blobCoords, blobSize):
	coordPairs = getCoordPairsFromCoordMap(dotCoords) # Returns (x, y), not (y, x)
	for coordPair in coordPairs:
		x, y = coordPair
		if coordExistsWithinRadius(y, x, blobCoords, blobSize):
			removeCoordinate(y, x, dotCoords)

def setScatterData(dotCoords, blobCoords, dotScatter, blobScatter):
	setScatterOffset(dotCoords, dotScatter)
	setScatterOffset(blobCoords, blobScatter)

def setScatterOffset(coordMap, scatterPlot):
	coordList = getCoordPairsFromCoordMap(coordMap)
	if len(coordList):
		scatterPlot.set_offsets(coordList)

def squareSum(data, y, x, pixelRadius):
	total = 0 
	for yValue in range(y - pixelRadius, y + pixelRadius + 1):
		for xValue in range(x - pixelRadius, x + pixelRadius + 1):
			if yValue < 0 or yValue >= len(data) or xValue < 0 or xValue >= len(data[0]):
				continue
			total += data[yValue, xValue]
	return total
