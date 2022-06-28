import numpy as np
from PIL import Image

def addCoordinate(y, x, coordMap):
	if y not in coordMap:
		coordMap[y] = set()
	coordMap[y].add(x)

def cleanDotCoords(sums, dotCoords, blobCoords, blobSize, dotSize):
	removeDotsNearBlobs(dotCoords, blobCoords, blobSize)
	removeDimmerOverlappingDots(dotCoords, sums, dotSize)

def coordExists(y, x, coordMap):
	if y in coordMap:
		if x in coordMap[y]:
			return True
	return False

def coordExistsWithinRadius(y, x, coordMap, radius):
	yRange = range(y - radius, y + radius + 1)
	xRange = range(x - radius, x + radius + 1)
	for currentY in yRange:
		if currentY in coordMap:
			for currentX in xRange:
				if currentX in coordMap[currentY]:
					return True
	return False

def coordIsNearBlob(y, x, blobCoords, blobSize):
	yRange = range(y - blobSize, y + blobSize + 1)
	xRange = range(x - blobSize, x + blobSize + 1)
	for currentY in yRange:
		if currentY in blobCoords:
			for currentX in xRange:
				if currentX in blobCoords[currentY]:
					return True
	return False

def coordIsNearDot(y, x, dotCoords, dotSize):
	yRange = range(y - dotSize, y + dotSize + 1)
	xRange = range(x - dotSize, x + dotSize + 1)
	for currentY in yRange:
		if currentY in dotCoords:
			for currentX in xRange:
				if currentX in dotCoords[currentY]:
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
	# Hashmaps mapping each y coordinate to a set of corresponding x coordinates
	# e.g., the coordinates (y1, x1) and (y1, x2) would be the following key-value pair:
	# {y1 : {x1, x2}}
	lowerDotThreshScale, upperDotThreshScale, lowerBlobThreshScale = thresholds
	lowerDotThresh = lowerDotThreshScale * np.std(sums)
	upperDotThresh = upperDotThreshScale * np.std(sums)
	lowerBlobThresh = lowerBlobThreshScale * upperDotThresh
	
	for y in range(len(sums)):
		for x in range(len(sums[0])):
			if sums[y, x] > lowerDotThresh:
				if sums[y, x] < upperDotThresh:
					addCoordinate(y, x, dotCoords)
				else:
					if squareSum(data, y, x, dotSize + 1) > lowerBlobThresh:
						addCoordinate(y, x, blobCoords)
					else:
						addCoordinate(y, x, dotCoords)
							
	return dotCoords, blobCoords

def getCoordsOfNeighbors(y, x, coordMap, dotSize):
	neighborCoords = []
	yRange = range(y - dotSize, y + dotSize + 1)
	xRange = range(x - dotSize, x + dotSize + 1)
	for currentY in yRange:
		if currentY in coordMap:
			for currentX in xRange:
				if currentX in coordMap[currentY]:
					neighborCoords.append((currentY, currentX))
	return neighborCoords

def getData(directory, filename):
	image = Image.open(directory + filename)
	data = np.array(image)
	subtractedData = data - np.mean(image)
	return subtractedData

def getFullDataSquareSum(data):
	sums = np.zeros_like(data)

	sums[:len(sums)-1, :len(sums[0]) - 1] += data[1:,                1:               ]
	sums[:len(sums)-1, :                ] += data[1:,                :                ]
	sums[:len(sums)-1, 1:               ] += data[1:,                :len(data[0]) - 1]

	sums[:,            :len(sums[0]) - 1] += data[:,                 1:               ]
	sums                                  += data
	sums[:,            1:               ] += data[:,                 :len(data[0]) - 1]

	sums[1:,           :len(sums[0]) - 1] += data[:len(data[0]) - 1, 1:               ]
	sums[1:,           :                ] += data[:len(data[0]) - 1, :                ]
	sums[1:,           1:               ] += data[:len(data[0]) - 1, :len(data[0]) - 1]

	return sums

def getSumsOfNeighbors(neighborCoords, sums):
	neighborSums = []
	for coordPair in neighborCoords:
		y, x = coordPair
		neighborSums.append(sums[y][x])
	return neighborSums

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

def removeDimmerOverlappingDots(dotCoords, sums, dotSize):
	coordPairs = getCoordPairsFromCoordMap(dotCoords) # Returns (x, y), not (y, x)
	for coordPair in coordPairs:
		x, y = coordPair
		neighborCoords = getCoordsOfNeighbors(y, x, dotCoords, dotSize)
		if len(neighborCoords) > 1:
			neighborSums = getSumsOfNeighbors(neighborCoords, sums)
			indexOfBrightestSum = findIndexOfMaxElement(neighborSums)
			removeAllButBrightestCoords(neighborCoords, indexOfBrightestSum, dotCoords)

def removeDotsNearBlobs(dotCoords, blobCoords, blobSize):
	coordPairs = getCoordPairsFromCoordMap(dotCoords) # Returns (x, y), not (y, x)
	for coordPair in coordPairs:
		x, y = coordPair
		if coordIsNearBlob(y, x, blobCoords, blobSize):
			removeCoordinate(y, x, dotCoords)

def setScatterData(dotCoords, blobCoords, dotScatter, blobScatter):
	setScatterOffset(dotCoords, dotScatter)
	setScatterOffset(blobCoords, blobScatter)

def setScatterOffset(coordMap, scatterPlot):
	coordList = getCoordPairsFromCoordMap(coordMap)
	scatterPlot.set_offsets(coordList)

def squareSum(data, y, x, pixelRadius):
	total = 0 
	for yValue in range(y - pixelRadius, y + pixelRadius + 1):
		for xValue in range(x - pixelRadius, x + pixelRadius + 1):
			if yValue < 0 or yValue >= len(data) or xValue < 0 or xValue >= len(data[0]):
				continue
			total += data[yValue, xValue]
	return total
